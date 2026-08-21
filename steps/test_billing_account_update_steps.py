from pytest_bdd import given, scenarios, then, when

from pages.address_add_page import AddressAddPage
from pages.billing_account_update_page import BillingAccountUpdatePage
from utils.test_data import fake, new_address_args

scenarios("billing_account_update.feature")


@given("kullanıcı Müşteri Hesabı sekmesinde bir hesap satırı görüntülemektedir", target_fixture="account_page")
def user_viewing_account_row(disposable_customer):
    page = BillingAccountUpdatePage(disposable_customer)
    page.create_account_and_wait()
    return page


@when("kullanıcı Edit butonuna tıklar")
def user_clicks_edit(account_page):
    account_page.click_edit_on_row()


@then('"Fatura Hesabını Düzenle" formu mevcut Hesap Adı, Açıklaması, Adres bilgileriyle önceden dolu açılır')
def edit_form_prefilled(account_page):
    assert account_page.is_edit_form_prefilled_correctly()


@given("kullanıcı hesap düzenleme formundadır", target_fixture="account_page")
def user_on_edit_form(disposable_customer):
    AddressAddPage(disposable_customer).add_new_address_and_wait_for_card(
        *new_address_args(nb_words=3)
    )
    page = BillingAccountUpdatePage(disposable_customer)
    page.create_account_and_wait()
    page.click_edit_on_row()
    return page


@when("Hesap Adı ve Adres alanları geçerli değerlerle güncellenip Kaydet'e tıklanır")
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
def user_made_changes_in_form(disposable_customer):
    page = BillingAccountUpdatePage(disposable_customer)
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
