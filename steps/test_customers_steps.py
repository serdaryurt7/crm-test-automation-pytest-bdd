from pytest_bdd import given, parsers, scenarios, then, when
from selenium.webdriver.support.ui import WebDriverWait

from pages.customers_page import CustomersPage
from pages.login_page import LoginPage

scenarios("customers.feature")


@given("kullanıcı müşteri arama sayfasındadır", target_fixture="customers_page")
def user_on_customers_page(driver, base_url):
    login_page = LoginPage(driver)
    login_page.open(base_url)
    login_page.login("demo", "Password123")
    WebDriverWait(driver, 10).until(lambda d: "/customers" in d.current_url)
    return CustomersPage(driver)


@when("kullanıcı arama kriteri girmez")
def user_enters_no_search_criteria(customers_page):
    customers_page.clear_all_search_fields()


@then("Ara butonu pasif kalır")
def search_button_disabled(customers_page):
    assert customers_page.is_search_button_disabled()


@then("sistem tüm arama alanlarını görüntüler")
def all_search_fields_visible(customers_page):
    assert customers_page.are_all_search_fields_visible()


@then("sistem Search ve Clear butonlarını görüntüler")
def search_buttons_visible(customers_page):
    assert customers_page.are_search_buttons_visible()


@then("B2C sekmesi aktif, B2B sekmesi pasif görüntülenir")
def b2c_active_b2b_inactive(customers_page):
    assert customers_page.is_b2c_active()
    assert customers_page.is_b2b_inactive()


@when("kullanıcı B2B sekmesine tıklamayı dener")
def user_tries_to_click_b2b(customers_page):
    customers_page.try_click_b2b()


@when(parsers.parse('kullanıcı ID Number alanına "{value}" değerini girer'))
@when(parsers.parse('kullanıcı ID Number alanına "{value}" değerini girmeyi dener'))
def user_enters_identity_number(customers_page, value):
    customers_page.enter_identity_number(value)


@then(parsers.parse('ID Number alanında "{value}" değeri görüntülenir'))
def identity_number_value_shown(customers_page, value):
    assert customers_page.get_identity_number_value() == value


@then("Search butonu aktif hale gelir")
def search_button_enabled(customers_page):
    assert not customers_page.is_search_button_disabled()


@when("kullanıcı Search butonuna tıklar")
@when("kullanıcı Search butonuna tıklamayı dener")
def user_clicks_search_button(customers_page):
    customers_page.submit_search()


@then("girilen ID Number'a sahip müşteri kaydı sonuç tablosunda görüntülenir")
def matching_customer_shown(customers_page):
    customers_page.wait_for_matching_customer()


@then("ID Number alanı yalnızca ilk 11 haneyi kabul eder")
def identity_number_truncated_to_11(customers_page):
    assert len(customers_page.get_identity_number_value()) == 11


@then(parsers.parse('"{message}" mesajı görüntülenir'))
def validation_message_shown(customers_page, message):
    customers_page.wait_for_empty_state_message(message)


@when(parsers.parse('kullanıcı Customer ID alanına "{value}" değerini girer'))
def user_enters_customer_id(customers_page, value):
    customers_page.enter_customer_id(value)


@then("yalnızca bu Customer ID'ye tam eşleşen tek müşteri kaydı sonuç listesinde görüntülenir")
def matching_customer_id_shown(customers_page):
    customers_page.wait_for_matching_customer_id()


@then(parsers.parse('Customer ID alanında "{value}" değeri görüntülenir'))
def customer_id_value_shown(customers_page, value):
    assert customers_page.get_customer_id_value() == value


@then("Customer ID alanı 20 üzeri karakter alamaz")
def customer_id_rejects_more_than_20_chars(customers_page):
    assert len(customers_page.get_customer_id_value()) == 20


@when(parsers.parse('kullanıcı GSM alanına "{value}" değerini girer'))
def user_enters_gsm(customers_page, value):
    customers_page.enter_gsm(value)


@then(parsers.parse('GSM alanında "{value}" değeri görüntülenir'))
def gsm_value_shown(customers_page, value):
    assert customers_page.get_gsm_value() == value


@then("GSM alanı en fazla 10 haneyi kabul eder")
def gsm_accepts_max_10_digits(customers_page):
    assert len(customers_page.get_gsm_value()) == 10
