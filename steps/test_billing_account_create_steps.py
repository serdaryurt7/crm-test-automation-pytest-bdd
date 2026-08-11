from urllib.parse import urlparse

from pytest_bdd import given, parsers, scenarios, then, when
from selenium.webdriver.support.ui import WebDriverWait

from pages.billing_account_create_page import BillingAccountCreatePage
from pages.create_customer_page import CreateCustomerPage
from pages.login_page import LoginPage

scenarios("billing_account_create.feature")

# Canlı doğrulandı: fatura hesapları sayfa başına 4 kayıt gösteriyor -
# sayfalama kontrollerini tetiklemek için bu limiti aşan bir sayı gerekiyor.
PAGE_SIZE = 4


def _create_fresh_customer(driver):
    # Zaten authenticated bir session varsayar, login YAPMAZ - aynı test
    # içinde ikinci bir disposable müşteri gerektiğinde kullanılıyor
    # (contact_update.feature'da kurulan "2. müşteri için re-login YOK"
    # deseniyle tutarlı).
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
    return BillingAccountCreatePage(driver)


def _create_fresh_customer_and_open_account_tab(driver, base_url):
    # Fatura hesabı oluşturma mutasyonlar barındırdığından HER SENARYO
    # için fresh, tek kullanımlık bir disposable müşteri create_customer
    # akışıyla oluşturuluyor - projedeki diğer *_create/*_update
    # feature'larıyla tutarlı, tam bağımsızlık için.
    login_page = LoginPage(driver)
    login_page.open(base_url)
    login_page.login("demo", "Password123")
    WebDriverWait(driver, 10).until(lambda d: "/customers" in d.current_url)
    return _create_fresh_customer(driver)


@given("kullanıcı bir müşterinin Müşteri Hesabı sekmesindedir", target_fixture="account_page")
def user_on_account_tab(driver, base_url):
    return _create_fresh_customer_and_open_account_tab(driver, base_url)


@when('kullanıcı "Yeni Hesap Oluştur" butonuna tıklayıp Hesap Adı ve Adres (hizmet adresi) alanlarını doldurup Oluştur\'a tıklar', target_fixture="created_account_name")
def user_creates_account_with_name_and_address(account_page):
    return account_page.create_account_and_wait()


@then("sistem fatura hesabını kalıcı olarak oluşturur (sayfa yenilense dahi listede görünür)")
def system_persists_account(account_page, created_account_name):
    assert account_page.wait_for_account_persisted_after_reload(created_account_name)


@given("müşterinin hiç kayıtlı fatura hesabı yoktur", target_fixture="account_page")
def customer_has_no_billing_accounts(driver, base_url):
    # Fresh müşteri hiçbir fatura hesabı OLMADAN oluşturuluyor - ek bir
    # adım gerekmiyor.
    return _create_fresh_customer_and_open_account_tab(driver, base_url)


@when("Müşteri Hesabı sekmesi açılır")
@when("Müşteri Hesabı sekmesi görüntülenir")
def account_tab_is_opened():
    # BillingAccountCreatePage.__init__ zaten sekmeyi açıyor - bu adımda
    # ek bir aksiyon gerekmiyor, sadece durum doğrulanıyor. Fixture'a
    # kasıtlı olarak bağlanmıyor - farklı senaryolarda Given adımı
    # farklı fixture'lar üretiyor (account_page / account_context), bu
    # adım her ikisiyle de uyumlu kalması için parametresiz bırakıldı.
    pass


@then("hesap bulunamadı durumunu belirten bir mesaj görüntülenir")
def not_found_message_displayed(account_page):
    assert account_page.is_empty_state_displayed()


@given("kullanıcı hesap oluşturma formundadır", target_fixture="account_page")
def user_on_account_creation_form(driver, base_url):
    page = _create_fresh_customer_and_open_account_tab(driver, base_url)
    page.click_create_account()
    return page


@when("Hesap Adı alanı boşaltılır")
def account_name_field_is_cleared(account_page):
    account_page.clear_account_name()


@then("ilgili alan hatalı olarak işaretlenir")
def related_field_marked_as_error(account_page):
    assert account_page.is_account_name_error_displayed()


@then("Oluştur butonu pasif kalır, fatura hesabı oluşturulmaz")
def save_disabled_and_no_account_created(account_page):
    assert account_page.is_save_button_disabled()
    assert account_page.is_create_form_open()
    assert account_page.get_account_row_count() == 0


@given("müşterinin birden fazla kayıtlı adresi vardır", target_fixture="account_page")
def customer_has_multiple_addresses(driver, base_url):
    page = _create_fresh_customer_and_open_account_tab(driver, base_url)
    page.click_create_account()
    if len(page.get_address_card_titles()) < 2:
        page.add_new_service_address("İkinci Sokak", "2", "ikinci adres açıklaması")
    return page


