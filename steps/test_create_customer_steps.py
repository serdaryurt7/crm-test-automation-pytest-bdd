from pytest_bdd import given, parsers, scenarios, then, when
from selenium.webdriver.support.ui import WebDriverWait

from pages.create_customer_page import CreateCustomerPage
from pages.search_customers_page import CustomersPage as SearchCustomersPage
from utils.test_data import FIELD_LIMITS, fake

scenarios("create_customer.feature")


@given("kullanıcı müşteri oluşturma sayfasındadır", target_fixture="create_customer_page")
def user_on_create_customer_page(authenticated_driver):
    search_page = SearchCustomersPage(authenticated_driver)
    search_page.enter_identity_number("00000000000")
    search_page.submit_search()
    search_page.wait_for_no_results_state()
    search_page.click_create_customer_button()
    WebDriverWait(authenticated_driver, 10).until(lambda d: "/customers/new" in d.current_url)
    return CreateCustomerPage(authenticated_driver)


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
    create_customer_page.wait.until(lambda d: not create_customer_page.is_submit_disabled())


@when("kullanıcı Create butonuna tıklar")
def click_submit(create_customer_page):
    create_customer_page.click_submit()


@then('sistem müşteri kaydını oluşturur ve "Customer Info" ekranını açar')
def navigated_to_customer_info(create_customer_page):
    create_customer_page.wait_for_navigated_to_customer_info()


@then(parsers.parse('müşterinin Cinsiyet bilgisi "{expected_gender}" olarak görüntülenir'))
def customer_info_gender_displayed(create_customer_page, expected_gender):
    assert create_customer_page.get_customer_info_gender_value() == expected_gender


@when(parsers.parse('kullanıcı zorunlu Demografik Bilgi alanlarını Gender "{gender}" ile rastgele Faker değerlerle doldurur'))
def fill_demographic_step_with_faker(create_customer_page, gender):
    create_customer_page.fill_demographic_step_with_faker(gender=gender)


@when("kullanıcı Adres alanlarını rastgele Faker değerlerle doldurup Save butonuna tıklar")
def add_address_with_faker(create_customer_page):
    create_customer_page.add_address_with_faker()


@when("kullanıcı İletişim Kanalı alanlarını rastgele Faker değerlerle doldurur")
def fill_contact_step_with_faker(create_customer_page):
    create_customer_page.fill_contact_step_with_faker()


@given('kullanıcı "Demografik Bilgi" ekranında bazı alanları doldurmuştur')
def fill_some_demographic_fields(create_customer_page):
    create_customer_page.fill_some_demographic_fields()


@when('kullanıcı "Cancel" butonuna tıklar')
def click_cancel(create_customer_page):
    create_customer_page.click_demographic_cancel()


@then("sistem işlemi iptal eder ve kullanıcıyı müşteri listesi ekranına yönlendirir")
def cancelled_and_redirected_to_customer_list(create_customer_page):
    create_customer_page.wait_for_navigated_to_customer_list()


@then("girilen hiçbir bilgi sistemde kaydedilmez")
def no_data_saved(driver, create_customer_page):
    search_page = SearchCustomersPage(driver)
    search_page.enter_identity_number(create_customer_page._last_identity_number)
    search_page.submit_search()
    search_page.wait_for_no_results_state()


@given('kullanıcı "Adres Bilgi" ekranındadır')
def user_on_address_info_screen(create_customer_page):
    create_customer_page.fill_demographic_step_with_faker(gender="Kadın")
    create_customer_page.click_demographic_next()
    create_customer_page.wait_for_address_step()


@then("her iki adres kartı da ayrı ayrı ve eksiksiz görüntülenir, İleri butonu aktif kalır")
def both_address_cards_displayed_and_next_enabled(create_customer_page):
    assert create_customer_page.are_all_entered_addresses_displayed_as_cards()
    assert not create_customer_page.is_address_next_disabled()


