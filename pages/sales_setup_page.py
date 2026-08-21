import random

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage
from pages.offer_selection_page import OfferSelectionPage
from utils.test_data import SIMPLE_OFFER_SEARCH_TERM


class SalesSetupPage(BasePage):

    CONFIG_TARGET = (By.CSS_SELECTOR, "[data-testid='sales-config-target']")
    CONFIG_FIELD = (By.CSS_SELECTOR, "[data-testid='sales-config-field']")
    CONFIG_NEXT = (By.CSS_SELECTOR, "[data-testid='sales-config-next']")
    SUBMIT = (By.CSS_SELECTOR, "[data-testid='sales-submit']")
    SUCCESS_TITLE = (By.CSS_SELECTOR, "[data-testid='sales-success-title']")

    def purchase_simple_offer(self, offer_name_contains=SIMPLE_OFFER_SEARCH_TERM):
        offer_page = OfferSelectionPage(self.driver)
        for row in offer_page.get_offer_rows():
            if offer_name_contains in row.text:
                row.click()
                break
        offer_page.click_add_to_cart_and_wait()
        offer_page.click_next_and_wait_for_config()

        self.wait.until(EC.visibility_of_element_located(self.CONFIG_TARGET))
        fields = self.driver.find_elements(*self.CONFIG_FIELD)
        for index, field in enumerate(fields):
            value = "5" + "".join(random.choices("0123456789", k=9)) if index == 0 else "".join(random.choices("0123456789", k=6))
            field.send_keys(value)
        self.wait.until(lambda d: d.find_element(*self.CONFIG_NEXT).is_enabled())
        self.driver.find_element(*self.CONFIG_NEXT).click()

        self.wait.until(EC.visibility_of_element_located(self.SUBMIT))
        self.driver.find_element(*self.SUBMIT).click()
        self.wait.until(EC.visibility_of_element_located(self.SUCCESS_TITLE))
