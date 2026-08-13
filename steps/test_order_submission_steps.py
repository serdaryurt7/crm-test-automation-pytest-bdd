from urllib.parse import urlparse

from pytest_bdd import given, scenarios, then, when
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.billing_account_products_page import BillingAccountProductsPage
from pages.create_customer_page import CreateCustomerPage
from pages.login_page import LoginPage
from pages.offer_selection_page import OfferSelectionPage
from pages.order_submission_page import OrderSubmissionPage
from pages.product_configuration_page import ProductConfigurationPage

scenarios("order_submission.feature")


def _create_fresh_customer_and_open_account_tab(driver, base_url):
    login_page = LoginPage(driver)
    login_page.open(base_url)
    login_page.login("demo", "Password123")
    WebDriverWait(driver, 10).until(lambda d: "/customers" in d.current_url)

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
    return BillingAccountProductsPage(driver)


def _reach_config_screen(driver, base_url, offer_name="Mobil 20GB Paket"):
    account_page = _create_fresh_customer_and_open_account_tab(driver, base_url)
    customer_url = driver.current_url
    account_page.create_account_and_wait()
    account_page.click_new_sale_on_row()
    offer_page = OfferSelectionPage(driver)
    offer_page.select_offer_by_name(offer_name)
    offer_page.click_add_to_cart_and_wait()
    offer_page.click_next_and_wait_for_config()
    return ProductConfigurationPage(driver), customer_url


def _reach_submission_screen(driver, base_url, offer_name="Mobil 20GB Paket"):
    config_page, customer_url = _reach_config_screen(driver, base_url, offer_name)
    config_page.fill_all_required_text_fields_with_dummy_values()
    config_page.click_next_and_wait_for_summary()
    return OrderSubmissionPage(driver), customer_url


def _place_order_from_account_page(driver, offer_name="Mobil 20GB Paket"):
    # UC-014/UC-015'te kurulan AYNI akış - hesap sayfasından başlayıp
    # tam bir sipariş tamamlıyor, benzersizlik gibi tekrarlı senaryolar
    # (TC-016-08) için DRY bir yapı taşı.
    account_page = BillingAccountProductsPage(driver)
    account_page.click_new_sale_on_row()
    offer_page = OfferSelectionPage(driver)
    offer_page.select_offer_by_name(offer_name)
    offer_page.click_add_to_cart_and_wait()
    offer_page.click_next_and_wait_for_config()
    config_page = ProductConfigurationPage(driver)
    config_page.fill_all_required_text_fields_with_dummy_values()
    config_page.click_next_and_wait_for_summary()
    submission_page = OrderSubmissionPage(driver)
    submission_page.click_submit_and_wait_for_success()
    return submission_page.get_order_id()


@given("kullanıcı Ürün Konfigürasyonu adımını tamamlamıştır", target_fixture="config_ready_context")
def config_step_completed(driver, base_url):
    config_page, customer_url = _reach_config_screen(driver, base_url)
    config_page.fill_all_required_text_fields_with_dummy_values()
    assert config_page.is_next_button_enabled()
    return config_page, customer_url


@when("Sipariş Gönder ekranına geçilir", target_fixture="submission_context")
def navigate_to_order_submission_screen(driver, config_ready_context):
    config_page, customer_url = config_ready_context
    config_page.click_next_and_wait_for_summary()
    return OrderSubmissionPage(driver), customer_url


@then("seçilen teklifler, hizmet adresi ve toplam tutar özet olarak görüntülenir")
def summary_shows_offers_address_and_total(submission_context):
    submission_page, _ = submission_context
    assert submission_page.get_summary_line_count() >= 1
    assert submission_page.is_service_address_displayed()
    assert submission_page.get_summary_total_value() > 0


@given("kullanıcı sepete yalnızca bir kez bir teklif eklemiştir", target_fixture="submission_context")
def cart_has_single_offer_added_once(driver, base_url):
    return _reach_submission_screen(driver, base_url)


@then("özet listesinde bu teklif TAM 1 KEZ, doğru toplam tutarla görüntülenmelidir")
def offer_appears_exactly_once_with_correct_total(submission_context):
    # Canlı doğrulandı (UC-014-08 keşfi + bu UC'de 2 ayrı tekrar): "Mobil
    # 20GB Paket" TEK BİR kez sepete eklenip Sipariş Gönder ekranına
    # ilerlendiğinde her seferinde doğru şekilde tek satır/199.90 TL
    # görüntüleniyor - kullanıcının belgelediği "3 kez tekrarlanma" bug'ı
    # bu ortamda 5 denemede de yeniden üretilemedi. Spesifikasyonun DOĞRU/
    # beklenen davranışını assert ediyor - regresyon net'i.
    submission_page, _ = submission_context
    assert submission_page.get_summary_line_count() == 1
    assert submission_page.get_summary_total_value() == 199.90


