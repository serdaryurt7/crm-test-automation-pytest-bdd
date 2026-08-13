from urllib.parse import urlparse

from pytest_bdd import given, scenarios, then, when
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.language_switcher_page import LanguageSwitcherPage
from pages.login_page import LoginPage

scenarios("language_support.feature")


def _login_fresh(driver, base_url):
    # Her test YENİ bir tarayıcı profiliyle başladığından (conftest.py'deki
    # driver fixture'ı) localStorage HER ZAMAN boş - dil varsayılan olarak
    # TR ile başlıyor (canlı doğrulandı, testler arası kirlenme riski yok).
    login_page = LoginPage(driver)
    login_page.open(base_url)
    login_page.login("demo", "Password123")
    WebDriverWait(driver, 10).until(lambda d: "/customers" in d.current_url)
    return LanguageSwitcherPage(driver)


def _get_testid_set(driver, attempts=5):
    # Sayfa navigasyon/dil değişimi sonrası Angular bazı elemanları
    # YENİDEN OLUŞTURABİLİYOR (özellikle ilk yüklemede) - find_elements ile
    # toplanan referanslardan biri, set comprehension TAMAMLANMADAN
    # ARADA stale kalabiliyor (canlı doğrulandı). billing_account_create_
    # page.py'deki find_account_row_by_name() ile AYNI desen: sadece
    # GEÇİCİ stale hatasında (gerçek bir "eksik/hatalı" sonuçtan YAPISAL
    # OLARAK ayrı tutularak) tüm tarama sabit, küçük bir üst sınırla
    # yeniden deneniyor.
    for _ in range(attempts):
        try:
            return {e.get_attribute("data-testid") for e in driver.find_elements(By.CSS_SELECTOR, "[data-testid]")}
        except StaleElementReferenceException:
            continue
    return {e.get_attribute("data-testid") for e in driver.find_elements(By.CSS_SELECTOR, "[data-testid]")}


def _trigger_identity_number_validation_error(driver):
    origin = urlparse(driver.current_url)
    driver.get(f"{origin.scheme}://{origin.netloc}/customers/new")
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "firstName")))
    id_field = driver.find_element(By.ID, "identityNumber")
    id_field.click()
    id_field.send_keys("123")
    id_field.send_keys(Keys.TAB)
    return WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='identityNumber-error']"))
    ).text


@given("kullanıcı uygulamada herhangi bir ekrandadır", target_fixture="lang_page")
def user_on_any_screen(driver, base_url):
    return _login_fresh(driver, base_url)


@when("dil değiştirici butonuna tıklanır")
def click_language_toggle(lang_page):
    lang_page.open_panel()


@then("TR/EN seçenekleri içeren panel açılır")
def panel_with_tr_en_options_opens(lang_page):
    assert lang_page.is_panel_open()
    assert set(lang_page.get_option_codes()) == {"tr", "en"}


@when("dil değiştirici butonuna tekrar tıklanır")
def click_language_toggle_again(lang_page):
    lang_page.close_panel()


@then("panel kapanır")
def panel_closes(lang_page):
    assert not lang_page.is_panel_open()


@given("dil değiştirici panel açıktır", target_fixture="lang_page")
def language_switcher_panel_open(driver, base_url):
    lang_page = _login_fresh(driver, base_url)
    lang_page.open_panel()
    return lang_page


@when('"EN" seçeneğine tıklanır')
def select_en_option(lang_page):
    lang_page.select_language("en")


@then("menü/buton/başlık gibi arayüz metinleri değişir (İngilizce'ye çevrilir)")
def ui_texts_change_after_language_switch(driver, lang_page):
    assert lang_page.get_current_language_code() == "EN"
    assert driver.find_element(By.CSS_SELECTOR, "[data-testid='page-title']").text.strip()


@then("bu tercih kullanıcı farklı ekranlara geçse dahi oturum boyunca korunur")
def preference_persists_across_screens(driver, lang_page):
    driver.find_element(By.CSS_SELECTOR, "[data-testid='nav-customer-create']").click()
    WebDriverWait(driver, 10).until(lambda d: "/customers/new" in d.current_url)
    assert lang_page.get_current_language_code() == "EN"


@given('kullanıcı dili "EN" yapmıştır', target_fixture="lang_page")
def user_set_language_to_en(driver, base_url):
    lang_page = _login_fresh(driver, base_url)
    lang_page.open_panel()
    lang_page.select_language("en")
    return lang_page


@when("sayfa yenilenir")
def page_is_refreshed(driver):
    driver.refresh()
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='language-switcher-toggle']")))


