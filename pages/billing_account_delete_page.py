from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.billing_account_create_page import BillingAccountCreatePage


class BillingAccountDeletePage(BillingAccountCreatePage):

    ACCOUNT_ROW_DELETE = (By.CSS_SELECTOR, "[data-testid='account-row-delete']")
    NEW_SALE_BUTTON = (By.CSS_SELECTOR, "[data-testid='account-new-sale']")

    CONFIRM_DIALOG = (By.CSS_SELECTOR, "[data-testid='confirm-dialog']")
    CONFIRM_DIALOG_MESSAGE = (By.CSS_SELECTOR, "[data-testid='confirm-dialog-message']")
    CONFIRM_DIALOG_CANCEL = (By.CSS_SELECTOR, "[data-testid='confirm-dialog-cancel']")
    CONFIRM_DIALOG_CONFIRM = (By.CSS_SELECTOR, "[data-testid='confirm-dialog-confirm']")

    def click_new_sale_on_row(self):
        self.wait.until(EC.element_to_be_clickable(self.NEW_SALE_BUTTON)).click()

    def click_delete_on_row(self, name=None):
        row = self.find_account_row_by_name(name) if name else self.driver.find_elements(*self.ACCOUNT_ROW)[0]
        self._deleted_account_name = row.find_element(*self.ACCOUNT_ROW_NAME).text
        row.find_element(*self.ACCOUNT_ROW_DELETE).click()
        self.wait.until(EC.visibility_of_element_located(self.CONFIRM_DIALOG))

    def is_confirm_dialog_present(self):
        dialogs = self.driver.find_elements(*self.CONFIRM_DIALOG)
        return bool(dialogs) and dialogs[0].is_displayed()

    def click_confirm_no(self):
        self.wait.until(EC.element_to_be_clickable(self.CONFIRM_DIALOG_CANCEL)).click()
        self.wait.until(EC.invisibility_of_element_located(self.CONFIRM_DIALOG))

    def click_confirm_yes_and_wait_for_removal(self):
        before_count = self.get_account_row_count()
        confirm_button = self.wait.until(EC.element_to_be_clickable(self.CONFIRM_DIALOG_CONFIRM))
        confirm_button.click()
        self.wait.until(
            lambda d: len(d.find_elements(*self.ACCOUNT_ROW)) < before_count or d.find_elements(*self.EMPTY_STATE_MESSAGE)
        )
        return confirm_button

    def click_confirm_yes_expecting_block(self):
        self.wait.until(EC.element_to_be_clickable(self.CONFIRM_DIALOG_CONFIRM)).click()
        self.wait.until(EC.invisibility_of_element_located(self.CONFIRM_DIALOG))

    def is_account_still_listed(self, name=None):
        target = name or self._deleted_account_name
        return self.find_account_row_by_name(target) is not None

    def is_account_removed_from_list(self, name=None):
        target = name or self._deleted_account_name
        return self.find_account_row_by_name(target) is None

    def wait_for_account_removal_persisted_after_reload(self, name=None):
        target = name or self._deleted_account_name
        detail_url = self.driver.current_url

        def removed_after_reload(driver):
            driver.get(detail_url)
            self.wait.until(EC.element_to_be_clickable(self.TAB_ACCOUNT)).click()
            self.wait.until(lambda d: d.find_elements(*self.ACCOUNT_ROW) or d.find_elements(*self.EMPTY_STATE_MESSAGE))
            return self.find_account_row_by_name(target) is None

        try:
            return self.wait.until(removed_after_reload)
        except TimeoutException:
            return False

    def attempt_duplicate_delete_with_stale_reference(self, stale_confirm_button):
        try:
            stale_confirm_button.click()
            return False
        except (StaleElementReferenceException, ElementNotInteractableException, ElementClickInterceptedException):
            return True

    def is_app_still_functional(self):
        return bool(self.driver.find_elements(By.TAG_NAME, "body")) and (
            bool(self.driver.find_elements(*self.ACCOUNT_ROW)) or bool(self.driver.find_elements(*self.EMPTY_STATE_MESSAGE))
        )
