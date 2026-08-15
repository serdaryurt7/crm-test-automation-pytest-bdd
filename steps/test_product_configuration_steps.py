from faker import Faker
from pytest_bdd import given, scenarios, then, when
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.billing_account_delete_page import BillingAccountDeletePage
from pages.create_customer_page import CreateCustomerPage
from pages.offer_selection_page import OfferSelectionPage
from pages.product_configuration_page import ProductConfigurationPage
from utils import config

scenarios("product_configuration.feature")

fake = Faker("tr_TR")


def _create_fresh_customer_and_open_account_tab(driver, extra_addresses=0):
    driver.get(config.url("/customers/new"))
    create_page = CreateCustomerPage(driver)
    create_page.fill_demographic_step_with_faker(gender="Erkek")
    create_page.click_demographic_next()
    create_page.wait_for_address_step()
    create_page.add_address_with_faker()
    create_page.wait_for_address_saved()
    for _ in range(extra_addresses):
        create_page.add_address_with_faker()
        create_page.wait_for_address_saved()
    create_page.click_address_next()
    create_page.wait_for_contact_step()
    create_page.fill_contact_step_with_faker()
    create_page.click_submit()
    create_page.wait_for_navigated_to_customer_info()
    return BillingAccountDeletePage(driver)


def _open_config_screen_with_offers(driver, offer_names, extra_addresses=0):
    # "Mobil 20GB Paket" / "Superbox 50GB" gibi yalnızca <input> alanları
    # içeren (dropdown/select alanı OLMAYAN) basit şablonlu teklifler
    # kasıtlı seçiliyor - canlı doğrulandı (bkz. project_brain.txt UC-015
    # keşfi): "Ev İnterneti Fiber 1000" gibi tekliflerde ek bir <app-select>
    # bant genişliği alanı var, bu senaryoların kapsamı dışında (YAGNI).
    account_page = _create_fresh_customer_and_open_account_tab(driver, extra_addresses)
    account_page.create_account_and_wait()
    account_page.click_new_sale_on_row()
    offer_page = OfferSelectionPage(driver)
    for offer_name in offer_names:
        offer_page.select_offer_by_name(offer_name)
        offer_page.click_add_to_cart_and_wait()
    offer_page.click_next_and_wait_for_config()
    return ProductConfigurationPage(driver)


@given("kullanıcı sepete birden fazla teklif ekleyip İleri ile Ürün Konfigürasyonu ekranına geçmiştir", target_fixture="config_page")
def cart_has_multiple_offers_on_config_screen(authenticated_driver):
    return _open_config_screen_with_offers(authenticated_driver, ["Mobil 20GB Paket", "Superbox 50GB"])


@then("sepetteki her teklif için ayrı bir konfigürasyon kartı (Ürün Teklif ID/Adı ile) görüntülenir")
def each_cart_offer_has_own_config_card(config_page):
    names = config_page.get_config_card_offer_names()
    assert config_page.get_config_card_count() == 2
    assert "Mobil 20GB Paket" in names
    assert "Superbox 50GB" in names


@given("kullanıcı Ürün Konfigürasyonu ekranındadır", target_fixture="config_page")
def user_on_product_configuration_screen(authenticated_driver):
    return _open_config_screen_with_offers(authenticated_driver, ["Mobil 20GB Paket"])


@when("zorunlu konfigürasyon alanları boş bırakılır")
def required_fields_left_empty(config_page):
    # Given adımı zaten alanları BOŞ bırakıyor - ek bir aksiyon gerekmiyor.
    pass


@then("İleri butonu pasif kalır")
def next_button_stays_disabled(config_page):
    assert not config_page.is_next_button_enabled()


@given("kullanıcının birden fazla kayıtlı adresi olduğu Ürün Konfigürasyonu ekranındadır", target_fixture="config_page")
def user_on_config_screen_with_multiple_addresses(authenticated_driver):
    return _open_config_screen_with_offers(authenticated_driver, ["Mobil 20GB Paket"], extra_addresses=1)


@when("müşterinin kayıtlı adreslerinden biri hizmet adresi olarak seçilir")
def select_one_of_registered_addresses(config_page):
    config_page.select_address_by_index(1)


@then("seçim işaretli olarak görüntülenir")
def selection_is_marked(config_page):
    states = config_page.get_address_selection_states()
    assert states[1] is True
    assert states.count(True) == 1


@when('"Yeni Adres Ekle" ile yeni bir hizmet adresi eklenir')
def add_new_service_address(config_page):
    config_page.add_new_service_address(fake.street_name(), fake.building_number(), fake.sentence(nb_words=4))


@then("yeni adres seçili olarak listeye eklenir")
def new_address_added_and_selected(config_page):
    assert config_page.is_newest_address_added_and_selected()


@given("kullanıcı Ürün Konfigürasyonu ekranında konfigürasyon alanlarını doldurmuştur", target_fixture="config_page")
def user_filled_config_fields(authenticated_driver):
    config_page = _open_config_screen_with_offers(authenticated_driver, ["Mobil 20GB Paket"])
    config_page.fill_all_required_text_fields_with_dummy_values()
    return config_page


@when('"Geri" butonuna tıklanır')
def click_back_button(config_page):
    config_page.click_back_and_wait_for_offer_selection()


@then("Teklif Seçimi ekranına dönülür ve sepet korunur")
def returned_to_offer_selection_cart_preserved(driver, config_page):
    offer_page = OfferSelectionPage(driver)
    assert offer_page.get_cart_line_count() == 1


@when("kullanıcı tekrar İleri butonuna tıklar")
def click_next_again(driver):
    driver.find_element(By.CSS_SELECTOR, "[data-testid='sales-offer-next']").click()
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='sales-config-field']")))


@then("daha önce girilmiş teknik konfigürasyon değerleri korunmuş olarak görüntülenir")
def previously_entered_values_preserved(driver):
    fields = driver.find_elements(By.CSS_SELECTOR, "[data-testid='sales-config-field']")
    values = [f.get_attribute("value") for f in fields if f.tag_name == "input"]
    assert values
    assert all(bool(v) for v in values)


@given("tüm zorunlu konfigürasyon alanları doldurulmuştur", target_fixture="config_page")
def all_required_config_fields_filled(authenticated_driver):
    config_page = _open_config_screen_with_offers(authenticated_driver, ["Mobil 20GB Paket"])
    config_page.fill_all_required_text_fields_with_dummy_values()
    assert config_page.is_next_button_enabled()
    return config_page


@when("İleri butonuna tıklanır")
def click_next_button(config_page):
    config_page.click_next_and_wait_for_summary()


@then("Sipariş Özeti (Sipariş Gönder) ekranına geçilir")
def navigated_to_order_summary(driver):
    assert driver.find_elements(By.CSS_SELECTOR, "[data-testid='sales-summary-total']")