@given('kullanıcı "Contact Medium" ekranında iletişim bilgilerini rastgele Faker değerlerle doldurmuştur')
def user_on_contact_medium_with_data_filled(create_customer_page):
    create_customer_page.fill_demographic_step_with_faker(gender="Kadın")
    create_customer_page.click_demographic_next()
    create_customer_page.wait_for_address_step()
    create_customer_page.add_address_with_faker()
    create_customer_page.wait_for_address_saved()
    create_customer_page.click_address_next()
    create_customer_page.wait_for_contact_step()
    create_customer_page.fill_contact_step_with_faker()


@when('kullanıcı "Previous" butonuna tıklar')
def click_contact_back(create_customer_page):
    create_customer_page.click_contact_back()


@then('sistem kullanıcıyı "Adres Bilgi" ekranına yönlendirir ve daha önce kaydedilmiş adres kartı eksiksiz görüntülenir')
def redirected_to_address_step_with_card_preserved(create_customer_page):
    create_customer_page.wait_for_address_saved()
    assert create_customer_page.are_all_entered_addresses_displayed_as_cards()


@then("varsa önceden girilmiş iletişim bilgileri korunur")
def contact_values_preserved(create_customer_page):
    assert create_customer_page.are_contact_values_displayed()


@when('kullanıcı zorunlu alanlardan birini "Soyad" boş bırakır')
def fill_demographic_step_without_last_name(create_customer_page):
    create_customer_page.fill_demographic_step_without_last_name()


@then('"Next" butonu pasif durumdadır')
def demographic_next_disabled(create_customer_page):
    assert create_customer_page.is_demographic_next_disabled()


@when("kullanıcı eksik bırakılan zorunlu alanı doldurur")
def fill_missing_last_name(create_customer_page):
    create_customer_page.fill_missing_last_name()


@then('"Next" butonu aktif hale gelir')
def demographic_next_enabled(create_customer_page):
    create_customer_page.wait.until(lambda d: not create_customer_page.is_demographic_next_disabled())


@given("kullanıcı adres girişi penceresini açmıştır")
def user_has_opened_address_form(create_customer_page):
    create_customer_page.fill_demographic_step_with_faker(gender="Kadın")
    create_customer_page.click_demographic_next()
    create_customer_page.wait_for_address_step()
    create_customer_page.click_add_address()
    create_customer_page.wait_for_address_form_open()


@when('kullanıcı zorunlu adres alanlarından birini "Şehir" boş bırakır')
def fill_address_form_without_city(create_customer_page):
    create_customer_page.fill_address_form_without_city()


@then('"Save" butonu pasif durumdadır')
def address_save_disabled(create_customer_page):
    assert create_customer_page.is_address_save_disabled()


@when("kullanıcı eksik bırakılan zorunlu adres alanını doldurur")
def fill_missing_city(create_customer_page):
    create_customer_page.fill_missing_city()


@then('"Save" butonu aktif hale gelir')
def address_save_enabled(create_customer_page):
    create_customer_page.wait.until(lambda d: not create_customer_page.is_address_save_disabled())


@given('kullanıcı "Contact Medium" ekranındadır')
def user_on_contact_medium_screen(create_customer_page):
    create_customer_page.fill_demographic_step_with_faker(gender="Kadın")
    create_customer_page.click_demographic_next()
    create_customer_page.wait_for_address_step()
    create_customer_page.add_address_with_faker()
    create_customer_page.wait_for_address_saved()
    create_customer_page.click_address_next()
    create_customer_page.wait_for_contact_step()
    create_customer_page.fix_email_with_faker()
    create_customer_page.fill_mobile_phone_with_faker()


@when("kullanıcı email alanına geçersiz formatta bir değer girer")
def enter_invalid_email(create_customer_page):
    create_customer_page.enter_invalid_email_format()


@then("sistem geçersiz email formatı uyarısını görüntüler")
def invalid_email_warning_displayed(create_customer_page):
    assert create_customer_page.is_email_error_displayed()


@then("Create butonu pasif durumdadır")
def submit_button_disabled(create_customer_page):
    assert create_customer_page.is_submit_disabled()


@when("kullanıcı email alanını geçerli formatta bir değerle günceller")
def fix_email(create_customer_page):
    create_customer_page.fix_email_with_faker()


@then('"Birth Date" alanı gün,ay,yıl formatında maskeli bir metin giriş alanıdır')
def birth_date_is_masked_text_input(create_customer_page):
    assert create_customer_page.is_birth_date_masked_text_input()


