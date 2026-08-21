from pytest_bdd import given, parsers, scenarios, then, when

from pages.contact_update_page import ContactUpdatePage
from utils.test_data import FIELD_LIMITS

scenarios("contact_update.feature")


@given("kullanıcı bir müşterinin İletişim Kanalı sekmesindedir", target_fixture="contact_page")
def user_on_contact_tab(disposable_customer):
    return ContactUpdatePage(disposable_customer)


@when("Edit ile Email, Mobile Phone alanları güncellenip Kaydet'e tıklanır")
def user_edits_email_and_mobile_then_saves(contact_page):
    contact_page.click_edit()
    contact_page.update_email_and_mobile_with_faker()
    contact_page.click_save()


@then("güncelleme kaydedilir ve görüntüleme modunda yeni bilgiler yansır")
def update_saved_and_reflected(contact_page):
    assert contact_page.is_new_values_reflected()


@given("kullanıcı düzenleme formundadır", target_fixture="contact_page")
def user_on_edit_form(disposable_customer):
    page = ContactUpdatePage(disposable_customer)
    page.click_edit()
    return page


@when("Email alanına geçersiz formatta bir değer girilir")
def user_enters_invalid_email_format(contact_page):
    contact_page.enter_invalid_email_format()


@then("geçersiz format hatası gösterilir ve güncelleme gerçekleştirilmez")
def invalid_format_error_and_no_update(contact_page):
    assert contact_page.is_email_error_displayed()
    assert contact_page.is_save_button_disabled()


@when(parsers.parse('"{alan}" alanı boşaltılır'))
def user_clears_required_field(contact_page, alan):
    contact_page.clear_required_field(alan)


@then("ilgili alan hatalı olarak işaretlenir")
def related_field_marked_as_error(contact_page):
    assert contact_page.is_required_field_error_displayed("Email") or contact_page.is_required_field_error_displayed(
        "Mobile Phone"
    )


@then("güncelleme gerçekleştirilmez")
def update_not_performed(contact_page):
    assert contact_page.is_save_button_disabled()


@when(parsers.parse('Mobile Phone alanına 8 haneli "{value}" değeri girilir'))
def user_enters_eight_digit_mobile_phone(contact_page, value):
    contact_page.update_mobile_phone(value)


@then("hata gösterilir ve Kaydet butonu pasif kalır")
def error_shown_and_save_disabled(contact_page):
    assert contact_page.is_mobile_phone_error_displayed()
    assert contact_page.is_save_button_disabled()


@given("müşterinin kayıtlı iletişim bilgileri mevcuttur", target_fixture="contact_page")
def customer_has_registered_contact_info(disposable_customer):
    return ContactUpdatePage(disposable_customer)


@when("kullanıcı İletişim Kanalı sekmesini açar")
def user_opens_contact_tab(contact_page):
    pass


@then("iletişim bilgileri salt okunur görüntülenir")
def contact_info_displayed_readonly(contact_page):
    assert contact_page.is_view_mode_readonly_with_edit_icon()


@then("başlığın yanında Edit ikonu bulunur")
def edit_icon_present(contact_page):
    assert contact_page.driver.find_element(*contact_page.EDIT_BUTTON).is_displayed()


@given('"İletişim Kanalı" sekmesi açıktır ve Edit ikonu görünmektedir', target_fixture="contact_page")
def contact_tab_open_with_edit_icon_visible(disposable_customer):
    return ContactUpdatePage(disposable_customer)


@when("kullanıcı Edit ikonuna tıklar")
def user_clicks_edit_icon(contact_page):
    contact_page.click_edit()


@then("sistem iletişim bilgilerini düzenlemek için formu açar")
def system_opens_edit_form(contact_page):
    assert contact_page.is_edit_form_open()


@given("kullanıcı formda değişiklik yapmıştır", target_fixture="contact_page")
def user_made_changes_in_form(disposable_customer):
    page = ContactUpdatePage(disposable_customer)
    page.click_edit()
    page.update_email_and_mobile_with_faker()
    return page


