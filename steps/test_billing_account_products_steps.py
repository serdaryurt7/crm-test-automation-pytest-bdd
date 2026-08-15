from pytest_bdd import given, scenarios, then, when
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.billing_account_products_page import BillingAccountProductsPage
from pages.create_customer_page import CreateCustomerPage
from pages.sales_setup_page import SalesSetupPage
from utils import config

scenarios("billing_account_products.feature")


def _create_fresh_customer(driver):
    # Zaten authenticated bir session varsayar, login YAPMAZ - 2. bir
    # disposable müşteri gerektiğinde auth guard /login'e yönlendirmesin
    # diye (projedeki diğer *_delete/*_products steps ile tutarlı).
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
    return BillingAccountProductsPage(driver)


def _create_fresh_customer_and_open_account_tab(driver):
    return _create_fresh_customer(driver)


def _purchase_offers_and_wait_for_products(driver, customer_url, account_page, offer_names):
    # Canlı doğrulandı (UC-013 keşfi): satış akışı "Sipariş oluşturuldu!"
    # ile BAŞARIYLA tamamlansa bile ürün hesabın panelinde ARA SIRA hiç
    # yansımıyor (ortam/zaman kaynaklı - UC-012/TC-012-03'te belgelenen
    # AYNI tutarsızlık deseni). Bu yüzden her teklif için, panelde
    # BEKLENEN sayıya GERÇEKTEN ulaşıldığı dinamik olarak doğrulanana
    # kadar (sabit, küçük bir üst sınırla) satın alma tekrarlanıyor -
    # sadece "satır var mı" değil, "satır sayısı ARTTI mı" kontrol
    # edilerek önceki bir satının satırını yanlışlıkla "yeni satın alma
    # başarılı" sanmanın önüne geçiliyor.
    panel_id = account_page.get_products_panel_id()
    expected_count = account_page.get_product_row_count(panel_id)
    for offer_name in offer_names:
        expected_count += 1
        succeeded = False
        for _ in range(4):
            account_page.click_new_sale_on_row()
            sales_page = SalesSetupPage(driver)
            try:
                sales_page.purchase_simple_offer(offer_name_contains=offer_name)
            except TimeoutException:
                pass
            driver.get(customer_url)
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='customer-detail-header']"))
            )
            account_page = BillingAccountProductsPage(driver)
            panel_id = account_page.get_products_panel_id()
            if account_page.wait_for_product_row_count_at_least(panel_id, expected_count):
                succeeded = True
                break
        assert succeeded, (
            f"'{offer_name}' teklifi {expected_count}. ürün olarak hesaba yansımadı "
            "(ortam kaynaklı tutarsızlık - 4 denemede de başarısız)."
        )
    return account_page, panel_id


def _setup_account_with_products(driver, offer_names):
    account_page = _create_fresh_customer_and_open_account_tab(driver)
    customer_url = driver.current_url
    account_page.create_account_and_wait()
    return _purchase_offers_and_wait_for_products(driver, customer_url, account_page, offer_names)


@given("kullanıcı bir fatura hesabı altındaki ürün listesini görüntülemektedir", target_fixture="products_context")
def user_viewing_product_list(authenticated_driver):
    return _setup_account_with_products(authenticated_driver, ["Mobil 20GB Paket"])


@when("kullanıcı bir ürünün View butonuna tıklar")
def click_view_button(products_context):
    account_page, panel_id = products_context
    account_page.click_preview_on_row(panel_id)


@then("panel Ürün Teklif ID/Adı/Spec ID ve karakteristiklerini salt okunur şekilde gösterir")
def preview_shows_readonly_offer_fields(products_context):
    account_page, _ = products_context
    assert account_page.is_preview_displayed_readonly_with_offer_fields()


@given("hesap altındaki bir ürün kampanyasız alınmıştır", target_fixture="products_context")
def account_product_without_campaign(authenticated_driver):
    return _setup_account_with_products(authenticated_driver, ["Mobil 20GB Paket"])


@when("ürün listesi görüntülenir")
def product_list_displayed(products_context):
    # Given adımı zaten ürün listesini görüntüler durumda bırakıyor -
    # bu adımda ek bir aksiyon gerekmiyor, sadece durum doğrulanıyor.
    pass


@then('kampanya alanları "—" olarak görüntülenir')
def campaign_fields_show_placeholder(products_context):
    account_page, panel_id = products_context
    assert account_page.has_no_campaign_fields_displayed(panel_id)


@given("kullanıcı ürün detay tablosunu görüntülemektedir", target_fixture="products_context")
def user_viewing_product_detail_table(authenticated_driver):
    return _setup_account_with_products(authenticated_driver, ["Mobil 20GB Paket"])


