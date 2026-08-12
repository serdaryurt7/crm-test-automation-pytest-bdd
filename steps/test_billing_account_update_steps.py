from urllib.parse import urlparse

from faker import Faker
from pytest_bdd import given, scenarios, then, when
from selenium.webdriver.support.ui import WebDriverWait

from pages.address_add_page import AddressAddPage
from pages.billing_account_update_page import BillingAccountUpdatePage
from pages.create_customer_page import CreateCustomerPage
from pages.login_page import LoginPage

scenarios("billing_account_update.feature")

fake = Faker("tr_TR")


def _create_fresh_customer(driver):
    # Zaten authenticated bir session varsayar, login YAPMAZ.
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
    return BillingAccountUpdatePage(driver)


def _create_fresh_customer_and_open_account_tab(driver, base_url):
    login_page = LoginPage(driver)
    login_page.open(base_url)
    login_page.login("demo", "Password123")
    WebDriverWait(driver, 10).until(lambda d: "/customers" in d.current_url)
    return _create_fresh_customer(driver)


def _create_fresh_customer_with_two_addresses(driver, base_url):
    # ÖNEMLİ: 2. adres, hesap formunun KENDİ "Yeni Adres Ekle" alt-
    # formuyla DEĞİL, Adres sekmesinin kendi (kalıcılığı kanıtlanmış)
    # akışıyla ekleniyor - UC-EACRML-008-05 kurulumunda keşfedildi ki
    # hesap formunun alt-formuyla eklenen adresler GERÇEK adres listesine
    # kalıcı olarak yansımıyor.
    page = _create_fresh_customer_and_open_account_tab(driver, base_url)
    address_page = AddressAddPage(driver)
    address_page.add_new_address_and_wait_for_card(fake.street_name(), fake.building_number(), fake.sentence(nb_words=3))
    return BillingAccountUpdatePage(driver)


@given("kullanıcı Müşteri Hesabı sekmesinde bir hesap satırı görüntülemektedir", target_fixture="account_page")
def user_viewing_account_row(driver, base_url):
    page = _create_fresh_customer_and_open_account_tab(driver, base_url)
    page.create_account_and_wait()
    return page


@when("kullanıcı Edit butonuna tıklar")
def user_clicks_edit(account_page):
    account_page.click_edit_on_row()


@then('"Fatura Hesabını Düzenle" formu mevcut Hesap Adı/Açıklaması/Adres bilgileriyle önceden dolu açılır')
def edit_form_prefilled(account_page):
    assert account_page.is_edit_form_prefilled_correctly()


@given("kullanıcı hesap düzenleme formundadır", target_fixture="account_page")
def user_on_edit_form(driver, base_url):
    page = _create_fresh_customer_with_two_addresses(driver, base_url)
    page.create_account_and_wait()
    page.click_edit_on_row()
    return page


@when("Hesap Adı ve Adres alanları (geçerli değerlerle) güncellenip Kaydet'e tıklanır")
def user_updates_name_and_address_then_saves(account_page):
    new_name = f"Güncel Hesap {fake.random_number(digits=4, fix_len=True)}"
    account_page.update_name_and_switch_address(new_name)
    account_page.click_save_and_wait_for_form_close()


@then("satır listede yeni bilgiyle yenilenir")
def row_refreshed_with_new_info(account_page):
    assert account_page.is_row_showing_updated_name()
    assert account_page.verify_new_address_persisted()


@when("Hesap Adı alanı boşaltılır")
def account_name_field_cleared(account_page):
    account_page.clear_account_name()


@then("ilgili alan hatalı olarak işaretlenir")
def related_field_marked_as_error(account_page):
    assert account_page.is_account_name_error_displayed()


@then("güncelleme gerçekleştirilmez, kullanıcı düzenleme ekranında kalır")
def update_blocked_user_stays_on_edit_screen(account_page):
    assert account_page.is_save_button_disabled()
    assert account_page.is_edit_form_open()


@when("hizmet adresi müşterinin başka bir kayıtlı adresiyle değiştirilir")
def service_address_switched(account_page):
    account_page.switch_to_alternate_address()
    account_page.click_save_and_wait_for_form_close()


@then("kaydedildiğinde hesap yeni adresle ilişkilendirilir")
def account_associated_with_new_address(account_page):
    assert account_page.verify_new_address_persisted()


@given("kullanıcı formda değişiklik yapmıştır", target_fixture="account_page")
def user_made_changes_in_form(driver, base_url):
    page = _create_fresh_customer_and_open_account_tab(driver, base_url)
    page.create_account_and_wait()
    page.click_edit_on_row()
    page.fill_account_name(f"Kaydedilmeyecek {fake.random_number(digits=4, fix_len=True)}")
    return page


@when("İptal butonuna tıklanır")
def user_clicks_cancel(account_page):
    account_page.click_cancel()


@then("hesap bilgileri değişmeden kalır")
def account_info_unchanged(account_page):
    assert not account_page.is_edit_form_open()
    assert account_page.is_row_showing_original_name()
