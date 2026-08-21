from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.address_add_page import AddressAddPage


class AddressDeletePage(AddressAddPage):

    CONFIRM_DIALOG = (By.CSS_SELECTOR, "[data-testid='confirm-dialog']")

    def open_card_menu(self, index=0):
        menus = self.driver.find_elements(*self.ADDRESS_CARD_MENU)
        menus[index].click()
        self.wait.until(EC.element_to_be_clickable(self.ADDRESS_CARD_EDIT))

    def _get_open_menu_delete_option(self):
        return self.wait.until(EC.presence_of_element_located(self.ADDRESS_CARD_DELETE))

    def is_delete_option_disabled(self, index=0):
        self.open_card_menu(index)
        return not self._get_open_menu_delete_option().is_enabled()

    def attempt_click_disabled_delete_option(self):
        delete_option = self._get_open_menu_delete_option()
        try:
            delete_option.click()
        except (ElementNotInteractableException, ElementClickInterceptedException):
            pass

    def is_confirm_dialog_present(self):
        dialogs = self.driver.find_elements(*self.CONFIRM_DIALOG)
        return bool(dialogs) and dialogs[0].is_displayed()

    def delete_card_at_index(self, index):
        before_count = self.get_card_count()
        self._deleted_title = self.get_all_card_titles()[index]
        self.open_card_menu(index)
        delete_option = self.wait.until(EC.element_to_be_clickable(self.ADDRESS_CARD_DELETE))
        delete_option.click()
        self.wait.until(lambda d: len(d.find_elements(*self.ADDRESS_CARD)) < before_count)
        return delete_option

    def delete_last_added_card(self):
        return self.delete_card_at_index(self.get_card_count() - 1)

    def delete_primary_card(self):
        primary_states = self.get_primary_states()
        primary_index = primary_states.index(True)
        return self.delete_card_at_index(primary_index)

    def is_remaining_address_auto_primary(self):
        return self.get_card_count() == 1 and self.get_primary_states() == [True]

    def wait_for_deletion_persisted_after_reload(self):
        detail_url = self.driver.current_url
        deleted_title = self._deleted_title

        def deletion_persisted(driver):
            driver.get(detail_url)
            self.wait.until(EC.element_to_be_clickable(self.TAB_ADDRESS)).click()
            self.wait.until(EC.visibility_of_element_located(self.ADDRESS_CARD))
            return deleted_title not in self.get_all_card_titles()

        try:
            return self.wait.until(deletion_persisted)
        except TimeoutException:
            return False

    def attempt_duplicate_delete_with_stale_reference(self, stale_delete_button):
        try:
            stale_delete_button.click()
            return False
        except (StaleElementReferenceException, ElementNotInteractableException, ElementClickInterceptedException):
            return True

    def is_app_still_functional(self):
        return bool(self.driver.find_elements(By.TAG_NAME, "body")) and self.get_card_count() >= 1
