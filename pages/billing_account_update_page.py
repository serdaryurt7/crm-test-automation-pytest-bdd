from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.billing_account_create_page import BillingAccountCreatePage


class BillingAccountUpdatePage(BillingAccountCreatePage):

    ACCOUNT_ROW_EDIT = (By.CSS_SELECTOR, "[data-testid='account-row-edit']")

    def _get_selected_address_title(self):
        titles = self.get_address_card_titles()
        states = self.get_address_selection_states()
        for title, selected in zip(titles, states):
            if selected:
                return title
        return None

    def is_edit_form_open(self):
        return self.is_create_form_open()

    def click_edit_on_row(self, name=None):
        row = self.find_account_row_by_name(name) if name else self.driver.find_elements(*self.ACCOUNT_ROW)[0]
        self._pre_edit_name = row.find_element(*self.ACCOUNT_ROW_NAME).text
        self._current_account_name = self._pre_edit_name
        self.wait.until(EC.element_to_be_clickable(row.find_element(*self.ACCOUNT_ROW_EDIT))).click()
        self.wait.until(EC.visibility_of_element_located(self.ACCOUNT_NAME_INPUT))
        self._pre_edit_description = self.driver.find_element(*self.ACCOUNT_DESCRIPTION_INPUT).get_attribute("value")
        self._pre_edit_selected_address_title = self._get_selected_address_title()

    def is_edit_form_prefilled_correctly(self):
        name_value = self.driver.find_element(*self.ACCOUNT_NAME_INPUT).get_attribute("value")
        description_value = self.driver.find_element(*self.ACCOUNT_DESCRIPTION_INPUT).get_attribute("value")
        return (
            name_value == self._pre_edit_name
            and description_value == self._pre_edit_description
            and self._get_selected_address_title() == self._pre_edit_selected_address_title
        )

    def update_name_and_switch_address(self, new_name):
        self.fill_account_name(new_name)
        self._current_account_name = new_name
        self._switch_to_first_unselected_address()

    def switch_to_alternate_address(self):
        self._switch_to_first_unselected_address()

    def _switch_to_first_unselected_address(self):
        states = self.get_address_selection_states()
        target_index = states.index(False)
        self.select_service_address_by_index(target_index)
        self._expected_service_address_title = self.get_address_card_titles()[target_index]

    def click_save_and_wait_for_form_close(self):
        self.click_save()
        self.wait.until(lambda d: not d.find_elements(*self.ACCOUNT_NAME_INPUT))

    def is_row_showing_updated_name(self):
        return self.find_account_row_by_name(self._current_account_name) is not None

    def is_row_showing_original_name(self):
        return self.find_account_row_by_name(self._pre_edit_name) is not None

    def verify_new_address_persisted(self):
        self.click_edit_on_row(self._current_account_name)
        return self._get_selected_address_title() == self._expected_service_address_title
