from pytest_bdd import given, scenarios, then, when
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.billing_account_delete_page import BillingAccountDeletePage
from pages.create_customer_page import CreateCustomerPage
from pages.delete_customer_page import DeleteCustomerPage
from pages.language_switcher_page import LanguageSwitcherPage
from pages.sales_setup_page import SalesSetupPage
from pages.search_customers_page import CustomersPage
from utils import config

scenarios("delete_customer.feature")


@given("kullanıcı silinecek müşterinin Müşteri Bilgisi ekranındadır", target_fixture="delete_customer_page")
def user_on_customer_to_delete_info_screen(authenticated_driver):
    # Silme (Evet ile onaylanan) GERİ DÖNÜŞÜ OLMAYAN bir mutasyon -
    # canlı doğrulandı: müşteri sonrasında hem arama sonuçlarından hem
    # de doğrudan URL erişiminden tamamen kayboluyor. Sabit bir müşteri
    # ID'si kullanmak, suite'in İKİNCİ çalıştırmasında "müşteri zaten
    # silinmiş, bulunamıyor" hatasıyla TÜM senaryoları bozardı - bu
    # yüzden her senaryo için HER SEFERİNDE fresh, tek kullanımlık bir
    # disposable müşteri create_customer akışıyla oluşturuluyor.
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

    return DeleteCustomerPage(authenticated_driver)


@when("kullanıcı Delete ikonuna tıklar")
@given("onay penceresi görüntülenmektedir")
def user_clicks_delete_icon(delete_customer_page):
    delete_customer_page.click_delete()


@then("onay penceresi, silme mesajı ve Evet, Hayır butonlarıyla birlikte görüntülenir")
def confirm_dialog_displayed(delete_customer_page):
    assert delete_customer_page.is_confirm_dialog_displayed_with_buttons()


@when('kullanıcı "Hayır" butonuna tıklar')
def user_clicks_no(delete_customer_page):
    delete_customer_page.click_confirm_no()


@then("pencere kapanır")
def dialog_closes(delete_customer_page):
    assert not delete_customer_page.is_dialog_open()


@then("müşteri kaydı hiçbir şekilde değiştirilmeden ekranda kalmaya devam eder")
def customer_unchanged(delete_customer_page):
    assert delete_customer_page.get_status() == "Aktif"


@when("kullanıcı arka plandaki herhangi bir alanla etkileşime girmeyi dener")
def user_attempts_background_interaction(delete_customer_page):
    delete_customer_page.attempt_background_interaction()


@then("pencere modal davranışı gösterip arka planı engeller")
def modal_blocks_background(delete_customer_page):
    assert not delete_customer_page.did_background_click_succeed()
    assert delete_customer_page.is_dialog_open()


@when('kullanıcı "Evet" butonuna tıklar')
def user_clicks_yes(delete_customer_page):
    delete_customer_page.click_confirm_yes()


@then("kullanıcı Müşteri Arama ekranına yönlendirilir")
def redirected_to_search(delete_customer_page):
    delete_customer_page.wait_for_redirect_to_search()


@then("silinen müşteri arama sonuçlarında artık görüntülenmez")
def deleted_customer_not_in_search_results(delete_customer_page, driver):
    customer_id = delete_customer_page.get_customer_id()
    delete_customer_page.wait_for_redirect_to_search()
    customers_page = CustomersPage(driver)
    assert customers_page.wait_for_customer_id_search_to_show_no_results(customer_id)


@then('silinen müşterinin eski detay ekranına doğrudan gidildiğinde bir "bulunamadı" durumu görüntülenir')
def deleted_customer_direct_url_shows_error(delete_customer_page):
    delete_customer_page.wait_for_redirect_to_search()
    assert delete_customer_page.wait_for_deleted_customer_not_found_after_reload()


@given(
    "görüntülenen müşteriye ait, bir fatura hesabına bağlı en az bir aktif ürün kaydı vardır",
    target_fixture="delete_customer_page",
)
def customer_has_active_product(delete_customer_page, driver):
    # Background zaten boş/disposable bir müşteri oluşturup Müşteri Bilgisi
    # ekranına yerleştirdi (delete_customer_page fixture'ı) - bu adım ONUN
    # ÜZERİNE, billing_account_delete_page.py'deki TC-012-03 önkoşuluyla
    # (account_has_active_product) AYNI minimal satın alma deseniyle bir
    # fatura hesabı + gerçek aktif ürün ekliyor. Orchestration (birden
    # fazla page object'in birlikte kullanımı) bilinçli olarak burada,
    # step katmanında tutuluyor.
    customer_url = delete_customer_page._detail_url

    billing_page = BillingAccountDeletePage(driver)
    billing_page.create_account_and_wait()
    billing_page.click_new_sale_on_row()
    sales_page = SalesSetupPage(driver)
    sales_page.purchase_simple_offer()

    # Sipariş tamamlandığında OTOMATİK olarak Müşteri Bilgisi ekranına
    # dönülmüyor (başarı ekranında kalınıyor, bkz. order_submission.md
    # TC-016-05) - müşteri detay URL'ine açıkça geri dönülüyor.
    driver.get(customer_url)
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='customer-detail-header']"))
    )
    return DeleteCustomerPage(driver)


@given("kullanıcı arayüz dilini İngilizce olarak ayarlamıştır")
def user_switches_language_to_english(delete_customer_page, driver):
    # TEK senaryo, TR/EN'i AYNI ANDA destekler: aşağıdaki Then adımları
    # literal Türkçe (veya İngilizce) metinle KARŞILAŞTIRMIYOR, yalnızca
    # yapısal durumu (URL, "değişmedi mi") doğruluyor - bu yüzden akışın
    # BİLEREK İngilizce arayüzde çalıştırılması, kontrolün gizliden
    # Türkçe metne bağımlı OLMADIĞININ pratik kanıtı (bağımlı olsaydı bu
    # çalıştırma kırılırdı). Aynı mekanizma varsayılan (TR) arayüzde de
    # değişmeden geçerlidir.
    language_page = LanguageSwitcherPage(driver)
    language_page.open_panel()
    language_page.select_language("en")
    # Silme denemesinden HEMEN ÖNCEKİ durumun (artık İngilizce arayüzde
    # okunan) anlık görüntüsü alınıyor - "değişmedi mi" karşılaştırması bu
    # referansa göre yapılacak (bkz. capture_status_snapshot dilden
    # bağımsızlık gerekçesi, delete_customer_page.py).
    delete_customer_page.capture_status_snapshot()


@then("sistem müşteriyi silmeyi reddeder")
def system_rejects_deletion(delete_customer_page):
    delete_customer_page.wait_for_delete_rejected()


@then("kullanıcı Müşteri Bilgisi ekranında kalır, müşteri durumu değişmeden kalır")
def customer_status_unchanged_on_info_screen(delete_customer_page):
    assert delete_customer_page.is_still_on_customer_info_with_status_unchanged()
