from urllib.parse import urlparse

from faker import Faker
from pytest_bdd import given, parsers, scenarios, then, when
from selenium.webdriver.support.ui import WebDriverWait

from pages.address_update_page import AddressUpdatePage
from pages.create_customer_page import CreateCustomerPage
from pages.login_page import LoginPage

scenarios("address_update.feature")

fake = Faker("tr_TR")


@given("kullanıcı bir müşterinin Adres sekmesinde kayıtlı bir adres kartı görüntülemektedir", target_fixture="address_page")
def user_on_customer_address_tab(driver, base_url):
    login_page = LoginPage(driver)
    login_page.open(base_url)
    login_page.login("demo", "Password123")
    WebDriverWait(driver, 10).until(lambda d: "/customers" in d.current_url)

    # Adres güncelleme/silme geri dönüşü zor mutasyonlar barındırdığından
    # (Primary değişikliği, silme vb.) HER SENARYO için fresh, tek
    # kullanımlık bir disposable müşteri create_customer akışıyla
    # oluşturuluyor - update_customer.feature/delete_customer.feature'da
    # kurulan desenle tutarlı, tam bağımsızlık ve tekrarlanabilirlik için.
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

    return AddressUpdatePage(driver)


@when('kullanıcı kart menüsünden "düzenle" seçeneğini seçer')
@given("kullanıcı adres düzenleme formundadır")
def user_clicks_edit_on_card(address_page):
    address_page.click_edit_first_card()


@then("form Şehir, Sokak, Bina No, Açıklama alanlarıyla önceden dolu açılır")
def form_is_prefilled(address_page):
    assert address_page.is_form_prefilled_correctly()


@when("Sokak/Bina No alanları değiştirilip Kaydet'e tıklanır")
def user_updates_street_and_building_then_saves(address_page):
    new_street = fake.street_name()
    new_building_no = fake.building_number()
    address_page.update_street_and_building(new_street, new_building_no)
    address_page.click_save()


@then("kart yeni bilgilerle güncellenir")
def card_shows_new_values(address_page):
    assert address_page.is_card_updated_with_new_values()


@when(parsers.parse('"{alan}" alanı boşaltılır'))
def user_clears_required_field(address_page, alan):
    address_page.clear_required_text_field(alan)


@then("Kaydet butonu pasif kalır")
def save_button_disabled(address_page):
    assert address_page.is_save_button_disabled()


@given("kullanıcı adres düzenleme formunda değişiklik yapmıştır")
def user_makes_changes_in_edit_form(address_page):
    address_page.click_edit_first_card()
    new_street = fake.street_name()
    new_building_no = fake.building_number()
    address_page.update_street_and_building(new_street, new_building_no)


@when("İptal butonuna tıklanır")
def user_clicks_cancel(address_page):
    address_page.click_cancel()


@then("kart eski bilgileriyle kalır")
def card_shows_original_values(address_page):
    assert address_page.is_card_showing_original_values()


@when(parsers.parse("Açıklama alanına {length:d} karakterlik bir metin girilir"), target_fixture="typed_description_value")
def user_types_long_description(address_page, length):
    return address_page.attempt_to_type_long_description(length)


@then("alan girilen metnin tamamını kabul eder")
def field_accepts_full_text(typed_description_value):
    assert len(typed_description_value) == 3000


@then("alan tanımlı karakter sınırını aşan girişi kabul etmez")
def field_rejects_text_beyond_limit(typed_description_value):
    assert len(typed_description_value) < 3000


@given("müşterinin birden fazla adresi vardır")
def customer_has_multiple_addresses(address_page):
    address_page.click_add_address()
    address_page.add_address_with_faker(fake.street_name(), fake.building_number(), fake.sentence(nb_words=4))


@when("kullanıcı ikinci adresi Primary olarak işaretler")
def user_marks_second_address_as_primary(address_page):
    address_page.mark_second_address_as_primary()


@then("yalnızca bu adres Primary görüntülenir, öncekinin işareti anlık olarak kalkar")
def only_second_address_primary(address_page):
    assert address_page.get_primary_states() == [False, True]


@then("sayfa yenilendiğinde de yalnızca ikinci adres Primary olarak kalır")
def primary_persists_after_reload(address_page):
    assert address_page.wait_for_primary_states_to_persist([False, True]) == [False, True]


@then("tek adres otomatik olarak Primary işaretlidir")
@then("değiştirilecek başka bir adres seçeneği bulunmadığından bu işaret değişmez")
def single_address_primary_and_fixed(address_page):
    assert address_page.is_single_address_primary_and_unchangeable()


@then('kart başlığı "Şehir, Sokak, No" formatında ve açıklama eksiksiz görüntülenir')
def card_title_and_detail_well_formed(address_page):
    assert address_page.is_card_title_and_detail_well_formed()