@when("Home Phone ve Fax alanları boş bırakılıp yalnızca zorunlu alanlar doldurulur")
def user_fills_only_required_fields(contact_page):
    contact_page.fill_only_required_fields_with_faker()


@then("güncelleme başarıyla tamamlanır")
def update_completes_successfully(contact_page):
    contact_page.click_save()
    assert contact_page.is_new_values_reflected()


@when("İptal butonuna tıklanır")
def user_clicks_cancel(contact_page):
    contact_page.click_cancel()


@then("değişiklikler kaydedilmez, önceki bilgiler korunur")
def changes_discarded_original_preserved(contact_page):
    assert contact_page.is_view_showing_original_values()


@given("müşterinin dışında başka bir müşteride zaten kayıtlı bir email vardır", target_fixture="duplicate_email_context")
def another_customer_has_this_email(disposable_customer, new_customer):
    other_page = ContactUpdatePage(disposable_customer)
    taken_email = other_page.get_displayed_email()

    new_customer()
    contact_page = ContactUpdatePage(disposable_customer)
    contact_page.click_edit()
    return contact_page, taken_email


@when("kullanıcı bu emaili Email alanına girer")
def user_enters_the_taken_email(duplicate_email_context):
    contact_page, taken_email = duplicate_email_context
    contact_page.enter_email_expecting_duplicate_rejection(taken_email)


@then("sistem güncellemeyi reddeder, ilgili alan hatalı olarak işaretlenir")
def system_rejects_duplicate_email(duplicate_email_context):
    contact_page, _ = duplicate_email_context
    assert contact_page.is_email_error_displayed()
    assert contact_page.is_save_button_disabled()


@when("telefon numarası değiştirilir")
def phone_number_is_changed(contact_page):
    contact_page.update_mobile_phone("5" + "".join(str((i * 3) % 10) for i in range(9)))


@then('Mobile, Home Phone, Fax alanlarının önünde sabit ülke kodu öneki değişmeden görüntülenmeye devam eder')
def country_code_remains_fixed(contact_page):
    assert contact_page.is_country_code_fixed_at_plus_90()


@when("Mobile Phone alanına 9 haneli geçerli formatta bir değer girilir")
def user_enters_nine_digit_mobile_phone(contact_page):
    contact_page.enter_mobile_phone_nine_digits()


@when("Mobile Phone alanına tam 10 haneli geçerli bir değer girilir")
def user_enters_ten_digit_mobile_phone(contact_page):
    contact_page.enter_mobile_phone_ten_digits()


@then("herhangi bir doğrulama hatası gösterilmez ve Kaydet butonu aktif hale gelir")
def no_error_and_save_enabled(contact_page):
    contact_page.wait_for_no_mobile_phone_error_and_save_enabled()


@when(parsers.parse('"{alan}" alanına 11 haneli bir değer girilmeye çalışılır'), target_fixture="typed_phone_value")
def user_attempts_eleven_digits_in_phone_field(contact_page, alan):
    return contact_page.attempt_to_type_eleven_digits_in_phone_field(alan)


@then("alan yalnızca ilk 10 haneyi kabul eder")
def phone_field_capped_at_ten_digits(typed_phone_value):
    assert len(typed_phone_value) == FIELD_LIMITS["gsm"], f"Beklenen 10 hane, gelen: {typed_phone_value!r} ({len(typed_phone_value)} hane)"


@when("Email alanına formatça geçerli ama 150 karakterden uzun bir değer girilir", target_fixture="typed_long_email")
def user_enters_long_valid_email(contact_page):
    return contact_page.attempt_to_type_long_valid_email(150)


@then("alan girilen değerin tamamını kabul eder, herhangi bir HTML seviyesi kısıtlama uygulanmaz")
def email_field_accepts_full_long_value(contact_page, typed_long_email):
    assert contact_page.driver.find_element(*contact_page.EMAIL_INPUT).get_attribute("value") == typed_long_email
