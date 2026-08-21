from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage
from utils.waits import poll_until


class DeleteCustomerPage(BasePage):
    DETAIL_HEADER = (By.CSS_SELECTOR, "[data-testid='customer-detail-header']")
    STATUS_BADGE = (By.CSS_SELECTOR, "[data-testid='status-badge']")
    DELETE_BUTTON = (By.CSS_SELECTOR, "[data-testid='customer-info-delete']")

    CONFIRM_DIALOG = (By.CSS_SELECTOR, "[data-testid='confirm-dialog']")
    CONFIRM_DIALOG_MESSAGE = (By.CSS_SELECTOR, "[data-testid='confirm-dialog-message']")
    CONFIRM_DIALOG_CANCEL = (By.CSS_SELECTOR, "[data-testid='confirm-dialog-cancel']")
    CONFIRM_DIALOG_CONFIRM = (By.CSS_SELECTOR, "[data-testid='confirm-dialog-confirm']")

    NAV_CUSTOMER_SEARCH = (By.CSS_SELECTOR, "[data-testid='nav-customer-search']")
    EMPTY_STATE_MESSAGE = (By.CSS_SELECTOR, "[data-testid='empty-state-message']")

    def __init__(self, driver):
        super().__init__(driver)
        self.wait.until(EC.visibility_of_element_located(self.DETAIL_HEADER))
        self._detail_url = driver.current_url
        self._last_background_click_succeeded = None

    def get_status(self):
        return self.driver.find_element(*self.STATUS_BADGE).text.strip()

    def click_delete(self):
        self.wait.until(EC.element_to_be_clickable(self.DELETE_BUTTON)).click()
        self.wait.until(EC.visibility_of_element_located(self.CONFIRM_DIALOG))

    def is_confirm_dialog_displayed_with_buttons(self):
        message_el = self.driver.find_element(*self.CONFIRM_DIALOG_MESSAGE)
        return (
            self.driver.find_element(*self.CONFIRM_DIALOG).is_displayed()
            and message_el.is_displayed()
            and bool(message_el.text.strip())
            and self.driver.find_element(*self.CONFIRM_DIALOG_CANCEL).is_displayed()
            and self.driver.find_element(*self.CONFIRM_DIALOG_CONFIRM).is_displayed()
        )

    def click_confirm_no(self):
        self.driver.find_element(*self.CONFIRM_DIALOG_CANCEL).click()
        self.wait.until(EC.invisibility_of_element_located(self.CONFIRM_DIALOG))

    def click_confirm_yes(self):
        self.driver.find_element(*self.CONFIRM_DIALOG_CONFIRM).click()

    def is_dialog_open(self):
        dialogs = self.driver.find_elements(*self.CONFIRM_DIALOG)
        return bool(dialogs) and dialogs[0].is_displayed()

    def attempt_background_interaction(self):
        try:
            self.driver.find_element(*self.NAV_CUSTOMER_SEARCH).click()
            self._last_background_click_succeeded = True
        except ElementClickInterceptedException:
            self._last_background_click_succeeded = False

    def did_background_click_succeed(self):
        return self._last_background_click_succeeded

    def get_customer_id(self):
        return self._detail_url.rstrip("/").split("/")[-1]

    def wait_for_redirect_to_search(self):
        self.wait.until(lambda d: d.current_url.rstrip("/").endswith("/customers"))

    def reload_detail_url(self):
        self.driver.get(self._detail_url)

    def is_empty_state_message_displayed(self):
        message_el = self.wait.until(EC.visibility_of_element_located(self.EMPTY_STATE_MESSAGE))
        return bool(message_el.text.strip())

    def wait_for_deleted_customer_not_found_after_reload(self, max_attempts=6, poll_interval_seconds=2):
        def _reload_detail_page():
            self.driver.get(self._detail_url)

        def _customer_not_found():
            if "/login" in self.driver.current_url:
                raise AssertionError(
                    "Beklenmeyen durum: eski detay URL'ine tekrar giden reload'lar sırasında "
                    "oturum sonlandı (login ekranına yönlendirildi) - bu, silinen müşterinin "
                    "'bulunamadı' durumundan FARKLI, ayrı bir bulgu olarak araştırılmalı."
                )
            messages = self.driver.find_elements(*self.EMPTY_STATE_MESSAGE)
            return bool(messages) and messages[0].is_displayed() and bool(messages[0].text.strip())

        return poll_until(
            condition=_customer_not_found,
            action=_reload_detail_page,
            attempts=max_attempts,
            interval=poll_interval_seconds,
        )

    def wait_for_delete_rejected(self):
        try:
            self.wait_for_redirect_to_search()
        except TimeoutException:
            return
        raise AssertionError(
            "Beklenen: aktif ürünü olan müşterinin silinmesi reddedilmeli. "
            "Gerçek: sistem müşteriyi sildi ve Müşteri Arama ekranına yönlendirdi "
            "(bilinen defekt, bkz. bugsbunny.txt madde 17)."
        )

    def capture_status_snapshot(self):
        self._status_before_delete_attempt = self.get_status()

    def is_still_on_customer_info_with_status_unchanged(self):
        return (
            bool(self.driver.find_elements(*self.DETAIL_HEADER))
            and self.driver.find_element(*self.DETAIL_HEADER).is_displayed()
            and self.get_status() == self._status_before_delete_attempt
        )
