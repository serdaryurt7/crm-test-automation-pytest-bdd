from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage
from utils.test_data import fake


class UpdateCustomerPage(BasePage):
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
    IDENTITY_NUMBER_ERROR = (By.CSS_SELECTOR, "[data-testid='info-identityNumber-error']")

    REQUIRED_FIELD_LOCATORS = {
        "Ad": FIRST_NAME_INPUT,
        "Soyad": LAST_NAME_INPUT,
    }

    def __init__(self, driver):
        super().__init__(driver)
        self.wait.until(EC.visibility_of_element_located(self.DETAIL_HEADER))
        self._detail_url = driver.current_url
        self._pre_edit_first_name = None
        self._pre_edit_last_name = None
        self._pre_edit_birth_date = None
        self._pre_edit_gender = None
        self._pre_edit_identity_number = None
        self._new_first_name = None

    def get_detail_url(self):
        return self._detail_url

    def reopen_edit_form(self, detail_url):
        # driver.get ile baska bir sayfaya (ör. yeni bir musteri
        # olusturma akisina) gidip geri donuldukten sonra duzenleme
        # formunu tekrar acmak icin kullaniliyor - navigasyon, devam eden
        # herhangi bir edit-mode durumunu sifirladigindan Edit'e tekrar
        # tiklanmasi gerekiyor.
        self.driver.get(detail_url)
        self.wait.until(EC.visibility_of_element_located(self.DETAIL_HEADER))
        self.click_edit()

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
        # Gender ve Birth Date bu oturum sirasinda native <select>/<input
        # type="date">'den role="combobox" olan <button> ve gg/aa/yyyy
        # formatinda maskeli <input type="text">'e gecirildi (canli
        # dogrulandi) - goruntuleme modu ile ayni format/metni kullaniyorlar,
        # ayrica bir format donusumune gerek yok.
        actual_birth_date = self.driver.find_element(*self.BIRTH_DATE_INPUT).get_attribute("value")
        selected_gender_text = self.driver.find_element(*self.GENDER_SELECT).text.strip()
        return (
            self.driver.find_element(*self.FIRST_NAME_INPUT).get_attribute("value") == self._pre_edit_first_name
            and self.driver.find_element(*self.LAST_NAME_INPUT).get_attribute("value") == self._pre_edit_last_name
            and actual_birth_date == self._pre_edit_birth_date
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
        field = self.fill(locator, "a" * length)
        return field.get_attribute("value")

    def update_identity_number(self, new_value):
        self.fill(self.IDENTITY_NUMBER_INPUT, new_value, blur=True)

    def is_identity_number_error_displayed(self):
        # Canli dogrulandi: Nationality ID baska bir musteriye ait bir
        # degerle degistirildiginde sistem ANLIK (client-side) bir
        # benzersizlik hatasi gosteriyor ve Kaydet butonu bu yuzden hic
        # enabled olmuyor - Save'e basmaya/backend'e istek gitmesine hic
        # gerek kalmiyor. Mesaj metni dile gore degisebilecegi icin
        # (TR/EN) yapisal olarak (hata elementinin gorunurlugu) kontrol
        # ediliyor, literal metin karsilastirilmiyor.
        self.wait.until(EC.visibility_of_element_located(self.IDENTITY_NUMBER_ERROR))
        return self.driver.find_element(*self.IDENTITY_NUMBER_ERROR).is_displayed()

    def get_identity_number_input_value(self):
        return self.driver.find_element(*self.IDENTITY_NUMBER_INPUT).get_attribute("value")

    def wait_for_identity_number_length_error(self):
        # Dilden bağımsız: TR ("...11 haneli olmalı...") ve EN ("...exactly
        # 11 digits...") mesajları farklı kelimelerle yazılsa da İKİSİNDE DE
        # ORTAK olan tek değişmez unsur "11" rakamının kendisi (bu iki dil
        # metni UC-017/TC-017-06 keşfinde canlı doğrulanmıştı - bkz.
        # search_customers_page.py'deki wait_for_identity_number_length_
        # validation_error() ile AYNI desen). is_identity_number_error_
        # displayed()'ten farkı: yalnızca "bir hata var mı" değil,
        # SPESİFİK OLARAK 11-hane uzunluk hatası mı olduğunu doğruluyor -
        # aynı hata elementi TC-004-03'teki benzersizlik hatası için de
        # kullanılıyor, "boş değil" kontrolü tek başına ayırt edici olmazdı.
        self.wait.until(lambda d: "11" in d.find_element(*self.IDENTITY_NUMBER_ERROR).text)

    def wait_for_save_enabled_with_no_identity_number_error(self):
        # "herhangi bir doğrulama hatası gösterilmez" negatif bir durumu
        # doğrudan kanıtlamaya çalışmak (erken/yarış durumuna açık) yerine -
        # TC-004-03b'deki AYNI desen: önce POZİTİF/nihai durumu (Kaydet
        # butonunun GERÇEKTEN enabled olması, ki bu zaten Angular'ın form
        # geçerlilik hesaplamasının hata bulmadığını kanıtlar) bekliyoruz,
        # sonra o ANDAKİ hata elementinin durumunu ek bir doğrulama olarak
        # okuyoruz.
        self.wait.until(lambda d: not self.is_save_button_disabled())
        errors = self.driver.find_elements(*self.IDENTITY_NUMBER_ERROR)
        assert not errors or not errors[0].is_displayed(), (
            "Kaydet butonu aktif olmasına rağmen Nationality ID hata mesajı hâlâ görünür"
        )

    def update_identity_number_with_random_unique_value(self):
        # Faker ile rastgele 11 haneli bir TC no üretiliyor - collision
        # riski ihmal edilebilir (create_customer_page.py'deki fill_
        # demographic_step_with_faker() ile AYNI yöntem, projenin genelinde
        # "pratikte eşsiz" Faker değerlerine güvenme konvansiyonuyla
        # tutarlı - ör. contact_update'teki email benzersizliği testleri).
        new_value = fake.numerify("###########")
        self.update_identity_number(new_value)
        return new_value

    def attempt_to_type_long_identity_number(self, length):
        # maxlength=11 gerçek bir HTML özniteliği (Birth Date maskesinin
        # aksine JS ile gün/ay geçerliliği filtrelemiyor - canlı doğrulandı,
        # bkz. create_customer.md notları) - bu yüzden hangi rakamla
        # doldurulursa doldurulsun tarayıcı tarafından güvenilir şekilde
        # ilk 11 karaktere kesilmesi beklenir.
        field = self.fill(self.IDENTITY_NUMBER_INPUT, "1" * length)
        return field.get_attribute("value")

    def get_save_error_text(self):
        return self.wait.until(EC.visibility_of_element_located(self.SAVE_ERROR)).text

    def is_save_error_displayed(self):
        return bool(self.driver.find_elements(*self.SAVE_ERROR)) and self.driver.find_element(*self.SAVE_ERROR).is_displayed()

    def attempt_xss_in_first_name(self):
        # Not: login.feature'daki SQL Injection/XSS senaryosunda oldugu gibi
        # native alert() gorulmesi tek basina yeterli degil - bu alanda
        # gozlenen ASIL davranis input'un ozel karakterleri (< > ( ) / 1 vb.)
        # yaziliken FILTRELEMESI, HTML kacislama degil.
        field = self.fill(self.FIRST_NAME_INPUT, "<script>alert(1)</script>")
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
        self.fill(locator)

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
