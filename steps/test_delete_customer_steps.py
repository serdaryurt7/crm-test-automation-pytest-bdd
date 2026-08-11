from urllib.parse import urlparse

from pytest_bdd import given, scenarios, then, when
from selenium.webdriver.support.ui import WebDriverWait

from pages.create_customer_page import CreateCustomerPage
from pages.delete_customer_page import DeleteCustomerPage
from pages.login_page import LoginPage
from pages.search_customers_page import CustomersPage

scenarios("delete_customer.feature")


@given("kullanıcı silinecek müşterinin Müşteri Bilgisi ekranındadır", target_fixture="delete_customer_page")
def user_on_customer_to_delete_info_screen(driver, base_url):
    login_page = LoginPage(driver)
    login_page.open(base_url)
    login_page.login("demo", "Password123")
    WebDriverWait(driver, 10).until(lambda d: "/customers" in d.current_url)

    # Silme (Evet ile onaylanan) GERİ DÖNÜŞÜ OLMAYAN bir mutasyon -
    # canlı doğrulandı: müşteri sonrasında hem arama sonuçlarından hem
    # de doğrudan URL erişiminden tamamen kayboluyor. Sabit bir müşteri
    # ID'si kullanmak, suite'in İKİNCİ çalıştırmasında "müşteri zaten
    # silinmiş, bulunamıyor" hatasıyla TÜM senaryoları bozardı - bu
    # yüzden her senaryo için HER SEFERİNDE fresh, tek kullanımlık bir
    # disposable müşteri create_customer akışıyla oluşturuluyor.
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

    return DeleteCustomerPage(driver)


@when("kullanıcı Delete ikonuna tıklar")
@given("onay penceresi görüntülenmektedir")
def user_clicks_delete_icon(delete_customer_page):
    delete_customer_page.click_delete()


@then("onay penceresi, silme mesajı ve Evet/Hayır butonlarıyla birlikte görüntülenir")
def confirm_dialog_displayed(delete_customer_page):
    assert delete_customer_page.is_confirm_dialog_displayed_with_buttons()


@when('kullanıcı "Hayır" butonuna tıklar')
def user_clicks_no(delete_customer_page):
    delete_customer_page.click_confirm_no()


@then("pencere kapanır")
def dialog_closes(delete_customer_page):
    assert not delete_customer_page.is_dialog_open()


@then("müşteri kaydı hiçbir şekilde değiştirilmeden ekranda kalmaya devam eder")
def customer_unchanged(delete_customer_page):
    assert delete_customer_page.get_status() == "Aktif"


@when("kullanıcı arka plandaki herhangi bir alanla etkileşime girmeyi dener")
def user_attempts_background_interaction(delete_customer_page):
    delete_customer_page.attempt_background_interaction()


@then("pencere modal davranışı gösterip arka planı engeller")
def modal_blocks_background(delete_customer_page):
    assert not delete_customer_page.did_background_click_succeed()
    assert delete_customer_page.is_dialog_open()


@when('kullanıcı "Evet" butonuna tıklar')
def user_clicks_yes(delete_customer_page):
    delete_customer_page.click_confirm_yes()


@then("kullanıcı Müşteri Arama ekranına yönlendirilir")
def redirected_to_search(delete_customer_page):
    delete_customer_page.wait_for_redirect_to_search()


@then("silinen müşteri arama sonuçlarında artık görüntülenmez")
def deleted_customer_not_in_search_results(delete_customer_page, driver):
    customer_id = delete_customer_page.get_customer_id()
    delete_customer_page.wait_for_redirect_to_search()
    customers_page = CustomersPage(driver)
    customers_page.enter_customer_id(customer_id)
    customers_page.submit_search()
    customers_page.wait_for_no_results_state()


@then('silinen müşterinin eski detay ekranına doğrudan gidildiğinde bir "bulunamadı" durumu görüntülenir')
def deleted_customer_direct_url_shows_error(delete_customer_page):
    delete_customer_page.wait_for_redirect_to_search()
    delete_customer_page.reload_detail_url()
    assert delete_customer_page.is_empty_state_message_displayed()