@then("arayüz İngilizce kalmaya devam eder")
def ui_stays_english_after_reload(lang_page):
    assert lang_page.get_current_language_code() == "EN"


@given("kullanıcı arayüz dilini EN olarak ayarlamıştır", target_fixture="lang_page")
def user_configured_language_to_en(driver, base_url):
    lang_page = _login_fresh(driver, base_url)
    lang_page.open_panel()
    lang_page.select_language("en")
    return lang_page


@when("kullanıcı oturumu kapatıp tekrar giriş yapar")
def user_logs_out_and_logs_back_in(driver):
    driver.find_element(By.CSS_SELECTOR, "[data-testid='nav-logout']").click()
    WebDriverWait(driver, 10).until(lambda d: "/login" in d.current_url)
    login_page = LoginPage(driver)
    login_page.wait.until(EC.visibility_of_element_located(login_page.USERNAME_INPUT))
    login_page.login("demo", "Password123")
    WebDriverWait(driver, 10).until(lambda d: "/customers" in d.current_url)


@then("arayüz EN olarak kalmaya devam eder, TR'ye dönmez")
def ui_stays_english_after_relogin(lang_page):
    # Canlı doğrulandı: dil tercihi localStorage tabanlı, oturum
    # kapatma/açmadan BAĞIMSIZ olarak kalıcı - spesifikasyonun "TR'ye
    # döner" varsayımı gerçek davranışla çelişiyordu, kullanıcı kararıyla
    # gerçek/çalışan davranışı doğrulayacak şekilde uyarlandı.
    assert lang_page.get_current_language_code() == "EN"


@given("otomasyon testleri data-testid tabanlı locator kullanmaktadır", target_fixture="testid_snapshot_context")
def automation_relies_on_testid_locators(driver, base_url):
    lang_page = _login_fresh(driver, base_url)
    testids_before = _get_testid_set(driver)
    return lang_page, testids_before


@when('dil "EN" olarak değiştirilir')
def language_is_changed_to_en(testid_snapshot_context):
    lang_page, _ = testid_snapshot_context
    lang_page.open_panel()
    lang_page.select_language("en")


@then("tüm data-testid değerleri dilden bağımsız aynı kalır, yalnızca görünen metin değişir")
def testid_values_remain_stable_across_languages(driver, testid_snapshot_context):
    _, testids_before = testid_snapshot_context
    testids_after = _get_testid_set(driver)
    assert testids_before == testids_after


@given('dil "EN"dir', target_fixture="validation_language_context")
def language_is_en_with_known_turkish_baseline(driver, base_url):
    # Karşılaştırmalı (dilden bağımsız) doğrulama için TR mesajı ÖNCE,
    # EN'e geçmeden hemen önce yakalanıyor - "mesaj değişti mi" kontrolü
    # literal bir dile (ne TR ne EN) bağımlı kalmadan yapılabiliyor.
    lang_page = _login_fresh(driver, base_url)
    turkish_message = _trigger_identity_number_validation_error(driver)
    lang_page.open_panel()
    lang_page.select_language("en")
    return turkish_message


@when("bir doğrulama hatası tetiklenir (Kimlik No formatı)", target_fixture="validation_messages")
def validation_error_is_triggered(driver, validation_language_context):
    turkish_message = validation_language_context
    english_message = _trigger_identity_number_validation_error(driver)
    return turkish_message, english_message


@then("mesaj Türkçe halinden farklı, İngilizce dilde görüntülenir")
def message_differs_from_turkish_version(validation_messages):
    turkish_message, english_message = validation_messages
    assert english_message
    assert english_message != turkish_message


@given('aktif dil "TR"dir', target_fixture="lang_page")
def active_language_is_tr(driver, base_url):
    return _login_fresh(driver, base_url)


@when("dil değiştirici panel görüntülenir")
def language_switcher_panel_displayed(lang_page):
    lang_page.open_panel()


@then('panelde aktif dil ("TR") vurgulanmış olarak işaretlenir')
def active_language_is_highlighted(lang_page):
    assert lang_page.is_language_highlighted_as_active("tr")


@given("kullanıcı dil değiştirici paneli açmıştır", target_fixture="lang_page")
def user_opened_language_switcher_panel(driver, base_url):
    lang_page = _login_fresh(driver, base_url)
    lang_page.open_panel()
    return lang_page


@then("yalnızca TR ve EN seçenekleri listelenir, başka dil bulunmaz")
def only_tr_and_en_options_are_listed(lang_page):
    codes = lang_page.get_option_codes()
    assert len(codes) == 2
    assert set(codes) == {"tr", "en"}
