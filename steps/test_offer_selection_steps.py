import random

from pytest_bdd import given, scenarios, then, when
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.billing_account_delete_page import BillingAccountDeletePage
from pages.create_customer_page import CreateCustomerPage
from pages.offer_selection_page import OfferSelectionPage
from utils import config

scenarios("offer_selection.feature")


def _create_fresh_customer(driver):
    driver.get(config.url("/customers/new"))
    create_page = CreateCustomerPage(driver)
    create_page.fill_demographic_step_with_faker(gender="Erkek")
    create_page.click_demographic_next()
    create_page.wait_for_address_step()
    create_page.add_address_with_faker()
    create_page.wait_for_address_saved()
    create_page.click_address_next()
    create_page.wait_for_contact_step()
    create_page.fill_contact_step_with_faker()
    create_page.click_submit()
    create_page.wait_for_navigated_to_customer_info()
    return BillingAccountDeletePage(driver)


def _create_fresh_customer_and_open_account_tab(driver):
    return _create_fresh_customer(driver)


def _open_offer_selection_screen(driver):
    account_page = _create_fresh_customer_and_open_account_tab(driver)
    account_page.create_account_and_wait()
    account_page.click_new_sale_on_row()
    return OfferSelectionPage(driver)


def _fill_config_fields_and_proceed_to_summary(driver):
    # SalesSetupPage'deki AYNI konfigürasyon doldurma mantığı - burada
    # BİLEREK tekrarlanıyor, çünkü SalesSetupPage.purchase_simple_offer()
    # hem teklif SEÇİMİNİ (bu senaryoda Given adımında ZATEN yapılmış)
    # hem de NİHAİ gönderimi (bu senaryo göndermeden ÖNCEKİ Sipariş
    # Özeti ekranını doğrulamak istiyor) tek bir akışta yapıyor - o
    # metodu burada çağırmak teklifi İKİNCİ KEZ seçmeye çalışır ve
    # nihai gönderimi de istemeden tetikler (KISS: zorla yeniden
    # kullanmak yerine küçük, kendine özgü bir adım tekrarı tercih
    # edildi).
    fields = driver.find_elements(By.CSS_SELECTOR, "[data-testid='sales-config-field']")
    for index, field in enumerate(fields):
        value = "5" + "".join(random.choices("0123456789", k=9)) if index == 0 else "".join(random.choices("0123456789", k=6))
        field.send_keys(value)
    next_btn = driver.find_element(By.CSS_SELECTOR, "[data-testid='sales-config-next']")
    WebDriverWait(driver, 10).until(lambda d: next_btn.is_enabled())
    next_btn.click()
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='sales-summary-line']")))


@given("kullanıcı bir fatura hesabının Müşteri Hesabı ekranındadır", target_fixture="account_page")
def user_on_account_screen(authenticated_driver):
    account_page = _create_fresh_customer_and_open_account_tab(authenticated_driver)
    account_page.create_account_and_wait()
    return account_page


@when('kullanıcı "Yeni Satış Başlat" butonuna tıklar', target_fixture="offer_page")
def click_new_sale_button(driver, account_page):
    account_page.click_new_sale_on_row()
    return OfferSelectionPage(driver)


@then('sistem "Teklif Seçimi" başlıklı ekrana yönlendirir ve varsayılan katalog listesini gösterir')
def offer_selection_screen_shown_with_default_catalog(offer_page):
    assert offer_page.is_catalog_tab_active_with_offers()


@given("kullanıcı Teklif Seçimi ekranındadır", target_fixture="offer_page")
def user_on_offer_selection_screen(authenticated_driver):
    return _open_offer_selection_screen(authenticated_driver)


@when('kullanıcı katalog dropdown\'ından "Mobil" seçeneğini seçer')
def select_mobil_category(offer_page):
    offer_page.select_catalog_category("Mobil")


@then("yalnızca Mobil kategorisindeki teklifler listelenir")
def only_mobil_offers_listed(offer_page):
    names = offer_page.get_offer_names()
    assert names
    assert all("Mobil" in name for name in names)


