from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage
from utils.test_data import FIELD_LIMITS


class LoginPage(BasePage):
    USERNAME_INPUT = (By.CSS_SELECTOR, "[data-testid='login-username']")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "[data-testid='login-password']")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "[data-testid='login-submit']")
    ERROR_MESSAGE = (By.CSS_SELECTOR, "[data-testid='login-error']")
    PASSWORD_TOGGLE = (By.CSS_SELECTOR, "[data-testid='login-password-toggle']")

    def __init__(self, driver):
        super().__init__(driver)
        self._last_username = None
        self._last_password = None

    def open(self, url):
        self.driver.get(url)
        self.wait.until(EC.visibility_of_element_located(self.USERNAME_INPUT))

    def login(self, username, password):
        self._last_username = username
        self._last_password = password
        username_field = self.driver.find_element(*self.USERNAME_INPUT)
        password_field = self.driver.find_element(*self.PASSWORD_INPUT)
        username_field.clear()
        password_field.clear()
        username_field.send_keys(username)
        password_field.send_keys(password)
        self.wait.until(EC.element_to_be_clickable(self.LOGIN_BUTTON)).click()

    def fill_credentials(self, username, password):
        username_field = self.driver.find_element(*self.USERNAME_INPUT)
        password_field = self.driver.find_element(*self.PASSWORD_INPUT)
        username_field.clear()
        password_field.clear()
        if username:
            username_field.send_keys(username)
        if password:
            password_field.send_keys(password)

    def is_login_button_disabled(self):
        return not self.driver.find_element(*self.LOGIN_BUTTON).is_enabled()

    def click_login_button(self):
        button = self.wait.until(EC.element_to_be_clickable(self.LOGIN_BUTTON))
        self.driver.execute_script(
            """
            const btn = arguments[0];
            window.__loginBtnWasDisabled = false;
            const observer = new MutationObserver(() => {
                if (btn.disabled) { window.__loginBtnWasDisabled = true; }
            });
            observer.observe(btn, { attributes: true, attributeFilter: ['disabled'] });
            """,
            button,
        )
        button.click()

    def was_disabled_during_submit(self):
        return bool(self.driver.execute_script("return window.__loginBtnWasDisabled;"))

    def get_error_message(self):
        return self.wait.until(EC.visibility_of_element_located(self.ERROR_MESSAGE)).text

    def wait_for_error_message_to_disappear(self):
        self.wait.until(EC.invisibility_of_element_located(self.ERROR_MESSAGE))

    def enter_password(self, password):
        self.driver.find_element(*self.PASSWORD_INPUT).send_keys(password)

    def get_password_input_type(self):
        return self.driver.find_element(*self.PASSWORD_INPUT).get_attribute("type")

    def toggle_password_visibility(self):
        toggle_button = self.wait.until(EC.presence_of_element_located(self.PASSWORD_TOGGLE))
        self.driver.execute_script("arguments[0].click();", toggle_button)

    def enter_long_values(self, length=FIELD_LIMITS["username"]):
        long_text = "a" * length
        self.driver.find_element(*self.USERNAME_INPUT).send_keys(long_text)
        self.driver.find_element(*self.PASSWORD_INPUT).send_keys(long_text)

    def get_username_value(self):
        return self.driver.find_element(*self.USERNAME_INPUT).get_attribute("value")

    def get_password_value(self):
        return self.driver.find_element(*self.PASSWORD_INPUT).get_attribute("value")

    def has_unexpected_alert(self):
        try:
            alert = self.driver.switch_to.alert
            alert.accept()
            return True
        except NoAlertPresentException:
            return False

    def is_login_form_displayed(self):
        return bool(self.driver.find_elements(*self.USERNAME_INPUT))

    def is_last_submitted_value_reflected_unescaped(self):
        page = self.driver.page_source
        for value in (self._last_username, self._last_password):
            if value and value in page:
                return True
        return False