@given("kullanıcı Sipariş Gönder ekranındadır", target_fixture="submission_context")
def user_on_order_submission_screen(driver, base_url):
    return _reach_submission_screen(driver, base_url)


@when('"Gönder" butonuna tıklanır')
def click_submit_button(submission_context):
    submission_page, _ = submission_context
    submission_page.click_submit_and_wait_for_success()


@then("sipariş oluşturulur, ürünler ilgili fatura hesabına eklenir")
def order_created_and_product_added_to_account(driver, submission_context):
    _, customer_url = submission_context
    driver.get(customer_url)
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='customer-detail-header']"))
    )
    account_page = BillingAccountProductsPage(driver)
    panel_id = account_page.get_products_panel_id()
    assert account_page.get_product_row_count(panel_id) >= 1


@when('"Geri" butonuna tıklanır')
def click_back_button(submission_context):
    submission_page, _ = submission_context
    submission_page.click_back_and_wait_for_config()


@then("Ürün Konfigürasyonu ekranına dönülür ve girilen bilgiler korunur")
def returned_to_config_screen_with_data_preserved(driver):
    fields = driver.find_elements(By.CSS_SELECTOR, "[data-testid='sales-config-field']")
    values = [f.get_attribute("value") for f in fields if f.tag_name == "input"]
    assert values
    assert all(bool(v) for v in values)


@given("kullanıcı siparişi başarıyla göndermiştir", target_fixture="submission_page")
def order_submitted_successfully(driver, base_url):
    submission_page, _ = _reach_submission_screen(driver, base_url)
    submission_page.click_submit_and_wait_for_success()
    return submission_page


@then('"Sipariş oluşturuldu!" başlıklı bir başarı ekranı görüntülenir')
def success_screen_is_displayed(submission_page):
    assert submission_page.is_success_screen_displayed()


@then("bir Sipariş ID'si gösterilir")
def order_id_is_displayed(submission_page):
    assert submission_page.get_order_id()


@when('"Gönder" isteği sırasında bir sunucu/ağ hatası simüle edilir')
def simulate_server_error_during_submit(driver, submission_context):
    # Uygulamanın gerçek bir 500 yanıtını taklit etmek yerine (CDP Fetch
    # domain ile request interception bu proje için gereksiz bir karmaşıklık
    # eklerdi - YAGNI), Chrome DevTools Protocol ile ağ bağlantısı GEÇİCİ
    # olarak kesiliyor - canlı doğrulandı: uygulama bunu da bir gönderim
    # hatası olarak ele alıyor ve "Sipariş gönderilemedi. Lütfen tekrar
    # deneyin." mesajını gösteriyor (sales-submit-error testid'i).
    submission_page, _ = submission_context
    driver.execute_cdp_cmd("Network.enable", {})
    driver.execute_cdp_cmd(
        "Network.emulateNetworkConditions",
        {"offline": True, "latency": 0, "downloadThroughput": -1, "uploadThroughput": -1},
    )
    try:
        submission_page.click_submit_and_wait_for_error()
    finally:
        driver.execute_cdp_cmd(
            "Network.emulateNetworkConditions",
            {"offline": False, "latency": 0, "downloadThroughput": -1, "uploadThroughput": -1},
        )


@then("kullanıcıya anlamlı bir hata mesajı gösterilir")
def meaningful_error_message_is_shown(submission_context):
    submission_page, _ = submission_context
    assert submission_page.is_error_message_displayed_with_text()


@then("yanlış bir başarı yönlendirmesi yapılmaz")
def no_false_success_redirect_happens(submission_context):
    submission_page, _ = submission_context
    assert submission_page.is_still_on_submit_screen_without_success()


@given('"Product Configuration" tamamlanmış ve "Submit Order" ekranı açılmıştır', target_fixture="repeat_order_context")
def config_completed_and_submit_screen_open(driver, base_url):
    _, customer_url = _reach_submission_screen(driver, base_url)
    return driver, customer_url


@when("art arda birden fazla sipariş oluşturulur", target_fixture="collected_order_ids")
def place_multiple_orders_in_a_row(repeat_order_context):
    driver, customer_url = repeat_order_context
    order_ids = []
    submission_page = OrderSubmissionPage(driver)
    submission_page.click_submit_and_wait_for_success()
    order_ids.append(submission_page.get_order_id())
    for _ in range(2):
        driver.get(customer_url)
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='customer-detail-header']"))
        )
        order_ids.append(_place_order_from_account_page(driver))
    return order_ids


@then("her siparişin Order ID'si birbirinden farklıdır")
def each_order_id_is_unique(collected_order_ids):
    assert len(collected_order_ids) == 3
    assert len(set(collected_order_ids)) == 3