@when('kullanıcı "Birth Date" alanına bir tarih girer')
def enter_birth_date(create_customer_page):
    create_customer_page.enter_birth_date_with_faker()


@then('seçilen tarih "Birth Date" alanına doğru şekilde yazılır')
def birth_date_displayed_correctly(create_customer_page):
    assert create_customer_page.is_birth_date_displayed_correctly()


@then('"Gender" alanı ekrana ilk geldiğinde varsayılan olarak "Erkek" seçili görüntülenir')
def gender_defaults_to_erkek(create_customer_page):
    assert create_customer_page.get_selected_gender_text() == "Erkek"


@when('kullanıcı "Gender" alanını açar')
def click_gender_field(create_customer_page):
    create_customer_page.click_gender_field()


@then("sistem tanımlı cinsiyet seçeneklerini listeler")
def gender_options_listed(create_customer_page):
    assert create_customer_page.get_gender_options() == ["Erkek", "Kadın"]


@when('kullanıcı listeden "Kadın" seçeneğini seçer')
def select_kadin(create_customer_page):
    create_customer_page.select_gender("Kadın")


@then('"Gender" alanı "Kadın" olarak güncellenir')
def gender_updated_to_kadin(create_customer_page):
    assert create_customer_page.get_selected_gender_text() == "Kadın"


@when('kullanıcı adres kartındaki "Edit" seçeneğine tıklar')
def click_address_card_edit(create_customer_page):
    create_customer_page.click_address_card_edit()


@then("adres bilgileri güncellenmek üzere form olarak açılır")
def address_edit_form_prefilled(create_customer_page):
    assert create_customer_page.is_address_edit_form_prefilled_correctly()


@when("kullanıcı adres form penceresini kapatır")
def close_address_form(create_customer_page):
    create_customer_page.click_address_form_cancel()


@when('kullanıcı adres kartındaki "Delete" seçeneğine tıklar')
def click_address_card_delete(create_customer_page):
    create_customer_page.click_address_card_delete()


@then("adres kartı listeden kaldırılır")
def address_card_removed(create_customer_page):
    assert create_customer_page.get_address_card_count() == 0


@then("listede başka kayıtlı adres kalmadığı için İleri butonu tekrar pasif hale gelir")
def address_next_disabled_after_delete(create_customer_page):
    assert create_customer_page.is_address_next_disabled()


@given('kullanıcı "Adres Bilgi" ekranında Şehir, Sokak ve No alanlarını doldurmuştur')
def user_filled_address_form_with_literal_values(create_customer_page):
    create_customer_page.fill_demographic_step_with_faker(gender="Kadın")
    create_customer_page.click_demographic_next()
    create_customer_page.wait_for_address_step()
    create_customer_page.fill_address_form("İstanbul", "Bağdat Caddesi", "45/2", "Ev adresi")


@when('kullanıcı "Save" butonuna tıklar')
def click_save_button(create_customer_page):
    create_customer_page.save_address_form()


@then("adres kart olarak listelenir ve tamamı bina-daire no dahil okunabilir şekilde görüntülenir")
def address_card_fully_readable(create_customer_page):
    assert create_customer_page.are_all_entered_addresses_displayed_as_cards()


@given('kullanıcının "Adres Bilgi" ekranında kayıtlı bir adres kartı bulunmaktadır')
def user_has_saved_address_card(create_customer_page):
    create_customer_page.fill_demographic_step_with_faker(gender="Kadın")
    create_customer_page.click_demographic_next()
    create_customer_page.wait_for_address_step()
    create_customer_page.fill_address_form("İstanbul", "Bağdat Caddesi", "45/2", "Ev adresi")
    create_customer_page.save_address_form()


@when('kullanıcı "Sokak" alanını "Fenerbahçe Caddesi" olarak günceller')
def update_street_field(create_customer_page):
    create_customer_page.update_address_street("Fenerbahçe Caddesi")


@then("adres kartı güncellenmiş bilgilerle listelenir")
def address_card_updated(create_customer_page):
    assert create_customer_page.are_all_entered_addresses_displayed_as_cards()


