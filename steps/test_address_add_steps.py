from urllib.parse import urlparse

from faker import Faker
from pytest_bdd import given, parsers, scenarios, then, when
from selenium.webdriver.support.ui import WebDriverWait

from pages.address_add_page import AddressAddPage
from pages.create_customer_page import CreateCustomerPage
from pages.login_page import LoginPage

scenarios("address_add.feature")

fake = Faker("tr_TR")


def _create_fresh_customer_and_open_address_tab(driver, base_url):
    # Adres ekleme mutasyonlar barındırdığından (yeni kart oluşturma)
    # HER SENARYO için fresh, tek kullanımlık bir disposable müşteri
    # create_customer akışıyla oluşturuluyor - address_update.feature'da
    # kurulan desenle tutarlı, tam bağımsızlık ve tekrarlanabilirlik için.
    login_page = LoginPage(driver)
    login_page.open(base_url)
    login_page.login("demo", "Password123")
    WebDriverWait(driver, 10).until(lambda d: "/customers" in d.current_url)

    origin = urlparse(driver.current_url)
    driver.get(f"{origin.scheme}://{origin.netloc}/customers/new")
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

    return AddressAddPage(driver)


@given("kullanıcı bir müşterinin Adres sekmesindedir", target_fixture="address_page")
def user_on_address_tab(driver, base_url):
    return _create_fresh_customer_and_open_address_tab(driver, base_url)


@given("müşterinin zaten kayıtlı bir adresi vardır", target_fixture="address_page")
def customer_already_has_one_address(driver, base_url):
    # Fresh müşteri create_customer wizard'ı sırasında zaten TAM OLARAK
    # 1 adresle oluşturuluyor - ek bir adım gerekmiyor.
    return _create_fresh_customer_and_open_address_tab(driver, base_url)


@given("kullanıcı yeni adres formundadır", target_fixture="address_page")
def user_on_new_address_form(driver, base_url):
    page = _create_fresh_customer_and_open_address_tab(driver, base_url)
    page.click_add_address()
    return page


@given("kullanıcı yeni adres formunu doldurmuştur", target_fixture="address_page")
def user_filled_new_address_form(driver, base_url):
    page = _create_fresh_customer_and_open_address_tab(driver, base_url)
    page.snapshot_card_count()
    page.click_add_address()
    page.fill_new_address_form(fake.street_name(), fake.building_number(), fake.sentence(nb_words=4))
    return page


@given("müşterinin 2 kayıtlı adresi vardır", target_fixture="address_page")
def customer_has_two_addresses(driver, base_url):
    page = _create_fresh_customer_and_open_address_tab(driver, base_url)
    page.add_new_address_and_wait_for_card(fake.street_name(), fake.building_number(), fake.sentence(nb_words=4))
    return page


@given("kullanıcı yeni bir adres eklemiştir", target_fixture="address_page")
def user_added_new_address(driver, base_url):
    page = _create_fresh_customer_and_open_address_tab(driver, base_url)
    page.add_new_address_and_wait_for_card(fake.street_name(), fake.building_number(), fake.sentence(nb_words=4))
    return page


@when("""kullanıcı "Yeni Adres Ekle" butonuna tıklayıp formu doldurup Save'e tıklar""")
def user_opens_fills_and_saves_new_address(address_page):
    address_page.add_new_address_and_wait_for_card(fake.street_name(), fake.building_number(), fake.sentence(nb_words=4))


@then("sistem gerçek bir POST isteğiyle (…/addresses) yeni adresi kaydeder")
def system_persists_new_address_via_real_backend_call(address_page):
    assert address_page.wait_for_new_address_persisted_after_reload()


@when("kullanıcı yeni bir adres ekler")
def user_adds_a_new_address(address_page):
    address_page.add_new_address_and_wait_for_card(fake.street_name(), fake.building_number(), fake.sentence(nb_words=4))


@then("önceki kart silinmez, yeni adres AYRI bir kart olarak eklenir")
def previous_card_not_deleted_new_card_added_separately(address_page):
    assert address_page.is_new_card_added_as_separate_card()


@when(parsers.parse('"{alan}" alanı boşaltılır'))
def user_leaves_field_empty_while_filling_others(address_page, alan):
    address_page.fill_new_address_form(
        fake.street_name(), fake.building_number(), fake.sentence(nb_words=4), skip_field=alan
    )


@then("Save butonu pasif kalır")
def save_button_stays_disabled(address_page):
    assert address_page.is_save_button_disabled()


@when(parsers.parse('Bina No alanına "{value}" gibi harf+rakam karışık bir değer girilir'), target_fixture="building_no_test_value")
def user_types_alphanumeric_building_no(address_page, value):
    address_page.type_into_building_no(value)
    return value


@then("değer sorunsuz kabul edilir")
def value_is_accepted_without_error(address_page, building_no_test_value):
    assert address_page.get_building_no_value() == building_no_test_value


@when("İptal butonuna tıklanır")
def user_clicks_cancel(address_page):
    address_page.click_cancel()


@then("hiçbir adres kaydedilmez")
def no_address_is_saved(address_page):
    assert not address_page.is_edit_form_open()
    assert address_page.card_count_matches_snapshot()


@when("Şehir dropdown'ı açılır")
def user_opens_city_dropdown(address_page):
    address_page.open_city_dropdown()


@then("yalnızca 81 il listelenir, serbest metin girişine izin verilmez")
def only_81_provinces_listed_no_free_text(address_page):
    assert address_page.is_city_dropdown_restricted_to_defined_provinces()


@when("kullanıcı 3. bir adres daha ekler")
def user_adds_third_address(address_page):
    address_page.add_new_address_and_wait_for_card(fake.street_name(), fake.building_number(), fake.sentence(nb_words=4))


@then("herhangi bir üst sınır hatasıyla karşılaşılmadan 3 adres de listelenir")
def three_addresses_listed_without_upper_limit_error(address_page):
    assert address_page.get_card_count() == 3


@when("Adres sekmesi görüntülenir")
def address_tab_is_displayed(address_page):
    assert address_page.get_card_count() >= 1


@then('yeni kart "Şehir, Sokak Adı, No" formatında okunabilir şekilde listede yer alır')
def new_card_is_well_formed_last_in_list(address_page):
    assert address_page.is_new_card_last_and_well_formed()