@then("her kayıt için bir Delete ikonu görüntülenir")
def each_record_has_delete_icon(products_context):
    account_page, panel_id = products_context
    assert account_page.each_row_has_delete_icon(panel_id)


@when("kullanıcı bir ürünün Delete ikonuna tıklar")
def click_delete_icon(products_context):
    account_page, panel_id = products_context
    account_page._pre_delete_count = account_page.get_product_row_count(panel_id)
    account_page._pre_delete_names = account_page.get_product_row_names(panel_id)
    account_page.attempt_delete_on_row(panel_id)


@then("herhangi bir işlem tetiklenmez, ürün verisi değişmeden kalır")
def delete_click_has_no_effect(products_context):
    account_page, panel_id = products_context
    assert account_page.is_delete_action_ineffective(
        panel_id, account_page._pre_delete_count, account_page._pre_delete_names
    )
    assert account_page.is_data_unchanged_after_reload(panel_id, account_page._pre_delete_names)


@given("ürün önizleme paneli açıktır", target_fixture="products_context")
def preview_panel_open(authenticated_driver):
    account_page, panel_id = _setup_account_with_products(authenticated_driver, ["Mobil 20GB Paket"])
    account_page.click_preview_on_row(panel_id)
    return account_page, panel_id


@when("Close butonuna tıklanır")
def click_close_button(products_context):
    account_page, _ = products_context
    account_page.close_preview()


@then("panel kapanıp ürün listesi görünümüne dönülür")
def preview_closes_and_list_returns(products_context):
    account_page, panel_id = products_context
    assert account_page.is_preview_closed_and_list_visible(panel_id)


@given("bir hesap altında birden fazla ürün vardır", target_fixture="products_context")
def account_has_multiple_products(authenticated_driver):
    return _setup_account_with_products(authenticated_driver, ["Mobil 20GB Paket", "TV Başlangıç Paketi"])


@then("tüm ürünler aynı tabloda ayrı satırlar olarak eksiksiz listelenir")
def all_products_listed_completely(products_context):
    account_page, panel_id = products_context
    names = account_page.get_product_row_names(panel_id)
    assert len(names) >= 2
    assert all(bool(name) for name in names)


@given("seçilen fatura hesabına bağlı hiç ürün kaydı yoktur", target_fixture="products_context")
def account_without_products(authenticated_driver):
    account_page = _create_fresh_customer_and_open_account_tab(authenticated_driver)
    account_page.create_account_and_wait()
    panel_id = account_page.get_products_panel_id()
    return account_page, panel_id


@when("kullanıcı hesap satırını görüntüler")
def user_views_account_row(products_context):
    # Given adımı zaten hesap satırını görüntüler durumda - ek bir
    # aksiyon gerekmiyor, sadece durum doğrulanıyor.
    pass


@then("ürün detay tablosu görüntülenmez")
def product_table_not_displayed(products_context):
    account_page, panel_id = products_context
    assert not account_page.is_products_table_displayed(panel_id)
    assert account_page.is_empty_state_displayed()


@given("fatura hesabı satırı ve ürün detay tablosu görünür durumdadır", target_fixture="products_context")
def account_row_and_table_visible(authenticated_driver):
    account_page = _create_fresh_customer_and_open_account_tab(authenticated_driver)
    account_page.create_account_and_wait()
    panel_id = account_page.get_products_panel_id()
    return account_page, panel_id


@when("kullanıcı Collapse ikonuna tıklar")
def click_collapse_icon(products_context):
    account_page, panel_id = products_context
    account_page.click_toggle_and_wait_collapsed(panel_id)


@then("ürün detay tablosu gizlenir")
def product_table_hidden(products_context):
    account_page, panel_id = products_context
    assert account_page.is_panel_collapsed(panel_id)


@then("kullanıcı Expand ile tabloyu tekrar görüntüleyebilir")
def user_can_expand_table_again(products_context):
    account_page, panel_id = products_context
    account_page.click_toggle_and_wait_expanded(panel_id)
    assert not account_page.is_panel_collapsed(panel_id)


@given("fatura hesabı genişletilmiş ve bağlı ürünler listelenmiştir", target_fixture="products_context")
def account_expanded_with_products(authenticated_driver):
    return _setup_account_with_products(authenticated_driver, ["Mobil 20GB Paket", "TV Başlangıç Paketi"])


@then("tablodaki her kayıt için bir View ikonu görüntülenir")
def each_record_has_view_icon(products_context):
    account_page, panel_id = products_context
    assert account_page.each_row_has_preview_icon(panel_id)
