import random
import re

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage
from utils.test_data import FIELD_LIMITS
from utils.text import turkish_fold
from utils.waits import poll_until


class CustomersPage(BasePage):
    PAGE_TITLE = (By.CSS_SELECTOR, "[data-testid='page-title']")
    PAGE_SUBTITLE = (By.CSS_SELECTOR, "[data-testid='page-subtitle']")

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

    RESULTS_TABLE = (By.CSS_SELECTOR, "[data-testid='customer-results']")
    RESULTS_COUNT = (By.CSS_SELECTOR, "[data-testid='customer-results-count']")
    RESULTS_RANGE = (By.CSS_SELECTOR, "[data-testid='customer-results-range']")
    EMPTY_STATE = (By.CSS_SELECTOR, "[data-testid='empty-state']")
    EMPTY_STATE_MESSAGE = (By.CSS_SELECTOR, "[data-testid='empty-state-message']")
    CREATE_CUSTOMER_BUTTON = (By.CSS_SELECTOR, "a[data-testid='customer-results-create']")
    SORT_CUSTOMER_ID = (By.CSS_SELECTOR, "[data-testid='customer-results-sort-customerId']")
    SORT_FIRST_NAME = (By.CSS_SELECTOR, "[data-testid='customer-results-sort-firstName']")
    SORT_SECOND_NAME = (By.CSS_SELECTOR, "[data-testid='customer-results-sort-secondName']")
    SORT_LAST_NAME = (By.CSS_SELECTOR, "[data-testid='customer-results-sort-lastName']")
    SORT_ROLE = (By.CSS_SELECTOR, "[data-testid='customer-results-sort-role']")
    SORT_NATIONALITY_ID = (By.CSS_SELECTOR, "[data-testid='customer-results-sort-nationalityId']")

    PAGINATION = (By.CSS_SELECTOR, "[data-testid='customer-results-pagination']")
    PREV_PAGE = (By.CSS_SELECTOR, "[data-testid='customer-results-prev-page']")
    NEXT_PAGE = (By.CSS_SELECTOR, "[data-testid='customer-results-next-page']")

    ROW = (By.CSS_SELECTOR, "[data-testid='customer-row']")
    ROW_LINK = (By.CSS_SELECTOR, "[data-testid='customer-row-link']")
    ROW_FIRST_NAME = (By.CSS_SELECTOR, "[data-testid='customer-row-first-name']")
    ROW_SECOND_NAME = (By.CSS_SELECTOR, "[data-testid='customer-row-second-name']")
    ROW_LAST_NAME = (By.CSS_SELECTOR, "[data-testid='customer-row-last-name']")
    ROW_ROLE = (By.CSS_SELECTOR, "[data-testid='customer-row-role']")
    ROW_IDENTITY = (By.CSS_SELECTOR, "[data-testid='customer-row-identity']")

    SORT_LOCATORS = {
        "Customer ID": SORT_CUSTOMER_ID,
        "Ad": SORT_FIRST_NAME,
        "İkinci Ad": SORT_SECOND_NAME,
        "Soyad": SORT_LAST_NAME,
        "Kimlik No": SORT_NATIONALITY_ID,
    }
    SORT_ROW_VALUE_LOCATORS = {
        "Customer ID": ROW_LINK,
        "Ad": ROW_FIRST_NAME,
        "İkinci Ad": ROW_SECOND_NAME,
        "Soyad": ROW_LAST_NAME,
        "Kimlik No": ROW_IDENTITY,
    }

    CUSTOMER_DETAIL_HEADER = (By.CSS_SELECTOR, "[data-testid='customer-detail-header']")

    def __init__(self, driver):
        super().__init__(driver)
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

    def wait_for_identity_number_length_validation_error(self):
        self.wait.until(lambda d: "11" in d.find_element(*self.EMPTY_STATE_MESSAGE).text)

    def wait_for_no_results_state(self):
        self.wait.until(EC.visibility_of_element_located(self.EMPTY_STATE))
        assert self.get_row_count() == 0, "Sonuç bulunamadı durumu beklenirken hâlâ satırlar görüntüleniyor"

    def wait_for_customer_id_search_to_show_no_results(self, customer_id, max_attempts=6, poll_interval_seconds=2):
        def _search_again():
            self.enter_customer_id(customer_id)
            self.submit_search()

        def _no_results():
            return self.get_row_count() == 0 and bool(self.driver.find_elements(*self.EMPTY_STATE))

        return poll_until(
            condition=_no_results,
            action=_search_again,
            attempts=max_attempts,
            interval=poll_interval_seconds,
        )

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

    def enter_long_first_last_name(self, length=60):
        long_text = "a" * length
        self.driver.find_element(*self.FIRST_NAME).send_keys(long_text)
        self.driver.find_element(*self.LAST_NAME).send_keys(long_text)

    def get_first_name_value(self):
        return self.driver.find_element(*self.FIRST_NAME).get_attribute("value")

    def get_last_name_value(self):
        return self.driver.find_element(*self.LAST_NAME).get_attribute("value")

    def enter_last_name(self, value):
        field = self.driver.find_element(*self.LAST_NAME)
        field.clear()
        field.send_keys(value)

    def wait_for_last_name_results(self, expected_last_name):
        expected = turkish_fold(expected_last_name)
        self.wait.until(
            lambda d: bool(d.find_elements(*self.ROW_LAST_NAME))
            and all(turkish_fold(e.text.strip()) == expected for e in d.find_elements(*self.ROW_LAST_NAME))
        )

    def enter_first_name(self, value):
        field = self.driver.find_element(*self.FIRST_NAME)
        field.clear()
        field.send_keys(value)

    def wait_for_first_name_results(self, expected_first_name):
        expected = turkish_fold(expected_first_name)
        self.wait.until(
            lambda d: bool(d.find_elements(*self.ROW_FIRST_NAME))
            and all(turkish_fold(e.text.strip()) == expected for e in d.find_elements(*self.ROW_FIRST_NAME))
        )

    def wait_for_last_name_results_starting_with(self, prefix):
        folded_prefix = turkish_fold(prefix)
        self.wait.until(
            lambda d: bool(d.find_elements(*self.ROW_LAST_NAME))
            and all(turkish_fold(e.text.strip()).startswith(folded_prefix) for e in d.find_elements(*self.ROW_LAST_NAME))
        )

    def wait_for_first_name_results_starting_with(self, prefix):
        folded_prefix = turkish_fold(prefix)
        self.wait.until(
            lambda d: bool(d.find_elements(*self.ROW_FIRST_NAME))
            and all(turkish_fold(e.text.strip()).startswith(folded_prefix) for e in d.find_elements(*self.ROW_FIRST_NAME))
        )

    def wait_for_results_matching_first_and_last_name(self, first_name_prefix, last_name_prefix):
        folded_first = turkish_fold(first_name_prefix)
        folded_last = turkish_fold(last_name_prefix)
        self.wait.until(
            lambda d: bool(d.find_elements(*self.ROW_LINK))
            and all(turkish_fold(e.text.strip()).startswith(folded_first) for e in d.find_elements(*self.ROW_FIRST_NAME))
            and all(turkish_fold(e.text.strip()).startswith(folded_last) for e in d.find_elements(*self.ROW_LAST_NAME))
        )

    def wait_for_results_matching_first_name_or_customer_id(self, first_name_prefix, customer_id):
        folded_prefix = turkish_fold(first_name_prefix)

        def check(d):
            links = d.find_elements(*self.ROW_LINK)
            firsts = d.find_elements(*self.ROW_FIRST_NAME)
            if not links:
                return False
            matches = [
                turkish_fold(fn.text.strip()).startswith(folded_prefix) or link.text.strip() == customer_id
                for link, fn in zip(links, firsts)
            ]
            return (
                all(matches)
                and any(link.text.strip() == customer_id for link in links)
                and any(turkish_fold(fn.text.strip()).startswith(folded_prefix) for fn in firsts)
            )

        self.wait.until(check)

    def get_row_count(self):
        return len(self.driver.find_elements(*self.ROW))

    def get_result_customer_ids(self):
        return [e.text.strip() for e in self.driver.find_elements(*self.ROW_LINK)]

    def is_customer_id_column_sorted_ascending(self):
        self.wait.until(lambda d: bool(d.find_elements(*self.ROW_LINK)))
        ids = [int(value) for value in self.get_result_customer_ids()]
        assert ids, "Sıralama kontrol edilirken sonuç listesi boştu - hiçbir kayıt doğrulanamadı"
        return ids == sorted(ids)

    def is_pagination_active(self):
        pagination = self.driver.find_elements(*self.PAGINATION)
        next_buttons = self.driver.find_elements(*self.NEXT_PAGE)
        return bool(pagination) and bool(next_buttons) and next_buttons[0].is_enabled()

    def capture_current_page_customer_ids(self):
        self._first_page_ids = set(self.get_result_customer_ids())

    def go_to_next_page(self):
        self.wait.until(EC.element_to_be_clickable(self.NEXT_PAGE)).click()

    def get_next_page_record_comparison(self):
        self.wait.until(
            lambda d: (ids := {e.text.strip() for e in d.find_elements(*self.ROW_LINK)})
            and ids != self._first_page_ids
        )
        next_page_ids = set(self.get_result_customer_ids())
        return {
            "next_page_ids": next_page_ids,
            "overlapping_ids": next_page_ids & self._first_page_ids,
        }

    def is_create_customer_button_visible(self):
        button = self.wait.until(EC.visibility_of_element_located(self.CREATE_CUSTOMER_BUTTON))
        return button.is_displayed() and button.is_enabled()

    def click_create_customer_button(self):
        self.wait.until(EC.element_to_be_clickable(self.CREATE_CUSTOMER_BUTTON)).click()

    def click_customer_row_link(self):
        self._window_handle_count_before_click = len(self.driver.window_handles)
        link = self.wait.until(EC.element_to_be_clickable(self.ROW_LINK))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link)
        link.click()

    def get_customer_detail_navigation_state(self, customer_id):
        """Detaya geçiş sonrası gözlemlenen durumu döndürür - iddia step'te.

        Beklemeler burada KALIYOR (bekleme page katmanının işi); yalnızca
        iddia step'e taşındı.
        """
        self.wait.until(lambda d: f"/customers/{customer_id}" in d.current_url)
        self.wait.until(EC.visibility_of_element_located(self.CUSTOMER_DETAIL_HEADER))
        return {
            "url": self.driver.current_url,
            "window_count": len(self.driver.window_handles),
            "window_count_before_click": self._window_handle_count_before_click,
        }

    def fill_all_search_fields_via_tab_navigation(self):
        identity_number = "".join(random.choices("0123456789", k=FIELD_LIMITS["identity_number"]))
        self.driver.find_element(*self.IDENTITY_NUMBER).click()
        actions = ActionChains(self.driver)
        actions.send_keys(identity_number).send_keys(Keys.TAB)
        actions.send_keys("5").send_keys(Keys.TAB)
        actions.send_keys("1234567890").send_keys(Keys.TAB)
        actions.send_keys(Keys.TAB)
        actions.send_keys("5551234567").send_keys(Keys.TAB)
        actions.send_keys("Ahmet").send_keys(Keys.TAB)
        actions.send_keys("Yilmaz").send_keys(Keys.TAB)
        actions.send_keys("12345678")
        actions.perform()

    def click_clear_button(self):
        self.wait.until(EC.element_to_be_clickable(self.SEARCH_CLEAR)).click()

    def get_all_search_field_values(self):
        """Tüm arama alanlarının o anki değerlerini döndürür - iddia step'te."""
        return {
            locator: self.driver.find_element(*locator).get_attribute("value")
            for locator in self.SEARCH_FIELDS
        }

    def verify_results_reset_to_default(self):
        self.wait.until(lambda d: len(d.find_elements(*self.ROW)) == 15)

    def get_results_count_number(self):
        el = self.wait.until(EC.visibility_of_element_located(self.RESULTS_COUNT))
        match = re.search(r"\d+", el.text)
        assert match, f"RESULTS_COUNT metninde sayı bulunamadı: {el.text!r}"
        return int(match.group())

    def get_results_range_bounds(self):
        total = self.get_results_count_number()
        range_el = self.wait.until(EC.visibility_of_element_located(self.RESULTS_RANGE))
        numbers = [int(n) for n in re.findall(r"\d+", range_el.text)]
        bounds = [n for n in numbers if n != total]
        assert len(bounds) >= 2, (
            f"RESULTS_RANGE metninde beklenen alt/üst sınır sayıları bulunamadı: {range_el.text!r}"
        )
        return min(bounds), max(bounds)

    def is_results_range_consistent_with_row_count(self):
        lower, upper = self.get_results_range_bounds()
        return (upper - lower + 1) == self.get_row_count()

    def capture_sort_column_values(self, column_label):
        locator = self.SORT_ROW_VALUE_LOCATORS[column_label]
        self.wait.until(lambda d: bool(d.find_elements(*locator)))
        return [e.text.strip() for e in self.driver.find_elements(*locator)]

    def click_sort_column(self, column_label):
        locator = self.SORT_LOCATORS[column_label]
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def wait_for_sort_column_values_to_change(self, column_label, previous_values):
        self.wait.until(lambda d: self.capture_sort_column_values(column_label) != previous_values)