@when("kullanıcı hesap formunda ikinci adresi hizmet adresi olarak seçer")
def user_selects_second_address_as_service_address(account_page):
    account_page.select_service_address_by_index(1)


@then("seçim formda işaretli görüntülenir")
def selection_marked_in_form(account_page):
    assert account_page.get_address_selection_states() == [False, True]


@when('"Yeni Adres Ekle" ile yeni bir adres eklenir')
def new_address_added_via_button(account_page):
    account_page.add_new_service_address("Yeni Eklenen Sokak", "77", "yeni eklenen açıklama")


@then("yeni adres formda seçili hizmet adresi olarak görüntülenir")
def new_address_shown_as_selected(account_page):
    assert account_page.is_newest_address_selected_as_service_address()


@given("kullanıcı bir fatura hesabı oluşturmuştur", target_fixture="account_context")
def user_has_created_a_billing_account(driver, base_url):
    page = _create_fresh_customer_and_open_account_tab(driver, base_url)
    name = page.create_account_and_wait()
    return page, name


@when("Müşteri Hesabı listesi görüntülenir", target_fixture="account_page")
def account_list_is_displayed(account_context):
    page, _ = account_context
    return page


@then("yeni hesap otomatik üretilmiş bir hesap numarasıyla listelenir")
def new_account_listed_with_generated_number(account_context):
    page, name = account_context
    assert page.is_account_listed_with_generated_number_and_status(name)


@then("hesabın durum bilgisi görüntülenir")
def account_status_displayed(account_context):
    page, name = account_context
    row = page.find_account_row_by_name(name)
    assert row is not None and row.find_element(*page.ACCOUNT_ROW_TOGGLE).is_displayed()


@given("müşterinin zaten bir fatura hesabı vardır", target_fixture="account_context")
def customer_already_has_one_billing_account(driver, base_url):
    page = _create_fresh_customer_and_open_account_tab(driver, base_url)
    first_name = page.create_account_and_wait()
    return page, first_name


@when("ikinci bir hesap daha oluşturulur", target_fixture="account_page")
def second_account_is_created(account_context):
    page, _ = account_context
    page.create_account_and_wait()
    return page


@then("her iki hesap da birbirinden bağımsız ayrı satırlar olarak listelenir")
def both_accounts_listed_independently(account_page):
    assert account_page.get_account_row_count() == 2


@given("kullanıcı formu doldurmuştur", target_fixture="account_page")
def user_filled_the_form(driver, base_url):
    page = _create_fresh_customer_and_open_account_tab(driver, base_url)
    page.click_create_account()
    page.fill_required_fields_with_faker()
    return page


@when("İptal butonuna tıklanır")
def user_clicks_cancel(account_page):
    account_page.click_cancel()


@then("hiçbir hesap oluşturulmaz")
def no_account_created(account_page):
    assert not account_page.is_create_form_open()
    assert account_page.get_account_row_count() == 0


@when(parsers.parse("Hesap Adı alanına {length:d} karakterlik bir metin girilir"), target_fixture="typed_account_name_value")
def user_types_long_account_name(account_page, length):
    return account_page.type_long_account_name(length)


@then("alan girilen metnin tamamını kabul eder")
def field_accepts_full_text(typed_account_name_value):
    assert len(typed_account_name_value) == 2000


@then("alan tanımlı karakter sınırını aşan girişi kabul etmez")
def field_rejects_text_beyond_limit(typed_account_name_value):
    assert len(typed_account_name_value) < 2000


@given("müşteriye ait en az bir fatura hesabı vardır", target_fixture="account_context")
def customer_has_at_least_one_billing_account(driver, base_url):
    page = _create_fresh_customer_and_open_account_tab(driver, base_url)
    name = page.create_account_and_wait()
    return page, name


@then("tablo Hesap Adı, Hesap Numarası, Hesap Tipi ve Durum bilgilerini içeren sütunlarla gösterilir")
def table_shows_defined_columns(account_context):
    page, name = account_context
    assert page.has_defined_columns_for_row(name)


@given("müşteriye ait sayfa başına limiti aşan sayıda fatura hesabı vardır", target_fixture="account_page")
def customer_has_more_accounts_than_page_size(driver, base_url):
    page = _create_fresh_customer_and_open_account_tab(driver, base_url)
    for _ in range(PAGE_SIZE + 1):
        page.create_account_and_wait()
    return page


@then("sayfalama kontrolleri görüntülenir ve doğru çalışır")
def pagination_displayed_and_functional(account_page):
    assert account_page.is_pagination_displayed_and_functional()


@then("hesap tablosu görüntülenmez")
def account_table_not_displayed(account_page):
    assert account_page.is_table_hidden_when_empty()
