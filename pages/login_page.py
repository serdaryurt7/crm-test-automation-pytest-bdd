from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class LoginPage:
    USERNAME_INPUT = (By.CSS_SELECTOR, "[data-testid='login-username']")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "[data-testid='login-password']")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "[data-testid='login-submit']")
    ERROR_MESSAGE = (By.CSS_SELECTOR, "[data-testid='login-error']")
    PASSWORD_TOGGLE = (By.CSS_SELECTOR, "[data-testid='login-password-toggle']")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def open(self, url):
        self.driver.get(url)
        self.wait.until(EC.visibility_of_element_located(self.USERNAME_INPUT))

    def login(self, username, password):
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
        self.wait.until(EC.element_to_be_clickable(self.LOGIN_BUTTON)).click()

    def get_error_message(self):
        return self.wait.until(EC.visibility_of_element_located(self.ERROR_MESSAGE)).text

    def wait_for_error_message_to_disappear(self):
        self.wait.until(EC.invisibility_of_element_located(self.ERROR_MESSAGE))

    def enter_password(self, password):
        self.driver.find_element(*self.PASSWORD_INPUT).send_keys(password)

    def get_password_input_type(self):
        return self.driver.find_element(*self.PASSWORD_INPUT).get_attribute("type")

    def toggle_password_visibility(self):
        # Not: normal .click() bu buton icin calismiyor (buton, input alaninin
        # uzerine mutlak konumlandirilmis, Selenium'un hesapladigi tiklama
        # noktasi input'a denk geliyor olabilir) - JS click guvenilir calisiyor.
        toggle_button = self.wait.until(EC.presence_of_element_located(self.PASSWORD_TOGGLE))
        self.driver.execute_script("arguments[0].click();", toggle_button)

    def enter_long_values(self, length=50):
        long_text = "a" * length
        self.driver.find_element(*self.USERNAME_INPUT).send_keys(long_text)
        self.driver.find_element(*self.PASSWORD_INPUT).send_keys(long_text)

    def get_username_value(self):
        return self.driver.find_element(*self.USERNAME_INPUT).get_attribute("value")

    def get_password_value(self):
        return self.driver.find_element(*self.PASSWORD_INPUT).get_attribute("value")