@when('kullanıcı "Mobile Phone" alanına geçersiz formatta bir değer girer')
def enter_invalid_mobile(create_customer_page):
    create_customer_page.enter_invalid_mobile_phone_format()


@then("sistem geçersiz telefon formatı uyarısını görüntüler")
def invalid_mobile_warning_displayed(create_customer_page):
    assert create_customer_page.is_mobile_phone_error_displayed()


@when('kullanıcı "Mobile Phone" alanını geçerli formatta bir değerle günceller')
def fix_mobile(create_customer_page):
    create_customer_page.fill_mobile_phone_with_faker()


@when(
    "kullanıcı Demografik Bilgi adımındaki zorunlu ve opsiyonel tüm alanları rastgele Faker değerleriyle doldurur",
    target_fixture="demographic_data",
)
def fill_demographic_step_with_all_fields(create_customer_page):
    gender = "Kadın" if fake.boolean() else "Erkek"
    return create_customer_page.fill_demographic_step_with_all_fields_via_faker(gender=gender)


@when(
    "kullanıcı İletişim Kanalı adımındaki zorunlu ve opsiyonel tüm alanları rastgele Faker değerleriyle doldurur",
    target_fixture="contact_data",
)
def fill_contact_step_with_all_fields(create_customer_page):
    return create_customer_page.fill_contact_step_with_all_fields_via_faker()


@then("opsiyonel alanlar dahil girilen tüm bilgiler eksiksiz ve doğru şekilde görüntülenir")
def all_fields_including_optional_displayed_correctly(create_customer_page, demographic_data, contact_data):
    assert create_customer_page.are_optional_fields_displayed_correctly(demographic_data, contact_data)


@when(parsers.parse('"{alan}" alanına 101 karakterlik değer girilmeye çalışılır'))
def attempt_101_chars_in_optional_name_field(create_customer_page, alan):
    create_customer_page._last_optional_name_value = (
        create_customer_page.attempt_to_type_long_value_in_optional_name_field(alan, FIELD_LIMITS["optional_name"] + 1)
    )


@then("alan en fazla 100 karakteri kabul eder")
def optional_name_field_capped_at_100(create_customer_page):
    assert len(create_customer_page._last_optional_name_value) == FIELD_LIMITS["optional_name"]


@when(parsers.parse('"{alan}" alanına tam 100 karakterlik bir değer girilir'))
def enter_exactly_100_chars_in_optional_name_field(create_customer_page, alan):
    create_customer_page._last_optional_name_value = (
        create_customer_page.attempt_to_type_long_value_in_optional_name_field(alan, FIELD_LIMITS["optional_name"])
    )


@then("alan girilen 100 karakterin tamamını kabul eder")
def optional_name_field_accepts_full_100(create_customer_page):
    assert len(create_customer_page._last_optional_name_value) == FIELD_LIMITS["optional_name"]


@when('"Birth Date" alanına geçerli 8 rakamlık bir tarih yazılır')
def type_valid_birth_date(create_customer_page):
    create_customer_page._birth_date_after_8_digits = create_customer_page.type_valid_birth_date_digits()


@then('alan gün, ay, yıl biçiminde tam 10 karakter uzunluğunda bir değer gösterir')
def birth_date_shows_10_char_formatted_value(create_customer_page):
    value = create_customer_page._birth_date_after_8_digits
    assert len(value) == FIELD_LIMITS["birth_date_formatted"], f"Beklenen 10 karakter, gelen: {value!r} ({len(value)} karakter)"
    assert value[2] == "/" and value[5] == "/", f"Beklenen gg/aa/yyyy formatı, gelen: {value!r}"


@when("aynı alana 9. bir rakam yazılmaya çalışılır")
def attempt_9th_digit_in_birth_date(create_customer_page):
    create_customer_page._birth_date_after_9th_digit = create_customer_page.append_extra_digit_to_birth_date()


@then("alanın değeri değişmeden kalır, fazla rakamın hiçbir etkisi olmaz")
def birth_date_value_unchanged_after_overflow(create_customer_page):
    assert create_customer_page._birth_date_after_9th_digit == create_customer_page._birth_date_after_8_digits