@when("Teklif Adı filtresine bir değer girilip Ara'ya tıklanır", target_fixture="search_context")
def search_by_name_value(offer_page):
    search_value = "Mobil 20GB"
    offer_page.search_by_name(search_value)
    return offer_page, search_value


@then("yalnızca eşleşen teklifler listelenir")
def only_matching_offers_listed(search_context):
    offer_page, search_value = search_context
    names = offer_page.get_offer_names()
    assert names
    assert all(search_value.lower() in name.lower() for name in names)


@when("var olmayan bir Teklif Adı ile arama yapılır")
def search_nonexistent_name(offer_page):
    offer_page.search_by_name("ZZZ-YOK-URUN-999")


@when("Teklif ID filtresine harf girilip Ara'ya tıklanır")
def search_by_letters_in_id_filter(offer_page):
    offer_page.search_by_id("abc")


@then("sonuç bulunamadı durumu görüntülenir")
def no_results_state_shown(offer_page):
    assert offer_page.get_offer_row_count() == 0


@given("kullanıcı bir teklif satırı seçmiştir", target_fixture="offer_selection_context")
def user_selected_an_offer_row(authenticated_driver):
    offer_page = _open_offer_selection_screen(authenticated_driver)
    selected_name = offer_page.get_offer_names()[0]
    price = offer_page.get_offer_price_value_by_name(selected_name)
    offer_page.select_offer_by_name(selected_name)
    return offer_page, selected_name, price


@when('"Sepete Ekle" butonuna tıklanır')
def click_add_to_cart(offer_selection_context):
    offer_page, _, _ = offer_selection_context
    offer_page.click_add_to_cart_and_wait()


@then("teklif sepette listelenir")
def offer_listed_in_cart(offer_selection_context):
    offer_page, selected_name, _ = offer_selection_context
    assert selected_name in offer_page.get_cart_line_names()


@then("toplam tutar teklifin fiyatı kadar artar")
def total_increases_by_offer_price(offer_selection_context):
    offer_page, _, price = offer_selection_context
    assert offer_page.get_cart_total_value() == price


@given('kullanıcı sepete "Ev İnterneti Fiber 100" teklifini YALNIZCA BİR KEZ eklemiştir', target_fixture="offer_page")
def offer_added_exactly_once(authenticated_driver):
    offer_page = _open_offer_selection_screen(authenticated_driver)
    offer_page.select_offer_by_name("Ev İnterneti Fiber 100")
    offer_page.click_add_to_cart_and_wait()
    return offer_page


@when("kullanıcı İleri ile Ürün Konfigürasyonu ve Sipariş Özeti ekranlarına ilerler")
def proceed_through_config_to_summary(driver, offer_page):
    offer_page.click_next_and_wait_for_config()
    _fill_config_fields_and_proceed_to_summary(driver)


@then("sipariş özetinde bu teklif TAM 1 KEZ görüntülenmeli, toplam tutar 299.90 TL olmalıdır")
def offer_appears_exactly_once_in_summary(driver):
    lines = driver.find_elements(By.CSS_SELECTOR, "[data-testid='sales-summary-line']")
    assert len(lines) == 1
    total_text = driver.find_element(By.CSS_SELECTOR, "[data-testid='sales-summary-total']").text
    total_value = float(total_text.replace("TL", "").replace(",", "").strip())
    assert total_value == 299.90


@given("sepette en az bir teklif vardır", target_fixture="offer_page")
def cart_has_at_least_one_offer(authenticated_driver):
    offer_page = _open_offer_selection_screen(authenticated_driver)
    offer_page.select_offer_by_name(offer_page.get_offer_names()[0])
    offer_page.click_add_to_cart_and_wait()
    return offer_page


@when('"Temizle" butonuna tıklanır')
def click_clear_cart(offer_page):
    offer_page.click_clear_cart_and_wait()


@then('sepet boşalır, toplam "0.00 TL" olur')
def cart_emptied_and_total_zero(offer_page):
    assert offer_page.is_cart_empty()
    assert offer_page.get_cart_total_value() == 0.0


