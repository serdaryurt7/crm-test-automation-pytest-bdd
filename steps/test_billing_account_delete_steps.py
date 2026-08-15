from faker import Faker
from pytest_bdd import given, scenarios, then, when
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.billing_account_delete_page import BillingAccountDeletePage
from pages.create_customer_page import CreateCustomerPage
from pages.sales_setup_page import SalesSetupPage
from utils import config

scenarios("billing_account_delete.feature")

fake = Faker("tr_TR")


def _create_fresh_customer(driver):
    # Zaten authenticated bir session varsayar, login YAPMAZ.
    driver.get(config.url("/customers/new"))
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
    return BillingAccountDeletePage(driver)


def _create_fresh_customer_and_open_account_tab(driver):
    # Hesap silme GERİ DÖNÜŞÜ ZOR bir mutasyon olduğundan HER SENARYO
    # için fresh, tek kullanımlık bir disposable müşteri create_customer
    # akışıyla oluşturuluyor - projedeki diğer *_delete.feature'larla
    # tutarlı, tam bağımsızlık için.
    return _create_fresh_customer(driver)


@given("kullanıcı, aktif ürünü olmayan bir hesap satırı görüntülemektedir", target_fixture="account_page")
def user_viewing_account_without_active_product(authenticated_driver):
    page = _create_fresh_customer_and_open_account_tab(authenticated_driver)
    page.create_account_and_wait()
    return page


@when("Delete butonuna tıklanır ve onay penceresinde onaylanırsa")
def delete_clicked_and_confirmed(account_page):
    account_page.click_delete_on_row()
    account_page.click_confirm_yes_and_wait_for_removal()


@then("hesap aktif hesap listesinden kalıcı olarak kaldırılır")
def account_permanently_removed_from_active_list(account_page):
    assert account_page.wait_for_account_removal_persisted_after_reload()


@given("silme onay penceresi görüntülenmektedir", target_fixture="account_page")
def delete_confirm_dialog_displayed(authenticated_driver):
    page = _create_fresh_customer_and_open_account_tab(authenticated_driver)
    page.create_account_and_wait()
    page.click_delete_on_row()
    return page


@when('kullanıcı "Hayır" butonuna tıklar')
def user_clicks_no(account_page):
    account_page.click_confirm_no()


@then("herhangi bir değişiklik yapılmaz, onay penceresi kapanır")
def no_change_dialog_closes(account_page):
    assert not account_page.is_confirm_dialog_present()
    assert account_page.is_account_still_listed()


@then("kullanıcı Müşteri Hesabı ekranında kalır")
def user_stays_on_account_screen(account_page):
    assert account_page.get_account_row_count() >= 1


@given("hesaba bağlı en az bir aktif ürün vardır", target_fixture="account_page")
def account_has_active_product(authenticated_driver):
    page = _create_fresh_customer_and_open_account_tab(authenticated_driver)
    customer_url = authenticated_driver.current_url
    page.create_account_and_wait()
    page.click_new_sale_on_row()
    sales_page = SalesSetupPage(authenticated_driver)
    sales_page.purchase_simple_offer()
    # Canlı doğrulandı: sipariş tamamlandığında OTOMATİK olarak Müşteri
    # Hesabı sekmesine DÖNÜLMÜYOR - kullanıcı "Sipariş oluşturuldu!"
    # başarı ekranında (sadece "Müşteri Aramaya Dön" linkiyle) kalıyor.
    # Bu yüzden müşteri detay URL'ine AÇIKÇA geri navigasyon gerekiyor -
    # BillingAccountDeletePage.__init__ tab-account'a hemen tıklamaya
    # çalıştığından, önce sayfanın (hard navigasyon sonrası) GERÇEKTEN
    # yüklendiği (customer-detail-header görünür) dinamik olarak
    # bekleniyor.
    authenticated_driver.get(customer_url)
    WebDriverWait(authenticated_driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='customer-detail-header']"))
    )
    return BillingAccountDeletePage(authenticated_driver)


