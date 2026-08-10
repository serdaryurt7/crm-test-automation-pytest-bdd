from datetime import datetime

from faker import Faker
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

fake = Faker("tr_TR")


class UpdateCustomerPage:
    DETAIL_HEADER = (By.CSS_SELECTOR, "[data-testid='customer-detail-header']")
    DETAIL_NAME = (By.CSS_SELECTOR, "[data-testid='customer-detail-name']")
    EDIT_BUTTON = (By.CSS_SELECTOR, "[data-testid='customer-info-edit']")
    DELETE_BUTTON = (By.CSS_SELECTOR, "[data-testid='customer-info-delete']")
    SAVE_BUTTON = (By.CSS_SELECTOR, "[data-testid='customer-info-save']")
    CANCEL_BUTTON = (By.CSS_SELECTOR, "[data-testid='customer-info-cancel']")
    SAVE_ERROR = (By.CSS_SELECTOR, "[data-testid='customer-info-save-error']")

    VALUE_FIRST_NAME = (By.CSS_SELECTOR, "[data-testid='customer-info-value-first-name']")
    VALUE_LAST_NAME = (By.CSS_SELECTOR, "[data-testid='customer-info-value-last-name']")
    VALUE_BIRTH_DATE = (By.CSS_SELECTOR, "[data-testid='customer-info-value-birth-date']")
    VALUE_GENDER = (By.CSS_SELECTOR, "[data-testid='customer-info-value-gender']")
    VALUE_IDENTITY_NUMBER = (By.CSS_SELECTOR, "[data-testid='customer-info-value-identity-number']")

    FIRST_NAME_INPUT = (By.CSS_SELECTOR, "[data-testid='customer-info-first-name']")
    LAST_NAME_INPUT = (By.CSS_SELECTOR, "[data-testid='customer-info-last-name']")
    BIRTH_DATE_INPUT = (By.CSS_SELECTOR, "[data-testid='customer-info-birth-date']")
    GENDER_SELECT = (By.CSS_SELECTOR, "[data-testid='customer-info-gender']")
    IDENTITY_NUMBER_INPUT = (By.CSS_SELECTOR, "[data-testid='customer-info-identity-number']")

    REQUIRED_FIELD_LOCATORS = {
        "Ad": FIRST_NAME_INPUT,
        "Soyad": LAST_NAME_INPUT,
    }

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.wait.until(EC.visibility_of_element_located(self.DETAIL_HEADER))
        self._detail_url = driver.current_url
        self._pre_edit_first_name = None
        self._pre_edit_last_name = None
        self._pre_edit_birth_date = None
        self._pre_edit_gender = None
        self._pre_edit_identity_number = None
        self._new_first_name = None

    def get_displayed_first_name(self):
        return self.driver.find_element(*self.VALUE_FIRST_NAME).text

    def get_displayed_last_name(self):
        return self.driver.find_element(*self.VALUE_LAST_NAME).text

    def get_displayed_full_name(self):
        return self.driver.find_element(*self.DETAIL_NAME).text

    def click_edit(self):
        self._pre_edit_first_name = self.get_displayed_first_name()
        self._pre_edit_last_name = self.get_displayed_last_name()
        self._pre_edit_birth_date = self.driver.find_element(*self.VALUE_BIRTH_DATE).text.strip()
        self._pre_edit_gender = self.driver.find_element(*self.VALUE_GENDER).text.strip()
        self._pre_edit_identity_number = self.driver.find_element(*self.VALUE_IDENTITY_NUMBER).text.strip()
        self.wait.until(EC.element_to_be_clickable(self.EDIT_BUTTON)).click()
        self.wait.until(EC.visibility_of_element_located(self.FIRST_NAME_INPUT))

    def is_form_prefilled_correctly(self):
        # Goruntuleme modu tarihi "dd/mm/yyyy" formatinda, <input type="date">
        # ise "yyyy-mm-dd" (ISO) formatinda tutuyor - karsilastirmadan once
        # ayni formata cevriliyor.
        expected_iso_birth_date = datetime.strptime(self._pre_edit_birth_date, "%d/%m/%Y").strftime("%Y-%m-%d")
        actual_birth_date = self.driver.find_element(*self.BIRTH_DATE_INPUT).get_attribute("value")
        selected_gender_text = Select(self.driver.find_element(*self.GENDER_SELECT)).first_selected_option.text.strip()
        return (
            self.driver.find_element(*self.FIRST_NAME_INPUT).get_attribute("value") == self._pre_edit_first_name
            and self.driver.find_element(*self.LAST_NAME_INPUT).get_attribute("value") == self._pre_edit_last_name
            and actual_birth_date == expected_iso_birth_date
            and selected_gender_text == self._pre_edit_gender
            and self.driver.find_element(*self.IDENTITY_NUMBER_INPUT).get_attribute("value") == self._pre_edit_identity_number
        )

    def is_read_only_view_mode(self):
        return self.driver.execute_script("return document.querySelectorAll('input, select').length;") == 0

    def is_edit_icon_visible(self):
        return self.driver.find_element(*self.EDIT_BUTTON).is_displayed()

    def is_delete_icon_visible(self):
        return self.driver.find_element(*self.DELETE_BUTTON).is_displayed()

    def click_cancel(self):
        self.wait.until(EC.element_to_be_clickable(self.CANCEL_BUTTON)).click()

    def is_view_showing_original_values(self):
        return (
            self.is_read_only_view_mode()
            and self.get_displayed_first_name() == self._pre_edit_first_name
            and self.get_displayed_last_name() == self._pre_edit_last_name
        )

    def attempt_to_type_long_value(self, field_label, length):
        locator = self.REQUIRED_FIELD_LOCATORS[field_label]
        field = self.driver.find_element(*locator)
        field.click()
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACK_SPACE)
        field.send_keys("a" * length)
        return field.get_attribute("value")

    def update_identity_number(self, new_value):
        field = self.driver.find_element(*self.IDENTITY_NUMBER_INPUT)
        field.click()
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACK_SPACE)
        field.send_keys(new_value)

    def get_save_error_text(self):
        return self.wait.until(EC.visibility_of_element_located(self.SAVE_ERROR)).text

    def is_save_error_displayed(self):
        return bool(self.driver.find_elements(*self.SAVE_ERROR)) and self.driver.find_element(*self.SAVE_ERROR).is_displayed()

    def attempt_xss_in_first_name(self):
        # Not: login.feature'daki SQL Injection/XSS senaryosunda oldugu gibi
        # native alert() gorulmesi tek basina yeterli degil - bu alanda
        # gozlenen ASIL davranis input'un ozel karakterleri (< > ( ) / 1 vb.)
        # yaziliken FILTRELEMESI, HTML kacislama degil.
        field = self.driver.find_element(*self.FIRST_NAME_INPUT)
        field.click()
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACK_SPACE)
        field.send_keys("<script>alert(1)</script>")
        return field.get_attribute("value")

    def has_unexpected_alert(self):
        try:
            alert = self.driver.switch_to.alert
            alert.accept()
            return True
        except NoAlertPresentException:
            return False

    def clear_required_field(self, field_label):
        # Not: .clear() Angular'in reaktif form durumunu (ve dolayisiyla
        # Kaydet butonunun disabled durumunu) guvenilir tetiklemiyor -
        # gercek kullanici tus vurusunu simule etmek icin CTRL+A + BACKSPACE
        # kullaniliyor (projenin genel .clear() pitfall konvansiyonuyla tutarli).
        locator = self.REQUIRED_FIELD_LOCATORS[field_label]
        field = self.driver.find_element(*locator)
        field.click()
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACK_SPACE)

    def is_save_button_disabled(self):
        return not self.driver.find_element(*self.SAVE_BUTTON).is_enabled()

    def update_first_name_with_faker(self):
        self._new_first_name = fake.first_name()
        field = self.driver.find_element(*self.FIRST_NAME_INPUT)
        field.clear()
        field.send_keys(self._new_first_name)

    def click_save(self):
        self.wait.until(EC.element_to_be_clickable(self.SAVE_BUTTON)).click()

    def is_new_first_name_reflected(self):
        self.wait.until(lambda d: self._new_first_name in self.get_displayed_full_name())
        return self._new_first_name in self.get_displayed_full_name()

    def reload_and_verify_first_name_persisted(self):
        # Zone.js, Angular'in kendi XHR/fetch sarmalayicisini bizim
        # execute_script ile enjekte ettigimiz interceptor'dan ONCE
        # kuruyor - bu yuzden PUT isteginin govdesini/URL'ini dogrudan
        # yakalamak guvenilir calismiyor. Bunun yerine gercek backend
        # kalicilik kaniti olarak TAMAMEN YENI bir navigasyonla (hard
        # reload) sayfayi yeniden yukleyip degerin hala orada olup
        # olmadigini kontrol ediyoruz - sadece client-side state olsaydi
        # bu reload'da kaybolurdu.
        self.driver.get(self._detail_url)
        self.wait.until(EC.visibility_of_element_located(self.DETAIL_HEADER))
        return self._new_first_name in self.get_displayed_full_name()