@given("sepet boştur", target_fixture="offer_page")
def cart_is_empty(authenticated_driver):
    return _open_offer_selection_screen(authenticated_driver)


@then('"İleri" butonu pasif durumdadır')
def next_button_disabled(offer_page):
    assert not offer_page.is_next_button_enabled()


@when('"Kampanya" sekmesine geçilir')
def switch_to_campaign_tab_step(offer_page):
    offer_page.switch_to_campaign_tab()


@then("kampanya bazlı teklifler katalogdan ayrı bir liste olarak görüntülenir")
def campaign_offers_shown_separately(offer_page):
    assert len(offer_page.get_campaign_rows()) > 0


@given("sepette (Basket) en az bir ürün vardır", target_fixture="duplicate_add_context")
def cart_has_one_product_for_duplicate_test(authenticated_driver):
    offer_page = _open_offer_selection_screen(authenticated_driver)
    name = offer_page.get_offer_names()[0]
    offer_page.select_offer_by_name(name)
    offer_page.click_add_to_cart_and_wait()
    before_names = offer_page.get_cart_line_names()
    before_total = offer_page.get_cart_total_value()
    return offer_page, name, before_names, before_total


@when('kullanıcı aynı ürünü tekrar "Sepete Ekle" ile eklemeyi dener')
def attempt_duplicate_add(duplicate_add_context):
    # Kasıtlı kırmızı (TC-014-13, canlı doğrulandı): mükerrer ekleme ŞU AN
    # engellenmiyor - bu adım "değişiklik olmamalı" beklentisiyle KÖR bir
    # sleep KULLANMIYOR, bunun yerine olası (buggy) bir satır artışını
    # KISA bir üst sınırla dinamik olarak bekliyor; artış GERÇEKLEŞMEZSE
    # (doğru davranışta olması gerektiği gibi) TimeoutException güvenle
    # yutuluyor - "değişmedi" sonucunu Then adımı ayrıca doğruluyor.
    offer_page, name, _, _ = duplicate_add_context
    offer_page.select_offer_by_name(name)
    before_count = offer_page.get_cart_line_count()
    offer_page.wait.until(EC.element_to_be_clickable(offer_page.ADD_TO_CART)).click()
    try:
        WebDriverWait(offer_page.driver, 3).until(lambda d: offer_page.get_cart_line_count() > before_count)
    except TimeoutException:
        pass


@then("sepete mükerrer bir kayıt eklenmez")
def no_duplicate_added(duplicate_add_context):
    offer_page, _, before_names, _ = duplicate_add_context
    assert offer_page.get_cart_line_names() == before_names


@then("Basket içeriği ve Total Amount değişmeden kalır")
def basket_and_total_unchanged(duplicate_add_context):
    offer_page, _, before_names, before_total = duplicate_add_context
    assert offer_page.get_cart_line_names() == before_names
    assert offer_page.get_cart_total_value() == before_total


@given("kullanıcı Campaign sekmesindedir", target_fixture="offer_page")
def user_on_campaign_tab(authenticated_driver):
    offer_page = _open_offer_selection_screen(authenticated_driver)
    offer_page.switch_to_campaign_tab()
    return offer_page


@when('bir kampanya seçilip "Sepete Ekle" ile eklenir', target_fixture="campaign_context")
def select_campaign_and_add_to_cart(offer_page):
    expected_price = offer_page.get_campaign_row_price_value(0)
    offer_page.select_campaign_by_index(0)
    offer_page.click_add_to_cart_and_wait()
    return offer_page, expected_price


@then("kampanya sepete eklenir")
def campaign_added_to_cart(campaign_context):
    offer_page, _ = campaign_context
    assert offer_page.get_cart_line_count() >= 1


@then("Total Amount kampanyanın indirimli fiyatını yansıtır")
def total_reflects_campaign_price(campaign_context):
    offer_page, expected_price = campaign_context
    assert offer_page.get_cart_total_value() == expected_price
