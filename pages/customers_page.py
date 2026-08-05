from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class CustomersPage:
    # Sayfa başlığı
    PAGE_TITLE = (By.CSS_SELECTOR, "[data-testid='page-title']")
    PAGE_SUBTITLE = (By.CSS_SELECTOR, "[data-testid='page-subtitle']")

    # Arama formu (gerçek HTML id'si olanlar By.ID, olmayanlar data-testid CSS selector)
    SEARCH_FORM = (By.CSS_SELECTOR, "[data-testid='customer-search-form']")
    TYPE_B2C = (By.CSS_SELECTOR, "[data-testid='customer-type-b2c']")
    TYPE_B2B = (By.CSS_SELECTOR, "[data-testid='customer-type-b2b']")
    IDENTITY_NUMBER = (By.ID, "identityNumber")
    CUSTOMER_ID = (By.ID, "customerId")
    ACCOUNT_NUMBER = (By.ID, "accountNumber")
    GSM = (By.ID, "gsm")
    GSM_COUNTRY = (By.CSS_SELECTOR, "[data-testid='customer-search-gsm-country']")
    FIRST_NAME = (By.ID, "firstName")
    LAST_NAME = (By.ID, "lastName")
    ORDER_NUMBER = (By.ID, "orderNumber")
    SEARCH_CLEAR = (By.CSS_SELECTOR, "[data-testid='customer-search-clear']")
    SEARCH_SUBMIT = (By.CSS_SELECTOR, "[data-testid='customer-search-submit']")

    SEARCH_FIELDS = (
        IDENTITY_NUMBER,
        CUSTOMER_ID,
        ACCOUNT_NUMBER,
        GSM,
        FIRST_NAME,
        LAST_NAME,
        ORDER_NUMBER,
    )

    # Sonuç tablosu
    RESULTS_TABLE = (By.CSS_SELECTOR, "[data-testid='customer-results']")
    RESULTS_COUNT = (By.CSS_SELECTOR, "[data-testid='customer-results-count']")
    RESULTS_RANGE = (By.CSS_SELECTOR, "[data-testid='customer-results-range']")
    EMPTY_STATE_MESSAGE = (By.CSS_SELECTOR, "[data-testid='empty-state-message']")
    SORT_CUSTOMER_ID = (By.CSS_SELECTOR, "[data-testid='customer-results-sort-customerId']")
    SORT_FIRST_NAME = (By.CSS_SELECTOR, "[data-testid='customer-results-sort-firstName']")
    SORT_SECOND_NAME = (By.CSS_SELECTOR, "[data-testid='customer-results-sort-secondName']")
    SORT_LAST_NAME = (By.CSS_SELECTOR, "[data-testid='customer-results-sort-lastName']")
    SORT_ROLE = (By.CSS_SELECTOR, "[data-testid='customer-results-sort-role']")
    SORT_NATIONALITY_ID = (By.CSS_SELECTOR, "[data-testid='customer-results-sort-nationalityId']")

    # Sayfalama (sayfa numarası butonları sonuç sayısına göre değiştiği için
    # sabit locator yerine page_button(n) metoduyla dinamik üretiliyor)
    PAGINATION = (By.CSS_SELECTOR, "[data-testid='customer-results-pagination']")
    PREV_PAGE = (By.CSS_SELECTOR, "[data-testid='customer-results-prev-page']")
    NEXT_PAGE = (By.CSS_SELECTOR, "[data-testid='customer-results-next-page']")

    # Satır şablonu: DOM'da her biri sayfadaki satır sayısı kadar (15x) tekrar
    # ediyor, TEK BAŞINA unique DEĞİL - find_elements ile veya bir <tr>
    # WebElement'i üzerinden relative aramada kullanılmalı.
    ROW = (By.CSS_SELECTOR, "[data-testid='customer-row']")
    ROW_LINK = (By.CSS_SELECTOR, "[data-testid='customer-row-link']")
    ROW_FIRST_NAME = (By.CSS_SELECTOR, "[data-testid='customer-row-first-name']")
    ROW_SECOND_NAME = (By.CSS_SELECTOR, "[data-testid='customer-row-second-name']")
    ROW_LAST_NAME = (By.CSS_SELECTOR, "[data-testid='customer-row-last-name']")
    ROW_ROLE = (By.CSS_SELECTOR, "[data-testid='customer-row-role']")
    ROW_IDENTITY = (By.CSS_SELECTOR, "[data-testid='customer-row-identity']")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10, ignored_exceptions=(StaleElementReferenceException,))
        self.wait.until(EC.visibility_of_element_located(self.SEARCH_SUBMIT))
        self._last_identity_number = None
        self._last_customer_id = None

    def is_search_button_disabled(self):
        return not self.driver.find_element(*self.SEARCH_SUBMIT).is_enabled()

    def clear_all_search_fields(self):
        for locator in self.SEARCH_FIELDS:
            field = self.driver.find_element(*locator)
            if field.get_attribute("value"):
                field.clear()

    def page_button(self, page_number):
        return (By.CSS_SELECTOR, f"[data-testid='customer-results-page-{page_number}']")

    def are_all_search_fields_visible(self):
        return all(self.driver.find_element(*locator).is_displayed() for locator in self.SEARCH_FIELDS)

    def are_search_buttons_visible(self):
        return (
            self.driver.find_element(*self.SEARCH_SUBMIT).is_displayed()
            and self.driver.find_element(*self.SEARCH_CLEAR).is_displayed()
        )

    def is_b2c_active(self):
        return self.driver.find_element(*self.TYPE_B2C).get_attribute("aria-pressed") == "true"

    def is_b2b_inactive(self):
        return not self.driver.find_element(*self.TYPE_B2B).is_enabled()

    def try_click_b2b(self):
        self.driver.find_element(*self.TYPE_B2B).click()

    def enter_identity_number(self, value):
        field = self.driver.find_element(*self.IDENTITY_NUMBER)
        field.clear()
        field.send_keys(value)
        self._last_identity_number = value

    def get_identity_number_value(self):
        return self.driver.find_element(*self.IDENTITY_NUMBER).get_attribute("value")

    def submit_search(self):
        self.wait.until(EC.element_to_be_clickable(self.SEARCH_SUBMIT)).click()

    def wait_for_matching_customer(self):
        self.wait.until(
            lambda d: [e.text.strip() for e in d.find_elements(*self.ROW_IDENTITY)] == [self._last_identity_number]
        )

    def wait_for_empty_state_message(self, expected_text):
        self.wait.until(lambda d: d.find_element(*self.EMPTY_STATE_MESSAGE).text == expected_text)

    def enter_customer_id(self, value):
        field = self.driver.find_element(*self.CUSTOMER_ID)
        field.clear()
        field.send_keys(value)
        self._last_customer_id = value

    def wait_for_matching_customer_id(self):
        self.wait.until(
            lambda d: [e.text.strip() for e in d.find_elements(*self.ROW_LINK)] == [self._last_customer_id]
        )

    def get_customer_id_value(self):
        return self.driver.find_element(*self.CUSTOMER_ID).get_attribute("value")

    def enter_gsm(self, value):
        field = self.driver.find_element(*self.GSM)
        field.clear()
        field.send_keys(value)

    def get_gsm_value(self):
        return self.driver.find_element(*self.GSM).get_attribute("value")
