from pytest_bdd import given, parsers, scenarios, then, when
from selenium.webdriver.support.ui import WebDriverWait

from pages.login_page import LoginPage
from utils.session import expire_refresh_token

scenarios("login.feature")


@given("kullanıcı login sayfasındadır", target_fixture="login_page")
def user_on_login_page(driver, base_url):
    page = LoginPage(driver)
    page.open(base_url)
    return page


@when(parsers.parse('"{username}" kullanıcı adı ve "{password}" şifresi ile giriş yapar'))
def user_logs_in(login_page, username, password):
    login_page.login(username, password)


@then("kullanıcı başarılı bir şekilde sisteme giriş yapmış olur")
def login_successful(driver):
    WebDriverWait(driver, 10).until(lambda d: "/customers" in d.current_url)
    assert "/customers" in driver.current_url


@then("kullanıcı adı veya şifre hatalı uyarısı görüntülenir")
def invalid_login_error_shown(login_page):
    assert "Kullanıcı adı veya şifre hatalı" in login_page.get_error_message()


def _optional_text(text: str) -> str:
    return text


_optional_text.pattern = r".*"
_EXTRA_TYPES = {"OptionalText": _optional_text}


@when(parsers.cfparse('"{username:OptionalText}" kullanıcı adı ve "{password:OptionalText}" şifresi girilir', extra_types=_EXTRA_TYPES))
def user_fills_credentials(login_page, username, password):
    login_page.fill_credentials(username, password)


@then("giriş butonu pasif kalır")
@then("Login butonu pasif duruma geçer")
def login_button_disabled(login_page):
    assert login_page.is_login_button_disabled()


@when("kullanıcı Login butonuna tıklar")
def user_clicks_login_button(login_page):
    login_page.click_login_button()


@then("giriş butonu aktif hale gelir")
def login_button_enabled(login_page):
    # Diğer benzer "X aktif hale gelir" step'leriyle tutarlı olarak:
    # ağır/uzun suite koşumlarında form geçerlilik durumunun anlık
    # okumadan hemen sonra güncellenmesi garanti değil - gerçekten
    # aktif olana kadar bekleniyor, sabit sleep yerine.
    WebDriverWait(login_page.driver, 10).until(lambda d: not login_page.is_login_button_disabled())


@then("herhangi bir script çalıştırılmaz ve yetkisiz erişim sağlanmaz")
def no_script_execution_and_no_unauthorized_access(login_page, driver):
    assert not login_page.has_unexpected_alert(), (
        "Girilen payload bir tarayıcı alert'i olarak çalıştı - XSS açığı tespit edildi"
    )
    assert "/customers" not in driver.current_url, (
        "Injection payload'ı ile yetkisiz erişim sağlandı"
    )
    assert not login_page.is_last_submitted_value_reflected_unescaped(), (
        "Girilen injection/XSS payload'ı sayfada ham (unescaped) olarak yansıtılıyor"
    )


@when("kullanıcı tarayıcıdan doğrudan login adresine gitmeyi dener")
def user_navigates_directly_to_login_url(driver, base_url):
    WebDriverWait(driver, 10).until(lambda d: "/customers" in d.current_url)
    driver.get(base_url)


@then("kullanıcı login formu gösterilmeden Müşteri Arama ekranına yönlendirilir")
def redirected_to_customers_without_login_form(driver, login_page):
    WebDriverWait(driver, 10).until(lambda d: "/customers" in d.current_url)
    assert "/customers" in driver.current_url
    assert not login_page.is_login_form_displayed(), (
        "Kullanıcı zaten giriş yapmışken /login ziyaretinde login formu gösterildi"
    )


@then("hata mesajı ekrandan kalkar")
def error_message_disappears(login_page):
    login_page.wait_for_error_message_to_disappear()


@when("kullanıcı art arda 5 kez hatalı bilgilerle giriş dener")
def user_attempts_five_failed_logins(login_page):
    for _ in range(5):
        login_page.login("admin-crm", "WrongPass123")
        login_page.get_error_message()


@then("hesap kilitlenir ve doğru bilgilerle bile giriş yapılamaz")
def account_locked_even_with_correct_credentials(login_page, driver):
    login_page.login("admin-crm", "Password123")
    login_page.get_error_message()
    assert "/customers" not in driver.current_url, "Hesap kilitliyken doğru bilgilerle giriş başarılı oldu"


@when(parsers.parse('kullanıcı şifre alanına "{password}" değerini girer'))
def user_enters_password(login_page, password):
    login_page.enter_password(password)


@when("kullanıcı göz ikonuna tıklar")
@when("kullanıcı göz ikonuna tekrar tıklar")
def user_clicks_eye_icon(login_page):
    login_page.toggle_password_visibility()


@then("şifre karakterleri maskeli görüntülenir")
@then("şifre karakterleri tekrar maskeli görüntülenir")
def password_is_masked(login_page):
    assert login_page.get_password_input_type() == "password"


@then("şifre karakterleri düz metin olarak görüntülenir")
def password_is_visible(login_page):
    assert login_page.get_password_input_type() == "text"


@when("kullanıcının oturum süresi dolar")
def user_session_expires(driver):
    WebDriverWait(driver, 10).until(lambda d: "/customers" in d.current_url)
    expire_refresh_token(driver)
    driver.refresh()


@then("kullanıcı otomatik olarak login ekranına yönlendirilir")
def redirected_to_login_screen(driver):
    WebDriverWait(driver, 10).until(lambda d: "/login" in d.current_url)
    assert "/login" in driver.current_url


@when("kullanıcı adı ve şifre alanlarına 50 karaktere eşit uzunlukta değerler girilir")
def user_enters_values_of_exactly_50_characters(login_page):
    login_page.enter_long_values(length=50)


@when("kullanıcı adı ve şifre alanlarına 51 karakter uzunluğunda değerler girilir")
def user_enters_values_of_51_characters(login_page):
    login_page.enter_long_values(length=51)


@then("her iki alan da en fazla 50 karakter kabul eder")
def fields_accept_max_50_characters(login_page):
    assert len(login_page.get_username_value()) == 50, "username alanı 50 karakteri aşıyor"
    assert len(login_page.get_password_value()) == 50, "password alanı 50 karakteri aşıyor"


@when(parsers.parse('"{username}" kullanıcı adı ile art arda 5 kez hatalı bilgilerle giriş dener'), target_fixture="last_error_message")
def user_attempts_five_failed_logins_with_username(login_page, username):
    last_message = None
    for _ in range(5):
        login_page.login(username, "WrongPass123")
        last_message = login_page.get_error_message()
    return last_message


@then(parsers.parse('son hata mesajı "{unexpected_message}" olmamalıdır'))
def last_message_should_not_be(last_error_message, unexpected_message):
    assert last_error_message != unexpected_message, (
        f"Tanımsız kullanıcı için beklenmeyen kilitlenme mesajı gösterildi: {last_error_message!r}"
    )
