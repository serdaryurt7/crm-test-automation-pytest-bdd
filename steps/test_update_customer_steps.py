from pytest_bdd import given, parsers, scenarios, then, when

from pages.create_customer_page import CreateCustomerPage
from pages.update_customer_page import UpdateCustomerPage
from utils import config

scenarios("update_customer.feature")


@given("kullanıcı bir müşterinin Müşteri Bilgisi ekranındadır", target_fixture="update_customer_page")
def user_on_customer_info_screen(authenticated_driver):
    # Sabit bir müşteri ID'sine (paylaşılan, kalıcı bir disposable kayıt)
    # bağımlı olmak yerine - delete_customer.feature'da uygulanan desenle
    # tutarlı olarak - her senaryo için HER SEFERİNDE fresh bir disposable
    # müşteri create_customer akışıyla oluşturuluyor. Bu, testleri
    # birbirinden ve önceki çalıştırmalarda oluşabilecek herhangi bir
    # yan etkiden tamamen bağımsız kılıyor.
    authenticated_driver.get(config.url("/customers/new"))
    create_page = CreateCustomerPage(authenticated_driver)
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

    return UpdateCustomerPage(authenticated_driver)


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


@when("Nationality ID, başka bir müşteriye zaten kayıtlı bir değerle değiştirilir")
def user_sets_conflicting_nationality_id(update_customer_page, driver):
    # Seed veriye (paylaşılan müşteri 1'in TC no'su) bağımlı kalmak
    # yerine, testin KENDİSİ ikinci, bağımsız bir disposable müşteri (B)
    # oluşturup GERÇEK/GÜNCEL bir "zaten kayıtlı" TC numarası elde
    # ediyor - bu, çakışma senaryosunu seed veri değişse/silinse dahi
    # her çalıştırmada güvenilir şekilde tekrarlanabilir kılıyor.
    # Orchestration (iki page object'in birlikte kullanımı) bilinçli
    # olarak burada, step katmanında tutuluyor - page object'lerin
    # birbirini çağırmaması için.
    original_url = update_customer_page.get_detail_url()

    driver.get(config.url("/customers/new"))
    create_page = CreateCustomerPage(driver)
    _, _, _, other_identity_number = create_page.fill_demographic_step_with_faker(gender="Kadın")
    create_page.click_demographic_next()
    create_page.wait_for_address_step()
    create_page.add_address_with_faker()
    create_page.wait_for_address_saved()
    create_page.click_address_next()
    create_page.wait_for_contact_step()
    create_page.fill_contact_step_with_faker()
    create_page.click_submit()
    create_page.wait_for_navigated_to_customer_info()

    update_customer_page.reopen_edit_form(original_url)
    update_customer_page.update_identity_number(other_identity_number)


@then("Nationality ID alanında bir doğrulama hatası anlık olarak görüntülenir")
def identity_number_error_displayed(update_customer_page):
    assert update_customer_page.is_identity_number_error_displayed()


@when("kullanıcı Nationality ID alanını değiştirmeden Kaydet'e tıklar")
def user_saves_without_changing_nationality_id(update_customer_page):
    update_customer_page.click_save()


@then('"already exist" hatası tetiklenmez, güncelleme normal şekilde tamamlanır')
def no_duplicate_nationality_error(update_customer_page):
    # Kaydet sonrası gerçek bir PUT isteği + görüntüleme moduna dönüş
    # asenkron - implicitly_wait kaldırıldıktan sonra kontrol çok daha
    # hızlı çalıştığından, API yanıtı gelmeden anlık okuma yapmak
    # yarış durumuna yol açıyordu. Görüntüleme moduna dönülene kadar
    # bekleniyor.
    update_customer_page.wait.until(lambda d: update_customer_page.is_read_only_view_mode())
    assert not update_customer_page.is_save_error_displayed()


@when("kullanıcı Ad alanını değiştirip İptal butonuna tıklar")
def user_changes_first_name_then_cancels(update_customer_page):
    update_customer_page.attempt_to_type_long_value("Ad", 10)
    update_customer_page.click_cancel()


@then("form kapanır, görüntüleme moduna dönülür")
def form_returns_to_view_mode(update_customer_page):
    # İptal sonrası görüntüleme moduna dönüş Angular'ın DOM'u güncellemesi
    # için kısa bir change-detection cycle'ı gerektirebiliyor (diğer
    # benzer asenkron durumlarla tutarlı olarak anlık kontrol yerine
    # bekleniyor).
    update_customer_page.wait.until(lambda d: update_customer_page.is_read_only_view_mode())


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


@when(parsers.parse('"{alan}" alanına tam 50 karakterlik bir değer girilir'), target_fixture="typed_field_value")
def user_types_exactly_50_characters(update_customer_page, alan):
    return update_customer_page.attempt_to_type_long_value(alan, 50)


@then("alan girilen 50 karakterin tamamını kabul eder")
def field_accepts_full_50_characters(typed_field_value):
    assert len(typed_field_value) == 50


@when("Nationality ID alanı 10 haneli bir değerle değiştirilir")
def user_sets_10_digit_identity_number(update_customer_page):
    update_customer_page.update_identity_number("1000000014")


@then("alanda 11 hane şartına dair bir doğrulama hatası görüntülenir")
def identity_number_length_error_displayed(update_customer_page):
    update_customer_page.wait_for_identity_number_length_error()


@when("Nationality ID alanı, başka hiçbir müşteriye ait olmayan tam 11 haneli geçerli bir değerle değiştirilir")
def user_sets_unique_11_digit_identity_number(update_customer_page):
    update_customer_page.update_identity_number_with_random_unique_value()


@then("herhangi bir doğrulama hatası gösterilmez, Kaydet butonu aktif hale gelir")
def no_identity_number_error_and_save_enabled(update_customer_page):
    update_customer_page.wait_for_save_enabled_with_no_identity_number_error()


@when("Nationality ID alanına 12 haneli bir değer girilmeye çalışılır", target_fixture="typed_field_value")
def user_types_12_digit_identity_number(update_customer_page):
    return update_customer_page.attempt_to_type_long_identity_number(12)


@then("alan yalnızca ilk 11 haneyi kabul eder, 12. hane yazılamaz")
def identity_number_capped_at_11_digits(typed_field_value):
    assert len(typed_field_value) == 11, f"Beklenen 11 hane, gelen: {typed_field_value!r} ({len(typed_field_value)} hane)"
