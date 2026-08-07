from pytest_bdd import given, parsers, scenarios, then, when
from selenium.webdriver.support.ui import WebDriverWait

from pages.create_customer_page import CreateCustomerPage
from pages.login_page import LoginPage
from pages.search_customers_page import CustomersPage as SearchCustomersPage

scenarios("create_customer.feature")


@given("kullanıcı müşteri oluşturma sayfasındadır", target_fixture="create_customer_page")
def user_on_create_customer_page(driver, base_url):
    login_page = LoginPage(driver)
    login_page.open(base_url)
    login_page.login("demo", "Password123")
    WebDriverWait(driver, 10).until(lambda d: "/customers" in d.current_url)

    # Manuel test case'in 1. adımıyla birebir: "No customer found" mesajının
    # altındaki Create Customer butonuna tıklanarak gerçek kullanıcı yolculuğu
    # ile ulaşılıyor (var olan search_customers.feature'daki "No Customer
    # Found" senaryosuyla aynı, doğrulanmış page object metotları tekrar
    # kullanılıyor).
    search_page = SearchCustomersPage(driver)
    search_page.enter_identity_number("00000000000")
    search_page.submit_search()
    search_page.wait_for_no_results_state()
    search_page.click_create_customer_button()
    WebDriverWait(driver, 10).until(lambda d: "/customers/new" in d.current_url)
    return CreateCustomerPage(driver)


@then("girilen değerler ilgili alanlarda görüntülenir")
def demographic_values_displayed(create_customer_page):
    assert create_customer_page.are_demographic_values_displayed()


@when("kullanıcı Demografik Bilgi adımında İleri butonuna tıklar")
def click_demographic_next(create_customer_page):
    create_customer_page.click_demographic_next()


@then('sistem Nationality ID\'nin kayıtlı olmadığını doğrular ve "Adres Bilgisi" ekranını açar')
def address_step_opened(create_customer_page):
    create_customer_page.wait_for_address_step()


@then("Adres adımında İleri butonu pasiftir")
def address_next_disabled(create_customer_page):
    assert create_customer_page.is_address_next_disabled()


@then("sistem adresi kart olarak listeler ve İleri butonu aktif hale gelir")
def address_saved_and_next_enabled(create_customer_page):
    create_customer_page.wait_for_address_saved()
    assert not create_customer_page.is_address_next_disabled()


@when("kullanıcı Adres adımında İleri butonuna tıklar")
def click_address_next(create_customer_page):
    create_customer_page.click_address_next()


@then('sistem "İletişim Kanalı" ekranını açar')
def contact_step_opened(create_customer_page):
    create_customer_page.wait_for_contact_step()


@then("Create butonu aktif hale gelir")
def submit_button_enabled(create_customer_page):
    assert not create_customer_page.is_submit_disabled()


@when("kullanıcı Create butonuna tıklar")
def click_submit(create_customer_page):
    create_customer_page.click_submit()


@then('sistem müşteri kaydını oluşturur ve "Customer Info" ekranını açar')
def navigated_to_customer_info(create_customer_page):
    create_customer_page.wait_for_navigated_to_customer_info()


@then(parsers.parse('müşterinin Cinsiyet bilgisi "{expected_gender}" olarak görüntülenir'))
def customer_info_gender_displayed(create_customer_page, expected_gender):
    assert create_customer_page.get_customer_info_gender_value() == expected_gender


@when(parsers.parse('kullanıcı zorunlu Demografik Bilgi alanlarını Gender "{gender}" ile rastgele (Faker) değerlerle doldurur'))
def fill_demographic_step_with_faker(create_customer_page, gender):
    create_customer_page.fill_demographic_step_with_faker(gender=gender)


@when("kullanıcı Adres alanlarını rastgele (Faker) değerlerle doldurup Save butonuna tıklar")
def add_address_with_faker(create_customer_page):
    create_customer_page.add_address_with_faker()


@when("kullanıcı İletişim Kanalı alanlarını rastgele (Faker) değerlerle doldurur")
def fill_contact_step_with_faker(create_customer_page):
    create_customer_page.fill_contact_step_with_faker()
