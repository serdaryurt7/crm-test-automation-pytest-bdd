from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage
from utils.text import parse_price, turkish_fold


class OfferSelectionPage(BasePage):

    TAB_CATALOG = (By.CSS_SELECTOR, "[data-testid='sales-tab-catalog']")
    TAB_CAMPAIGN = (By.CSS_SELECTOR, "[data-testid='sales-tab-campaign']")

    CATALOG_SELECT = (By.CSS_SELECTOR, "[data-testid='sales-catalog-select']")
    OFFER_ID_FILTER = (By.CSS_SELECTOR, "[data-testid='sales-offer-id-filter']")
    OFFER_NAME_FILTER = (By.CSS_SELECTOR, "[data-testid='sales-offer-name-filter']")
    OFFER_SEARCH = (By.CSS_SELECTOR, "[data-testid='sales-offer-search']")

    OFFER_ROW = (By.CSS_SELECTOR, "[data-testid='sales-offer-row']")
    OFFER_ROW_ID = (By.CSS_SELECTOR, "[data-testid='sales-offer-row-id']")
    OFFER_ROW_NAME = (By.CSS_SELECTOR, "[data-testid='sales-offer-row-name']")
    OFFER_ROW_PRICE = (By.CSS_SELECTOR, "[data-testid='sales-offer-row-price']")

    ADD_TO_CART = (By.CSS_SELECTOR, "[data-testid='sales-add-to-cart']")

    CART_EMPTY = (By.CSS_SELECTOR, "[data-testid='sales-cart-empty']")
    CART_LINE = (By.CSS_SELECTOR, "[data-testid='sales-cart-line']")
    CART_LINE_NAME = (By.CSS_SELECTOR, "[data-testid='sales-cart-line-name']")
    CART_LINE_TOTAL = (By.CSS_SELECTOR, "[data-testid='sales-cart-line-total']")
    CART_LINE_REMOVE = (By.CSS_SELECTOR, "[data-testid='sales-cart-line-remove']")
    CART_TOTAL = (By.CSS_SELECTOR, "[data-testid='sales-cart-total']")
    CART_CLEAR = (By.CSS_SELECTOR, "[data-testid='sales-cart-clear']")

    OFFER_NEXT = (By.CSS_SELECTOR, "[data-testid='sales-offer-next']")

    CAMPAIGN_ID_FILTER = (By.CSS_SELECTOR, "[data-testid='sales-campaign-id-filter']")
    CAMPAIGN_NAME_FILTER = (By.CSS_SELECTOR, "[data-testid='sales-campaign-name-filter']")
    CAMPAIGN_SEARCH = (By.CSS_SELECTOR, "[data-testid='sales-campaign-search']")
    CAMPAIGN_ROW = (By.CSS_SELECTOR, "[data-testid='sales-campaign-row']")
    CAMPAIGN_ROW_ID = (By.CSS_SELECTOR, "[data-testid='sales-campaign-row-id']")
    CAMPAIGN_ROW_OFFER_NAMES = (By.CSS_SELECTOR, "[data-testid='sales-campaign-row-offer-names']")
    CAMPAIGN_ROW_LIST_PRICE = (By.CSS_SELECTOR, "[data-testid='sales-campaign-row-list-price']")
    CAMPAIGN_ROW_PRICE = (By.CSS_SELECTOR, "[data-testid='sales-campaign-row-price']")


    def __init__(self, driver):
        super().__init__(driver)
        self.wait.until(EC.visibility_of_element_located(self.OFFER_ROW))

    def is_catalog_tab_active_with_offers(self):
        return bool(self.driver.find_elements(*self.TAB_CATALOG)) and self.get_offer_row_count() > 0

    def switch_to_campaign_tab(self):
        self.wait.until(EC.element_to_be_clickable(self.TAB_CAMPAIGN)).click()
        self.wait.until(EC.visibility_of_element_located(self.CAMPAIGN_ROW))

    def get_campaign_rows(self):
        return self.driver.find_elements(*self.CAMPAIGN_ROW)

    def select_campaign_by_index(self, index=0):
        self.get_campaign_rows()[index].click()

    def get_campaign_row_price_value(self, index=0):
        text = self.get_campaign_rows()[index].find_element(*self.CAMPAIGN_ROW_PRICE).text
        return parse_price(text)

    def select_catalog_category(self, category_text):
        before_count = self.get_offer_row_count()
        self.wait.until(EC.element_to_be_clickable(self.CATALOG_SELECT)).click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[role='listbox']")))
        for option in self.driver.find_elements(By.CSS_SELECTOR, "[role='option']"):
            if option.text.strip() == category_text:
                option.click()
                break
        self.wait.until(lambda d: self.get_offer_row_count() != before_count)

    def search_by_name(self, value):
        self.fill(self.OFFER_NAME_FILTER, value)
        self.wait.until(EC.element_to_be_clickable(self.OFFER_SEARCH)).click()
        self.wait.until(lambda d: self._offer_names_match(value))

    def search_by_id(self, value):
        self.fill(self.OFFER_ID_FILTER, value)
        self.wait.until(EC.element_to_be_clickable(self.OFFER_SEARCH)).click()
        self.wait.until(lambda d: self._offer_ids_match(value))

    def _offer_names_match(self, value):
        rows = self.driver.find_elements(*self.OFFER_ROW_NAME)
        if not rows:
            return True
        return all(turkish_fold(value) in turkish_fold(row.text) for row in rows)

    def _offer_ids_match(self, value):
        rows = self.driver.find_elements(*self.OFFER_ROW_ID)
        if not rows:
            return True
        return all(row.text.strip() == value for row in rows)

    def get_offer_rows(self):
        return self.driver.find_elements(*self.OFFER_ROW)

    def get_offer_row_count(self):
        return len(self.get_offer_rows())

    def get_offer_names(self):
        return [row.find_element(*self.OFFER_ROW_NAME).text.strip() for row in self.get_offer_rows()]

    def select_offer_by_name(self, name):
        for row in self.get_offer_rows():
            if row.find_element(*self.OFFER_ROW_NAME).text.strip() == name:
                row.click()
                return row
        raise NoSuchElementException(f"Teklif satırı bulunamadı: {name}")

    def get_offer_price_value_by_name(self, name):
        for row in self.get_offer_rows():
            if row.find_element(*self.OFFER_ROW_NAME).text.strip() == name:
                text = row.find_element(*self.OFFER_ROW_PRICE).text
                return parse_price(text)
        raise NoSuchElementException(f"Teklif satırı bulunamadı: {name}")

    def get_cart_line_count(self):
        return len(self.driver.find_elements(*self.CART_LINE))

    def get_cart_line_names(self):
        return [line.find_element(*self.CART_LINE_NAME).text.strip() for line in self.driver.find_elements(*self.CART_LINE)]

    def get_cart_total_value(self):
        text = self.driver.find_element(*self.CART_TOTAL).text
        return parse_price(text)

    def is_cart_empty(self):
        return self.get_cart_line_count() == 0 and bool(self.driver.find_elements(*self.CART_EMPTY))

    def click_add_to_cart_and_wait(self):
        before_count = self.get_cart_line_count()
        self.wait.until(EC.element_to_be_clickable(self.ADD_TO_CART)).click()
        self.wait.until(lambda d: self.get_cart_line_count() > before_count)

    def click_clear_cart_and_wait(self):
        self.wait.until(EC.element_to_be_clickable(self.CART_CLEAR)).click()
        self.wait.until(lambda d: self.get_cart_line_count() == 0)

    def is_next_button_enabled(self):
        return self.driver.find_element(*self.OFFER_NEXT).is_enabled()

    def click_next_and_wait_for_config(self):
        self.wait.until(EC.element_to_be_clickable(self.OFFER_NEXT)).click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='sales-config-target']")))
