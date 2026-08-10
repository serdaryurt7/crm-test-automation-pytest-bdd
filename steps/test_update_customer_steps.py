from pytest_bdd import given, parsers, scenarios, then, when
from selenium.webdriver.support.ui import WebDriverWait

from pages.login_page import LoginPage
from pages.search_customers_page import CustomersPage
from pages.update_customer_page import UpdateCustomerPage

scenarios("update_customer.feature")

# Ortak proje kuralı: paylaşılan seed müşterileri (1-3) asla mutasyona
# uğratılmaz; her Edit/Delete/CRUD keşfi tek bir disposable test
# müşterisi (ID 80) üzerinde yapılır.
DISPOSABLE_TEST_CUSTOMER_ID = "80"

# Seed müşteri 1'in gerçek, sistemde zaten kayıtlı Nationality ID'si -
# çakışma (conflict) senaryosunu güvenilir şekilde tetiklemek için
# kullanılıyor (yalnızca okunuyor, seed müşteriye hiçbir mutasyon yapılmaz).
OTHER_CUSTOMERS_NATIONALITY_ID = "10000000146"


@given("kullanıcı bir müşterinin Müşteri Bilgisi ekranındadır", target_fixture="update_customer_page")
def user_on_customer_info_screen(driver, base_url):
    login_page = LoginPage(driver)
    login_page.open(base_url)
    login_page.login("demo", "Password123")
    WebDriverWait(driver, 10).until(lambda d: "/customers" in d.current_url)

    customers_page = CustomersPage(driver)
    customers_page.enter_customer_id(DISPOSABLE_TEST_CUSTOMER_ID)
    customers_page.submit_search()
    customers_page.wait_for_matching_customer_id()
    customers_page.click_customer_row_link()
    customers_page.verify_navigated_to_customer_detail_same_tab(DISPOSABLE_TEST_CUSTOMER_ID)

    return UpdateCustomerPage(driver)


@when("kullanıcı Edit ikonuna tıklar")
@given("kullanıcı düzenleme formundadır")
def user_clicks_edit_icon(update_customer_page):
    update_customer_page.click_edit()


@then("form mevcut bilgilerle önceden dolu açılır")
def form_is_prefilled(update_customer_page):
    assert update_customer_page.is_form_prefilled_correctly()


@when("kullanıcı Ad alanını değiştirip Kaydet'e tıklar")
def user_updates_first_name_and_saves(update_customer_page):
    update_customer_page.update_first_name_with_faker()
    update_customer_page.click_save()


@then("ekrandaki müşteri adı yeni değeri yansıtır")
def displayed_name_reflects_new_value(update_customer_page):
    assert update_customer_page.is_new_first_name_reflected()


@then("güncelleme sayfa yenilense dahi kalıcı olarak korunur")
def update_persists_after_reload(update_customer_page):
    assert update_customer_page.reload_and_verify_first_name_persisted()


@when(parsers.parse('"{alan}" alanı boşaltılır'))
def user_clears_required_field(update_customer_page, alan):
    update_customer_page.clear_required_field(alan)


@then("Kaydet butonu pasif kalır")
def save_button_disabled(update_customer_page):
    assert update_customer_page.is_save_button_disabled()


@when("Nationality ID, başka bir müşteriye zaten kayıtlı bir değerle değiştirilip kaydedilir")
def user_sets_conflicting_nationality_id_and_saves(update_customer_page):
    update_customer_page.update_identity_number(OTHER_CUSTOMERS_NATIONALITY_ID)
    update_customer_page.click_save()


@then(parsers.parse('sistem güncellemeyi reddedip "{expected_message}" mesajını gösterir'))
def update_rejected_with_message(update_customer_page, expected_message):
    assert update_customer_page.get_save_error_text() == expected_message


@then("kullanıcı formda kalır")
def user_stays_in_form(update_customer_page):
    assert not update_customer_page.is_read_only_view_mode()


@when("kullanıcı Nationality ID alanını değiştirmeden Kaydet'e tıklar")
def user_saves_without_changing_nationality_id(update_customer_page):
    update_customer_page.click_save()


@then('"already exist" hatası tetiklenmez, güncelleme normal şekilde tamamlanır')
def no_duplicate_nationality_error(update_customer_page):
    assert not update_customer_page.is_save_error_displayed()
    assert update_customer_page.is_read_only_view_mode()


@when("kullanıcı Ad alanını değiştirip İptal butonuna tıklar")
def user_changes_first_name_then_cancels(update_customer_page):
    update_customer_page.attempt_to_type_long_value("Ad", 10)
    update_customer_page.click_cancel()


@then("form kapanır, görüntüleme moduna dönülür")
def form_returns_to_view_mode(update_customer_page):
    assert update_customer_page.is_read_only_view_mode()


@then("ekran güncelleme öncesi orijinal değerleri gösterir")
def screen_shows_original_values(update_customer_page):
    assert update_customer_page.is_view_showing_original_values()


@then("tüm alanlar salt okunur olarak gösterilir, düzenlenemez")
def all_fields_read_only(update_customer_page):
    assert update_customer_page.is_read_only_view_mode()


@then("başlığın yanında Edit ve Delete ikonları görüntülenir")
def edit_and_delete_icons_visible(update_customer_page):
    assert update_customer_page.is_edit_icon_visible()
    assert update_customer_page.is_delete_icon_visible()


@when(parsers.parse('"{alan}" alanına 51 karakterlik değer girilmeye çalışılır'), target_fixture="typed_field_value")
def user_types_51_characters(update_customer_page, alan):
    return update_customer_page.attempt_to_type_long_value(alan, 51)


@then("alan en fazla 50 karakteri kabul eder")
def field_accepts_max_50_characters(typed_field_value):
    assert len(typed_field_value) == 50


@when('Ad alanına "<script>alert(1)</script>" girilmeye çalışılıp kaydedilir', target_fixture="typed_field_value")
def user_attempts_xss_in_first_name(update_customer_page):
    value = update_customer_page.attempt_xss_in_first_name()
    update_customer_page.click_save()
    return value


@then("sistem yalnızca izin verilen karakterleri kabul eder, zararlı karakterler alana hiç yazılamaz")
def only_safe_characters_accepted(typed_field_value):
    dangerous_characters = set("<>()/")
    assert not (dangerous_characters & set(typed_field_value)), (
        f"Zararlı karakterler alana yazılabildi: {typed_field_value!r}"
    )


@then("herhangi bir script çalıştırılmaz")
def no_script_executed(update_customer_page):
    assert not update_customer_page.has_unexpected_alert()