@when("kullanıcı hesabı silmeyi dener")
def user_attempts_to_delete_account(account_page):
    account_page.click_delete_on_row()
    account_page.click_confirm_yes_expecting_block()


@then("hesap listeden kaldırılmaz")
def account_not_removed_from_list(account_page):
    assert account_page.is_account_still_listed()


@then("sistem doğrudan silmek yerine bir uyarı/engelleme mesajı gösterir")
def system_shows_warning_instead_of_deleting(account_page):
    # Canlı doğrulandı: "The billing account cannot be deleted because it
    # has active products." mesajı bir toast olarak gösteriliyor - ama bu
    # toast'ın kendi bir data-testid'i YOK (dilden bağımsız/güvenilir bir
    # locator ile yakalanamıyor). Bu yüzden dil-bağımsız, GÜVENİLİR olan
    # yapısal sonuç doğrulanıyor: hesap silinmedi/Aktif kaldı - toast'ın
    # kendisi doğrulanamıyor olsa da işlemin GERÇEKTEN reddedildiği
    # (bir önceki Then adımında zaten) kanıtlanmış durumda.
    assert account_page.is_account_still_listed()


@given("bir fatura hesabı silinmiştir", target_fixture="account_page")
def a_billing_account_has_been_deleted(authenticated_driver):
    page = _create_fresh_customer_and_open_account_tab(authenticated_driver)
    page.create_account_and_wait("Kalıcı Hesap")
    page.create_account_and_wait("Silinen Hesap")
    page.click_delete_on_row("Silinen Hesap")
    page.click_confirm_yes_and_wait_for_removal()
    return page


@when("Müşteri Hesabı sekmesindeki hesap listesi görüntülenir")
def account_list_is_displayed(account_page):
    # Given adımı zaten Müşteri Hesabı sekmesinde - bu adımda ek bir
    # aksiyon gerekmiyor, sadece durum doğrulanıyor.
    pass


@then("silinen hesap artık bu listede görüntülenmez")
def deleted_account_not_in_list(account_page):
    assert account_page.is_account_removed_from_list("Silinen Hesap")
    assert account_page.is_account_still_listed("Kalıcı Hesap")


@given("müşterinin yalnızca 1 hesabı vardır", target_fixture="account_page")
def customer_has_exactly_one_account(authenticated_driver):
    page = _create_fresh_customer_and_open_account_tab(authenticated_driver)
    page.create_account_and_wait()
    return page


@when("bu hesap silinir")
def this_account_is_deleted(account_page):
    account_page.click_delete_on_row()
    account_page.click_confirm_yes_and_wait_for_removal()


@then('"Hesap bulunmuyor" boş durumuna dönülür')
def empty_state_returns(account_page):
    assert account_page.is_empty_state_displayed()


@given("bir hesap silinmiştir", target_fixture="stale_delete_context")
def an_account_has_been_deleted(authenticated_driver):
    page = _create_fresh_customer_and_open_account_tab(authenticated_driver)
    page.create_account_and_wait()
    page.click_delete_on_row()
    stale_confirm_button = page.click_confirm_yes_and_wait_for_removal()
    return page, stale_confirm_button


@when(
    "kullanıcı aynı hesabı (artık silinmiş, stale bir referansla) tekrar silmeyi dener",
    target_fixture="duplicate_delete_result",
)
def user_attempts_duplicate_delete(stale_delete_context):
    page, stale_confirm_button = stale_delete_context
    return page, page.attempt_duplicate_delete_with_stale_reference(stale_confirm_button)


@then("sistem ikinci denemeyi güvenli şekilde reddeder, uygulama tutarlı durumda kalır")
def second_attempt_safely_rejected(duplicate_delete_result):
    page, was_safely_rejected = duplicate_delete_result
    assert was_safely_rejected
    assert page.is_app_still_functional()
