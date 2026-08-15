from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage
from utils.test_data import fake


class ContactUpdatePage(BasePage):
    TAB_CONTACT = (By.CSS_SELECTOR, "[data-testid='tab-contact']")
    EDIT_BUTTON = (By.CSS_SELECTOR, "[data-testid='customer-contact-edit']")

    VALUE_EMAIL = (By.CSS_SELECTOR, "[data-testid='customer-contact-value-email']")
    VALUE_HOME_PHONE = (By.CSS_SELECTOR, "[data-testid='customer-contact-value-home-phone']")
    VALUE_MOBILE_PHONE = (By.CSS_SELECTOR, "[data-testid='customer-contact-value-mobile-phone']")
    VALUE_FAX = (By.CSS_SELECTOR, "[data-testid='customer-contact-value-fax']")

    EMAIL_INPUT = (By.CSS_SELECTOR, "[data-testid='customer-contact-email']")
    HOME_PHONE_INPUT = (By.CSS_SELECTOR, "[data-testid='customer-contact-home-phone']")
    HOME_PHONE_COUNTRY = (By.CSS_SELECTOR, "[data-testid='customer-contact-home-phone-country']")
    MOBILE_PHONE_INPUT = (By.CSS_SELECTOR, "[data-testid='customer-contact-mobile-phone']")
    MOBILE_PHONE_COUNTRY = (By.CSS_SELECTOR, "[data-testid='customer-contact-country-code']")
    FAX_INPUT = (By.CSS_SELECTOR, "[data-testid='customer-contact-fax']")
    FAX_COUNTRY = (By.CSS_SELECTOR, "[data-testid='customer-contact-fax-country']")
    CANCEL_BUTTON = (By.CSS_SELECTOR, "[data-testid='customer-contact-cancel']")
    SAVE_BUTTON = (By.CSS_SELECTOR, "[data-testid='customer-contact-save']")

    EMAIL_ERROR = (By.CSS_SELECTOR, "[data-testid='contact-email-error']")
    MOBILE_PHONE_ERROR = (By.CSS_SELECTOR, "[data-testid='contact-mobile-error']")

    # Home Phone/Fax bilerek dışarıda bırakıldı - opsiyonel alanlar,
    # "boşaltıldığında hata verir" beklentisi yapısal olarak geçerli değil.
    REQUIRED_FIELD_LOCATORS = {
        "Email": EMAIL_INPUT,
        "Mobile Phone": MOBILE_PHONE_INPUT,
    }
    REQUIRED_FIELD_ERROR_LOCATORS = {
        "Email": EMAIL_ERROR,
        "Mobile Phone": MOBILE_PHONE_ERROR,
    }

    # TC-009-13/009-15 için: 3 telefon alanı (Mobile Phone zorunlu,
    # Home Phone/Fax opsiyonel) AYNI "en fazla 10 hane" input-seviyesi
    # kısıtlamasını paylaşıyor - REQUIRED_FIELD_LOCATORS ile AYNI dinamik
    # eşleme deseni, ama üçüncü (opsiyonel) alanları da kapsıyor.
    ALL_PHONE_FIELD_LOCATORS = {
        "Mobile Phone": MOBILE_PHONE_INPUT,
        "Home Phone": HOME_PHONE_INPUT,
        "Fax": FAX_INPUT,
    }

    def __init__(self, driver):
        super().__init__(driver)
        self.driver.find_element(*self.TAB_CONTACT).click()
        self.wait.until(EC.visibility_of_element_located(self.EDIT_BUTTON))
        self._pre_edit_email = None
        self._pre_edit_home_phone = None
        self._pre_edit_mobile_phone = None
        self._pre_edit_fax = None
        self._new_email = None
        self._new_mobile_phone = None

    def get_displayed_email(self):
        return self.driver.find_element(*self.VALUE_EMAIL).text

    def get_displayed_home_phone(self):
        return self.driver.find_element(*self.VALUE_HOME_PHONE).text

    def get_displayed_mobile_phone(self):
        return self.driver.find_element(*self.VALUE_MOBILE_PHONE).text

    def get_displayed_fax(self):
        return self.driver.find_element(*self.VALUE_FAX).text

    def is_view_mode_readonly_with_edit_icon(self):
        # Dilden/içerikten bağımsız yapısal kontrol: düzenleme alanları
        # (input) DOM'da yok VE Edit ikonu görünür durumda.
        return not self.is_edit_form_open() and self.driver.find_element(*self.EDIT_BUTTON).is_displayed()

    def click_edit(self):
        self._pre_edit_email = self.get_displayed_email()
        self._pre_edit_home_phone = self.get_displayed_home_phone()
        self._pre_edit_mobile_phone = self.get_displayed_mobile_phone()
        self._pre_edit_fax = self.get_displayed_fax()
        self.wait.until(EC.element_to_be_clickable(self.EDIT_BUTTON)).click()
        self.wait.until(EC.visibility_of_element_located(self.EMAIL_INPUT))

    def is_edit_form_open(self):
        return bool(self.driver.find_elements(*self.EMAIL_INPUT))

    def update_email(self, new_email):
        field = self.driver.find_element(*self.EMAIL_INPUT)
        field.click()
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACK_SPACE)
        field.send_keys(new_email)
        field.send_keys(Keys.TAB)
        self._new_email = new_email

    def update_mobile_phone(self, new_value):
        field = self.driver.find_element(*self.MOBILE_PHONE_INPUT)
        field.click()
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACK_SPACE)
        field.send_keys(new_value)
        field.send_keys(Keys.TAB)
        self._new_mobile_phone = new_value

    def update_email_and_mobile_with_faker(self):
        email = f"{fake.user_name()}.{fake.random_number(digits=6, fix_len=True)}@example.com"
        mobile = fake.numerify("5#########")
        self.update_email(email)
        self.update_mobile_phone(mobile)
        return email, mobile

    def click_save(self):
        self.wait.until(EC.element_to_be_clickable(self.SAVE_BUTTON)).click()

    def click_cancel(self):
        self.wait.until(EC.element_to_be_clickable(self.CANCEL_BUTTON)).click()

    def is_save_button_disabled(self):
        return not self.driver.find_element(*self.SAVE_BUTTON).is_enabled()

    def is_new_values_reflected(self):
        self.wait.until(lambda d: self._new_email in self.get_displayed_email())
        return self._new_email in self.get_displayed_email() and self._new_mobile_phone in self.get_displayed_mobile_phone()

    def is_view_showing_original_values(self):
        return not self.is_edit_form_open() and self.get_displayed_email() == self._pre_edit_email

    def enter_invalid_email_format(self):
        invalid_email = "gecersiz-email-format"
        self.update_email(invalid_email)
        return invalid_email

    def _is_error_displayed(self, locator):
        # Mesaj metni dile göre değişebileceğinden (gerçek uygulamada
        # Türkçe "Geçerli bir e-posta girin..." çıkıyor, manuel case'in
        # beklediği İngilizce metinle birebir aynı değil) yapısal olarak
        # (hata elementinin görünürlüğü + dolu olması) kontrol ediliyor.
        # Hata elementi blur sonrası ASENKRON render edildiğinden (canlı
        # doğrulandı - anlık find_elements() bazen elementi henüz DOM'a
        # gelmeden yakalayıp yanlışlıkla "yok" sonucu veriyordu), sabit
        # bir find_elements yerine WebDriverWait'in dinamik polling'i
        # kullanılıyor.
        try:
            self.wait.until(EC.visibility_of_element_located(locator))
        except TimeoutException:
            return False
        return bool(self.driver.find_element(*locator).text.strip())

    def is_email_error_displayed(self):
        return self._is_error_displayed(self.EMAIL_ERROR)

    def is_mobile_phone_error_displayed(self):
        return self._is_error_displayed(self.MOBILE_PHONE_ERROR)

    def enter_mobile_phone_eight_digits(self):
        invalid_value = "05551234"
        self.update_mobile_phone(invalid_value)
        return invalid_value

    def enter_mobile_phone_nine_digits(self):
        # TC-009-04'teki (8 hane) ile AYNI desen - "bir eksik" sınır
        # değerin 9 hanelik karşılığı. Türkiye GSM formatı "5 ile başlayan
        # 10 hane" olduğundan (create_customer_page.py ile aynı kural),
        # 9 hane de tanımlı formatın DIŞINDA - hata beklenmesi doğru.
        invalid_value = "555123456"
        self.update_mobile_phone(invalid_value)
        return invalid_value

    def enter_mobile_phone_ten_digits(self):
        valid_value = "5551234567"
        self.update_mobile_phone(valid_value)
        return valid_value

    def wait_for_no_mobile_phone_error_and_save_enabled(self):
        # "herhangi bir doğrulama hatası gösterilmez" negatif bir durumu
        # doğrudan/erken kanıtlamaya çalışmak yerine (TC-004-11'de
        # kaçınılan AYNI tuzak) - önce POZİTİF/nihai durumu (Kaydet
        # butonunun GERÇEKTEN enabled olması, ki bu zaten Angular'ın form
        # geçerlilik hesaplamasının hata bulmadığını kanıtlar) bekliyoruz,
        # sonra o ANDAKİ hata elementinin durumunu ek bir doğrulama olarak
        # okuyoruz.
        self.wait.until(lambda d: not self.is_save_button_disabled())
        errors = self.driver.find_elements(*self.MOBILE_PHONE_ERROR)
        assert not errors or not errors[0].is_displayed() or not errors[0].text.strip(), (
            "Kaydet butonu aktif olmasına rağmen Mobile Phone hata mesajı hâlâ görünür"
        )

    def attempt_to_type_eleven_digits_in_phone_field(self, field_label):
        # ALL_PHONE_FIELD_LOCATORS ile dinamik eşleme - Mobile Phone/Home
        # Phone/Fax'ın ÜÇÜ de aynı mekanizmayı (native <input> maxlength)
        # paylaştığından tek bir metotla test edilebiliyor.
        locator = self.ALL_PHONE_FIELD_LOCATORS[field_label]
        field = self.driver.find_element(*locator)
        field.click()
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACK_SPACE)
        field.send_keys("55512345678")  # 11 hane
        return field.get_attribute("value")

    def attempt_to_type_long_valid_email(self, total_length=150):
        # Uzun ama FORMATÇA GEÇERLİ bir email (geçerli bir domain ile
        # bitiyor, "@" öncesi karakter sayısı uzatılarak toplam uzunluk
        # ayarlanıyor) - HTML seviyesinde bir maxlength olup olmadığını
        # test etmek için; alanın kendi format doğrulamasını (nokta/@
        # kuralı) TETİKLEMEDEN yalnızca uzunluk sınırını izole ediyor.
        domain = "@example.com"
        long_email = ("a" * (total_length - len(domain))) + domain
        self.update_email(long_email)
        return long_email

    def clear_required_field(self, field_label):
        locator = self.REQUIRED_FIELD_LOCATORS[field_label]
        field = self.driver.find_element(*locator)
        field.click()
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACK_SPACE)
        field.send_keys(Keys.TAB)

    def is_required_field_error_displayed(self, field_label):
        return self._is_error_displayed(self.REQUIRED_FIELD_ERROR_LOCATORS[field_label])

    def fill_only_required_fields_with_faker(self):
        # Home Phone / Fax BİLEREK boş bırakılıyor - opsiyonel oldukları
        # senaryosu için. Email/Mobile zorunlu, geçerli değerlerle
        # dolduruluyor.
        return self.update_email_and_mobile_with_faker()

    def get_country_code_prefixes(self):
        return (
            self.driver.find_element(*self.HOME_PHONE_COUNTRY).text.strip(),
            self.driver.find_element(*self.MOBILE_PHONE_COUNTRY).text.strip(),
            self.driver.find_element(*self.FAX_COUNTRY).text.strip(),
        )

    def is_country_code_fixed_at_plus_90(self):
        return all(prefix == "+90" for prefix in self.get_country_code_prefixes())

    def enter_email_expecting_duplicate_rejection(self, email):
        # E-posta benzersizliği ANINDA (client-side, blur sonrası) kontrol
        # ediliyor - canlı doğrulandı: Save'e hiç basmaya gerek kalmadan
        # hata elementi görünür oluyor ve Save otomatik disabled kalıyor.
        self.update_email(email)
