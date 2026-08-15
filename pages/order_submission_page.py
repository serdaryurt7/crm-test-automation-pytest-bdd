import re

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage


class OrderSubmissionPage(BasePage):
    # "İleri" ile Ürün Konfigürasyonu'ndan ulaşılan "Sipariş Gönder" ekranı
    # (özet + gönderim + başarı/hata durumları) - OfferSelectionPage/
    # ProductConfigurationPage/SalesSetupPage ile AYNI "has-a, is-a değil"
    # standalone tasarım kararı.

    STEP_TITLE = (By.CSS_SELECTOR, "[data-testid='sales-step-title']")

    SUMMARY_LINE = (By.CSS_SELECTOR, "[data-testid='sales-summary-line']")
    SUMMARY_LINE_NAME = (By.CSS_SELECTOR, "[data-testid='sales-summary-line-name']")
    SUMMARY_ADDRESS_TITLE = (By.CSS_SELECTOR, "[data-testid='sales-summary-address-title']")
    SUMMARY_ADDRESS_DETAIL = (By.CSS_SELECTOR, "[data-testid='sales-summary-address-detail']")
    SUMMARY_TOTAL = (By.CSS_SELECTOR, "[data-testid='sales-summary-total']")

    BACK_BUTTON = (By.CSS_SELECTOR, "[data-testid='sales-submit-back']")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "[data-testid='sales-submit']")
    SUBMIT_ERROR = (By.CSS_SELECTOR, "[data-testid='sales-submit-error']")

    SUCCESS_TITLE = (By.CSS_SELECTOR, "[data-testid='sales-success-title']")
    ORDER_NUMBER = (By.CSS_SELECTOR, "[data-testid='sales-order-number']")
    BACK_TO_SEARCH = (By.CSS_SELECTOR, "[data-testid='sales-back-to-search']")

    def __init__(self, driver):
        super().__init__(driver)
        self.wait.until(EC.visibility_of_element_located(self.SUMMARY_LINE))

    # --- Özet ---
    def get_summary_line_count(self):
        return len(self.driver.find_elements(*self.SUMMARY_LINE))

    def get_summary_line_names(self):
        return [line.find_element(*self.SUMMARY_LINE_NAME).text.strip() for line in self.driver.find_elements(*self.SUMMARY_LINE)]

    def get_summary_total_value(self):
        text = self.driver.find_element(*self.SUMMARY_TOTAL).text
        return float(text.replace("TL", "").replace(",", "").strip())

    def is_service_address_displayed(self):
        title = self.driver.find_element(*self.SUMMARY_ADDRESS_TITLE).text.strip()
        detail = self.driver.find_element(*self.SUMMARY_ADDRESS_DETAIL).text.strip()
        return bool(title) and bool(detail)

    # --- Navigasyon / gönderim ---
    def click_back_and_wait_for_config(self):
        self.wait.until(EC.element_to_be_clickable(self.BACK_BUTTON)).click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='sales-config-field']")))

    def click_submit_and_wait_for_success(self):
        self.wait.until(EC.element_to_be_clickable(self.SUBMIT_BUTTON)).click()
        self.wait.until(EC.visibility_of_element_located(self.ORDER_NUMBER))

    def click_submit_and_wait_for_error(self):
        self.wait.until(EC.element_to_be_clickable(self.SUBMIT_BUTTON)).click()
        self.wait.until(EC.visibility_of_element_located(self.SUBMIT_ERROR))

    def is_error_message_displayed_with_text(self):
        return bool(self.driver.find_element(*self.SUBMIT_ERROR).text.strip())

    def is_still_on_submit_screen_without_success(self):
        # "yanlış bir başarı yönlendirmesi yapılmaz" - başarı ekranına ait
        # HİÇBİR işaretin (sipariş numarası) mevcut OLMADIĞI, hâlâ özet/
        # gönderim ekranında kalındığı yapısal olarak doğrulanıyor.
        return bool(self.driver.find_elements(*self.SUMMARY_LINE)) and not self.driver.find_elements(*self.ORDER_NUMBER)

    # --- Başarı ekranı ---
    def is_success_screen_displayed(self):
        return bool(self.driver.find_elements(*self.SUCCESS_TITLE)) and bool(self.driver.find_elements(*self.ORDER_NUMBER))

    def get_order_id(self):
        # "Sipariş ID: 87147419" gibi bir metinden dilden bağımsız olarak
        # SADECE rakamlar çıkarılıyor (literal "Sipariş ID:" ön ekine
        # bağımlı kalınmıyor).
        text = self.driver.find_element(*self.ORDER_NUMBER).text
        match = re.search(r"\d+", text)
        return match.group() if match else None
