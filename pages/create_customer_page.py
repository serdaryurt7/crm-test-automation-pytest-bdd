import random
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage
from utils.test_data import fake

class CreateCustomerPage(BasePage):
    PAGE_TITLE = (By.CSS_SELECTOR, "[data-testid='page-title']")

    STEPPER_STEP_1 = (By.CSS_SELECTOR, "[data-testid='stepper-step-1']")
    STEPPER_STEP_2 = (By.CSS_SELECTOR, "[data-testid='stepper-step-2']")
    STEPPER_STEP_3 = (By.CSS_SELECTOR, "[data-testid='stepper-step-3']")

    # --- Adım 1: Demografik Bilgi ---
    FIRST_NAME = (By.ID, "firstName")
    SECOND_NAME = (By.ID, "secondName")
    LAST_NAME = (By.ID, "lastName")
    BIRTH_DATE = (By.ID, "birthDate")
    GENDER = (By.ID, "gender") # kullanılıyor mu ?
    GENDER_LIST = (By.ID, "gender-list")
    FATHER_NAME = (By.ID, "fatherName")
    MOTHER_NAME = (By.ID, "motherName")
    IDENTITY_NUMBER = (By.ID, "identityNumber")
    DEMOGRAPHIC_CANCEL = (By.CSS_SELECTOR, "[data-testid='customer-create-cancel']")
    DEMOGRAPHIC_NEXT = (By.CSS_SELECTOR, "[data-testid='customer-create-demographic-next']")

    # --- Adım 2: Adres ---
    ADD_ADDRESS_BUTTON = (By.CSS_SELECTOR, "[data-testid='customer-create-add-address']")
    ADDRESS_BACK = (By.CSS_SELECTOR, "[data-testid='customer-create-address-back']")
    ADDRESS_NEXT = (By.CSS_SELECTOR, "[data-testid='customer-create-address-next']")
    ADDRESS_CITY = (By.ID, "address-city")
    ADDRESS_CITY_LIST = (By.ID, "address-city-list")
    ADDRESS_CITY_ERROR = (By.ID, "address-city-error")
    ADDRESS_STREET = (By.ID, "address-street")
    ADDRESS_BUILDING_NO = (By.ID, "address-building")
    ADDRESS_DESCRIPTION = (By.ID, "address-description")
    ADDRESS_FORM_CANCEL = (By.CSS_SELECTOR, "[data-testid='address-cancel']")
    ADDRESS_SAVE = (By.CSS_SELECTOR, "[data-testid='address-save']")
    ADDRESS_CARD = (By.CSS_SELECTOR, "[data-testid='address-card']")
    ADDRESS_CARD_TITLE = (By.CSS_SELECTOR, "[data-testid='address-card-title']")
    ADDRESS_CARD_DETAIL = (By.CSS_SELECTOR, "[data-testid='address-card-detail']")
    ADDRESS_CARD_MENU = (By.CSS_SELECTOR, "[data-testid='address-card-menu']")
    ADDRESS_CARD_EDIT = (By.CSS_SELECTOR, "[data-testid='address-card-edit']")
    ADDRESS_CARD_DELETE = (By.CSS_SELECTOR, "[data-testid='address-card-delete']")

    # --- Adım 3: İletişim Kanalı ---
    EMAIL = (By.ID, "new-contact-email")
    EMAIL_ERROR = (By.ID, "new-contact-email-error")
    HOME_PHONE_COUNTRY = (By.CSS_SELECTOR, "[data-testid='customer-create-home-phone-country']")
    HOME_PHONE = (By.ID, "new-contact-home")
    MOBILE_PHONE_COUNTRY = (By.CSS_SELECTOR, "[data-testid='customer-create-country-code']")
    MOBILE_PHONE = (By.ID, "new-contact-mobile")
    MOBILE_PHONE_ERROR = (By.ID, "new-contact-mobile-error")
    FAX_COUNTRY = (By.CSS_SELECTOR, "[data-testid='customer-create-fax-country']")
    FAX = (By.ID, "new-contact-fax")
    CONTACT_BACK = (By.CSS_SELECTOR, "[data-testid='customer-create-contact-back']")
    SUBMIT = (By.CSS_SELECTOR, "[data-testid='customer-create-submit']")

    # --- Oluşturma sonrası: Customer Info ekranı ---
    CUSTOMER_DETAIL_HEADER = (By.CSS_SELECTOR, "[data-testid='customer-detail-header']")
    CUSTOMER_INFO_GENDER = (By.CSS_SELECTOR, "[data-testid='customer-info-value-gender']")
    CUSTOMER_INFO_SECOND_NAME = (By.CSS_SELECTOR, "[data-testid='customer-info-value-second-name']")
    CUSTOMER_INFO_FATHER_NAME = (By.CSS_SELECTOR, "[data-testid='customer-info-value-father-name']")
    CUSTOMER_INFO_MOTHER_NAME = (By.CSS_SELECTOR, "[data-testid='customer-info-value-mother-name']")
    CONTACT_INFO_HOME_PHONE = (By.CSS_SELECTOR, "[data-testid='customer-contact-value-home-phone']")
    CONTACT_INFO_FAX = (By.CSS_SELECTOR, "[data-testid='customer-contact-value-fax']")
    TAB_CONTACT = (By.CSS_SELECTOR, "[data-testid='tab-contact']")

    # Gender ve Adres Şehir alanları uygulama tarafında native <select>'ten
    # role="combobox" olan <button> + açılır <ul role="listbox"> ikilisine
    # geçirildi (bu oturum sırasında canlı doğrulandı - eski Select() tabanlı
    # kod artık gerçek uygulamayla uyuşmuyordu). GENDER_VALUE_MAP görünen
    # Türkçe metni listbox'taki data-value'ya çeviriyor.
    GENDER_VALUE_MAP = {"Erkek": "male", "Kadın": "female"}

    # UpdateCustomerPage.REQUIRED_FIELD_LOCATORS ile AYNI desen - Gherkin
    # Examples'taki okunabilir alan adını gerçek locator'a eşliyor, dinamik/
    # tek bir Scenario Outline'ın 3 alanı da (Second/Father/Mother Name)
    # kod tekrarı olmadan test edebilmesini sağlıyor.
    OPTIONAL_NAME_FIELD_LOCATORS = {
        "Second Name": SECOND_NAME,
        "Father Name": FATHER_NAME,
        "Mother Name": MOTHER_NAME,
    }

    def __init__(self, driver):
        # Not: BasePage zaten ignored_exceptions=(StaleElementReferenceException,)
        # kuruyor - bu sayfada ELDE EDİLEN davranış birebir aynı, yalnızca
        # tanım tek yere taşındı.
        super().__init__(driver)
        self.wait.until(EC.visibility_of_element_located(self.FIRST_NAME))
        self._entered_addresses = []

    # --- Adım 1: Demografik Bilgi ---
    def enter_first_name(self, value):
        field = self.driver.find_element(*self.FIRST_NAME)
        field.clear()
        field.send_keys(value)

    def enter_second_name(self, value):
        field = self.driver.find_element(*self.SECOND_NAME)
        field.clear()
        field.send_keys(value)

    def enter_last_name(self, value):
        field = self.driver.find_element(*self.LAST_NAME)
        field.clear()
        field.send_keys(value)

    def enter_birth_date(self, value):
        # value: "DD/MM/YYYY". Alan artık native <input type="date"> DEĞİL,
        # maskeli bir metin input'u (type="text", placeholder="gg/aa/yyyy") -
        # rakamlar sırayla (GGAAYYYY) yazılınca "/" otomatik ekleniyor
        # (ampirik doğrulandı: "15061990" -> "15/06/1990"). Önceki MM/DD/YYYY
        # tuş sırası dönüşümüne artık gerek yok.
        day, month, year = value.split("/")
        field = self.driver.find_element(*self.BIRTH_DATE)
        field.clear()
        field.send_keys(f"{day}{month}{year}")

    def is_birth_date_masked_text_input(self):
        # Birth Date bu oturum sırasında native <input type="date">'den
        # (tarayıcı/OS takvimi açan) gg/aa/yyyy formatında maskeli bir
        # <input type="text">'e geçirildi (canlı doğrulandı) - bu artık bir
        # bug değil, kasıtlı bir tasarım değişikliği. Eski
        # is_birth_date_native_date_picker() ismi yanıltıcı olacağından
        # gerçek davranışı yansıtacak şekilde yeniden adlandırıldı.
        field = self.driver.find_element(*self.BIRTH_DATE)
        return field.get_attribute("type") == "text" and field.get_attribute("placeholder") == "gg/aa/yyyy"

    def enter_birth_date_with_faker(self):
        birth_date = fake.date_of_birth(minimum_age=18, maximum_age=90).strftime("%d/%m/%Y")
        self.enter_birth_date(birth_date)
        self._last_entered_birth_date = birth_date
        return birth_date

    def get_birth_date_displayed_value(self):
        # Artık native <input type="date"> olmadığı için değer ISO formatında
        # (yyyy-mm-dd) DEĞİL, ekranda görünen gg/aa/yyyy formatında geliyor.
        return self.driver.find_element(*self.BIRTH_DATE).get_attribute("value")

    def is_birth_date_displayed_correctly(self):
        return self.get_birth_date_displayed_value() == self._last_entered_birth_date

    def _is_gender_list_open(self):
        list_els = self.driver.find_elements(*self.GENDER_LIST)
        return bool(list_els) and list_els[0].is_displayed()

    def click_gender_field(self):
        self.driver.find_element(*self.GENDER).click()
        self.wait.until(EC.visibility_of_element_located(self.GENDER_LIST))

    def get_gender_options(self):
        # Bu metod hem liste ZATEN AÇIKKEN (ör. "kullanıcı Gender alanını
        # açar" adımından hemen sonra) hem KAPALIYKEN çağrılabiliyor - her
        # iki durumda da güvenli çalışması için önce açık olup olmadığı
        # kontrol ediliyor.
        if not self._is_gender_list_open():
            self.click_gender_field()
        return [
            o.text.strip()
            for o in self.driver.find_elements(By.CSS_SELECTOR, "#gender-list li[role='option']")
        ]

    def select_gender(self, value):
        if not self._is_gender_list_open():
            self.click_gender_field()
        data_value = self.GENDER_VALUE_MAP[value]
        self.driver.find_element(By.CSS_SELECTOR, f"#gender-list li[data-value='{data_value}']").click()
        # Secimden hemen sonra devam etmek (ör. form validity kontrolu)
        # yuk altinda kacan bir race condition'a yol acabiliyordu - liste
        # gercekten kapanip Angular'in secimi islemesini bekliyoruz.
        self.wait.until(EC.invisibility_of_element_located(self.GENDER_LIST))

    def enter_father_name(self, value):
        field = self.driver.find_element(*self.FATHER_NAME)
        field.clear()
        field.send_keys(value)

    def enter_mother_name(self, value):
        field = self.driver.find_element(*self.MOTHER_NAME)
        field.clear()
        field.send_keys(value)

    def attempt_to_type_long_value_in_optional_name_field(self, field_label, length):
        # UpdateCustomerPage.attempt_to_type_long_value() ile AYNI desen:
        # .clear() Angular'ın reaktif form durumunu güvenilir tetiklemediği
        # için CTRL+A + BACKSPACE ile gerçek kullanıcı tuş vuruşu simüle
        # edilerek alan önce temizleniyor.
        locator = self.OPTIONAL_NAME_FIELD_LOCATORS[field_label]
        field = self.fill(locator, "a" * length)
        return field.get_attribute("value")

    def type_valid_birth_date_digits(self, digits="15061990"):
        # Canlı doğrulandı: Birth Date maskesi basit "ilk N rakamı al"
        # mekanizması DEĞİL - gün/ay geçerliliğini ANLIK doğrulayan daha
        # karmaşık bir maske (ör. "123456789" yazılınca ay basamağı
        # geçersiz kaldığından bazı rakamlar sessizce filtreleniyor, sonuç
        # girilen rakamların birebir ilk 8'i OLMUYOR). Bu yüzden GERÇEKTEN
        # geçerli, belirsizlik yaratmayan bir tarih (15/06/1990) kasıtlı
        # olarak sabit kullanılıyor - amaç maskenin gün/ay doğrulama
        # detaylarını değil, yalnızca 10 karakterlik üst sınır kapasitesini
        # test etmek.
        field = self.fill(self.BIRTH_DATE, digits)
        return field.get_attribute("value")

    def append_extra_digit_to_birth_date(self):
        field = self.driver.find_element(*self.BIRTH_DATE)
        field.send_keys("9")
        return field.get_attribute("value")

    def enter_identity_number(self, value):
        field = self.driver.find_element(*self.IDENTITY_NUMBER)
        field.clear()
        field.send_keys(value)
        field.send_keys(Keys.TAB)
        # Identity Number genelde demografik doldurma akışının SON alanı
        # oluyor. Canlı olarak doğrulandı: TAB/blur sonrası bile DOM'daki
        # değerler zaten doğruyken "Next" butonu ANLIK olarak hâlâ disabled
        # dönebiliyor - Angular'ın form validity durumunu yeniden hesaplayıp
        # butonu güncellemesi ayrı bir change-detection cycle'ında (~200ms)
        # gerçekleşiyor. WebDriverWait ile "ne" bekleneceği duruma göre
        # değiştiğinden (bazen disabled KALMALI) kısa sabit bir bekleme
        # kullanılıyor.
        time.sleep(0.3)
        self._last_identity_number = value

    def fill_demographic_step(self, first_name, last_name, birth_date, gender, identity_number):
        self.enter_first_name(first_name)
        self.enter_last_name(last_name)
        self.enter_birth_date(birth_date)
        self.select_gender(gender)
        self.enter_identity_number(identity_number)
        self._last_first_name = first_name
        self._last_last_name = last_name
        self._last_birth_date = birth_date
        self._last_gender = gender

    def fill_demographic_step_with_faker(self, gender):
        # Gender parametre olarak dışarıdan (Scenario Outline Examples'tan)
        # veriliyor, Faker ile rastgele SEÇİLMİYOR. GEÇMİŞ NOT: burada uzun
        # süre gerçek bir bug vardı (ne seçilirse seçilsin sistem her zaman
        # "Erkek" kaydediyordu) - Kadın/Erkek AYRI AYRI çalıştırılarak bu
        # asimetrik davranış kanıtlanıyordu. Bu oturum sırasında (Gender/
        # Birth Date alanlarının native kontrollerden özel widget'lara
        # geçirildiği güncellemeyle birlikte) canlı olarak yeniden
        # doğrulandı: bug artık YOK, "Kadın" seçilince gerçekten "Kadın"
        # kaydediliyor. Senaryo hâlâ iki cinsiyeti de ayrı ayrı çalıştırıyor
        # (regresyon guard'ı olarak DEĞERLİ), ama artık kasıtlı kırmızı
        # değil - ikisi de PASS etmesi beklenen normal bir doğrulama.
        first_name = fake.first_name_female() if gender == "Kadın" else fake.first_name_male()
        last_name = fake.last_name()
        birth_date = fake.date_of_birth(minimum_age=18, maximum_age=90).strftime("%d/%m/%Y")
        identity_number = fake.numerify("###########")
        self.fill_demographic_step(first_name, last_name, birth_date, gender, identity_number)
        return first_name, last_name, birth_date, identity_number

    def fill_demographic_step_with_all_fields_via_faker(self, gender):
        # fill_demographic_step_with_faker()'dan farklı olarak, OPSİYONEL
        # alanları (Second Name, Father Name, Mother Name) da dolduruyor -
        # "tüm alanlar (opsiyonel dahil) doldurulduğunda müşterinin
        # eksiksiz oluşturulması" senaryosu için. Diğer tüm senaryoların
        # kullandığı minimal disposable-customer akışı (fill_demographic_
        # step_with_faker) BİLEREK değiştirilmedi - bu ayrı bir metot,
        # sadece bu senaryoya özel.
        first_name = fake.first_name_female() if gender == "Kadın" else fake.first_name_male()
        second_name = fake.first_name()
        last_name = fake.last_name()
        birth_date = fake.date_of_birth(minimum_age=18, maximum_age=90).strftime("%d/%m/%Y")
        father_name = fake.first_name_male()
        mother_name = fake.first_name_female()
        identity_number = fake.numerify("###########")

        self.enter_first_name(first_name)
        self.enter_second_name(second_name)
        self.enter_last_name(last_name)
        self.enter_birth_date(birth_date)
        self.select_gender(gender)
        self.enter_father_name(father_name)
        self.enter_mother_name(mother_name)
        self.enter_identity_number(identity_number)

        return {
            "first_name": first_name,
            "second_name": second_name,
            "last_name": last_name,
            "birth_date": birth_date,
            "gender": gender,
            "father_name": father_name,
            "mother_name": mother_name,
            "identity_number": identity_number,
        }

    def fill_demographic_step_without_last_name(self):
        # Last Name (Soyad) BİLEREK boş bırakılıyor - "Next butonu pasif
        # kalmalı" senaryosu için diğer tüm zorunlu alanlar (First Name,
        # Birth Date, Gender, Nationality ID) doldurulup sadece Soyad
        # atlanıyor.
        first_name = fake.first_name()
        birth_date = fake.date_of_birth(minimum_age=18, maximum_age=90).strftime("%d/%m/%Y")
        gender = fake.random_element(elements=("Kadın", "Erkek"))
        identity_number = fake.numerify("###########")
        self.enter_first_name(first_name)
        self.enter_birth_date(birth_date)
        self.select_gender(gender)
        self.enter_identity_number(identity_number)

    def fill_missing_last_name(self):
        last_name = fake.last_name()
        self.enter_last_name(last_name)
        # enter_identity_number()'daki aynı blur/change-detection gerekçesi
        # - burada Soyad akışın son alanı oluyor.
        self.driver.find_element(*self.LAST_NAME).send_keys(Keys.TAB)
        time.sleep(0.3)
        return last_name

    def get_first_name_value(self):
        return self.driver.find_element(*self.FIRST_NAME).get_attribute("value")

    def get_last_name_value(self):
        return self.driver.find_element(*self.LAST_NAME).get_attribute("value")

    def get_identity_number_value(self):
        return self.driver.find_element(*self.IDENTITY_NUMBER).get_attribute("value")

    def get_selected_gender_text(self):
        return self.driver.find_element(*self.GENDER).text.strip()

    def are_demographic_values_displayed(self):
        return (
            self.get_first_name_value() == self._last_first_name
            and self.get_last_name_value() == self._last_last_name
            and self.get_birth_date_displayed_value() == self._last_birth_date
            and self.get_selected_gender_text() == self._last_gender
            and self.get_identity_number_value() == self._last_identity_number
        )

    def click_demographic_next(self):
        self.wait.until(EC.element_to_be_clickable(self.DEMOGRAPHIC_NEXT)).click()

    def is_demographic_next_disabled(self):
        return not self.driver.find_element(*self.DEMOGRAPHIC_NEXT).is_enabled()

    def fill_some_demographic_fields(self):
        first_name = fake.first_name()
        last_name = fake.last_name()
        identity_number = fake.numerify("###########")
        self.enter_first_name(first_name)
        self.enter_last_name(last_name)
        self.enter_identity_number(identity_number)
        return first_name, last_name, identity_number

    def click_demographic_cancel(self):
        self.wait.until(EC.element_to_be_clickable(self.DEMOGRAPHIC_CANCEL)).click()

    def wait_for_navigated_to_customer_list(self):
        self.wait.until(lambda d: d.current_url.rstrip("/").endswith("/customers"))

    # --- Adım 2: Adres ---
    def click_add_address(self):
        self.wait.until(EC.element_to_be_clickable(self.ADD_ADDRESS_BUTTON)).click()

    def select_address_city(self, city_name):
        # Şehir alanı native <select>'ten role="combobox" olan <button> +
        # açılır <ul id="address-city-list" role="listbox"> ikilisine
        # geçirildi (Gender ile aynı desen, bu oturumda canlı doğrulandı).
        city_field = self.wait.until(EC.visibility_of_element_located(self.ADDRESS_CITY))
        city_field.click()
        self.wait.until(EC.visibility_of_element_located(self.ADDRESS_CITY_LIST))
        self.driver.find_element(By.CSS_SELECTOR, f"#address-city-list li[data-value='{city_name}']").click()
        self.wait.until(EC.invisibility_of_element_located(self.ADDRESS_CITY_LIST))

    def enter_address_street(self, value):
        field = self.driver.find_element(*self.ADDRESS_STREET)
        field.clear()
        field.send_keys(value)

    def enter_address_building_no(self, value):
        field = self.driver.find_element(*self.ADDRESS_BUILDING_NO)
        field.clear()
        field.send_keys(value)

    def enter_address_description(self, value):
        field = self.driver.find_element(*self.ADDRESS_DESCRIPTION)
        field.clear()
        field.send_keys(value)

    def click_address_save(self):
        self.wait.until(EC.element_to_be_clickable(self.ADDRESS_SAVE)).click()

    def click_address_next(self):
        self.wait.until(EC.element_to_be_clickable(self.ADDRESS_NEXT)).click()

    def add_address(self, city, street, building_no, description):
        self.click_add_address()
        self.select_address_city(city)
        self.enter_address_street(street)
        self.enter_address_building_no(building_no)
        self.enter_address_description(description)
        self.click_address_save()
        self._entered_addresses.append((city, street, building_no, description))

    def fill_address_form(self, city, street, building_no, description):
        # add_address()'ten farklı olarak Save'e TIKLAMIYOR - manuel case'in
        # "form doldurulmuştur" (Given) ile "Save'e tıklar" (When) adımlarını
        # ayrı ayrı test edebilmesi için doldurma ve kaydetme birbirinden
        # ayrıştırıldı.
        self.click_add_address()
        self.select_address_city(city)
        self.enter_address_street(street)
        self.enter_address_building_no(building_no)
        self.enter_address_description(description)
        self._pending_address = (city, street, building_no, description)
        self._pending_address_is_edit = False

    def update_address_street(self, new_street):
        # Var olan bir adresi Edit formunda güncellerken kullanılıyor - Save'e
        # basılınca save_address_form() bunun YENİ bir adres değil, MEVCUT
        # kaydın güncellemesi olduğunu self._pending_address_is_edit ile
        # ayırt edip listeye APPEND etmek yerine son elemanı DEĞİŞTİRİYOR.
        self.enter_address_street(new_street)
        city, _, building_no, description = self._entered_addresses[-1]
        self._pending_address = (city, new_street, building_no, description)
        self._pending_address_is_edit = True

    def save_address_form(self):
        self.click_address_save()
        if self._pending_address_is_edit:
            self._entered_addresses[-1] = self._pending_address
        else:
            self._entered_addresses.append(self._pending_address)

    def add_address_with_faker(self):
        # Şehir Faker'dan DEĞİL, ekrandaki gerçek listbox seçeneklerinden
        # rastgele seçiliyor: address-city alanı yalnızca kendi option
        # listesindeki 81 il adından biriyle TAM eşleşirse kabul ediyor,
        # Faker'ın ürettiği bir şehir adının bu listeyle birebir eşleşeceği
        # garanti edilemez (örn. ilçe/kısaltma farkı).
        self.click_add_address()
        city_field = self.wait.until(EC.visibility_of_element_located(self.ADDRESS_CITY))
        city_field.click()
        self.wait.until(EC.visibility_of_element_located(self.ADDRESS_CITY_LIST))
        city_options = self.driver.find_elements(By.CSS_SELECTOR, "#address-city-list li[role='option']")
        chosen = random.choice(city_options)
        city = chosen.get_attribute("data-value")
        chosen.click()
        self.wait.until(EC.invisibility_of_element_located(self.ADDRESS_CITY_LIST))
        street = fake.street_name()
        building_no = fake.building_number()
        description = fake.sentence(nb_words=4)
        self.enter_address_street(street)
        self.enter_address_building_no(building_no)
        self.enter_address_description(description)
        self.click_address_save()
        self._entered_addresses.append((city, street, building_no, description))
        return city, street, building_no, description

    def wait_for_address_form_open(self):
        self.wait.until(EC.visibility_of_element_located(self.ADDRESS_SAVE))

    def fill_address_form_without_city(self):
        # Şehir (City) BİLEREK boş bırakılıyor - "Save butonu pasif kalmalı"
        # senaryosu için diğer tüm zorunlu adres alanları (Street, Building
        # No, Description) doldurulup sadece Şehir atlanıyor.
        street = fake.street_name()
        building_no = fake.building_number()
        description = fake.sentence(nb_words=4)
        self.enter_address_street(street)
        self.enter_address_building_no(building_no)
        self.enter_address_description(description)

    def fill_missing_city(self):
        city_field = self.wait.until(EC.visibility_of_element_located(self.ADDRESS_CITY))
        city_field.click()
        self.wait.until(EC.visibility_of_element_located(self.ADDRESS_CITY_LIST))
        city_options = self.driver.find_elements(By.CSS_SELECTOR, "#address-city-list li[role='option']")
        chosen = random.choice(city_options)
        city = chosen.get_attribute("data-value")
        chosen.click()
        self.wait.until(EC.invisibility_of_element_located(self.ADDRESS_CITY_LIST))
        return city

    def is_address_save_disabled(self):
        return not self.driver.find_element(*self.ADDRESS_SAVE).is_enabled()

    def open_address_card_menu(self):
        self.wait.until(EC.element_to_be_clickable(self.ADDRESS_CARD_MENU)).click()

    def click_address_card_edit(self):
        self.open_address_card_menu()
        self.wait.until(EC.element_to_be_clickable(self.ADDRESS_CARD_EDIT)).click()

    def is_address_edit_form_prefilled_correctly(self):
        city, street, building_no, description = self._entered_addresses[-1]
        # Edit formu açılırken Şehir butonu (Angular render) hemen DOM'da
        # olmayabiliyor - canlı olarak doğrulandı (NoSuchElementException).
        city_field = self.wait.until(EC.visibility_of_element_located(self.ADDRESS_CITY))
        city_value = city_field.text.strip()
        street_value = self.driver.find_element(*self.ADDRESS_STREET).get_attribute("value")
        building_value = self.driver.find_element(*self.ADDRESS_BUILDING_NO).get_attribute("value")
        description_value = self.driver.find_element(*self.ADDRESS_DESCRIPTION).get_attribute("value")
        return (city_value, street_value, building_value, description_value) == (city, street, building_no, description)

    def click_address_form_cancel(self):
        self.wait.until(EC.element_to_be_clickable(self.ADDRESS_FORM_CANCEL)).click()

    def click_address_card_delete(self):
        self.open_address_card_menu()
        self.wait.until(EC.element_to_be_clickable(self.ADDRESS_CARD_DELETE)).click()
        if self._entered_addresses:
            self._entered_addresses.pop()

    def get_address_card_count(self):
        return len(self.driver.find_elements(*self.ADDRESS_CARD))

    def wait_for_address_step(self):
        self.wait.until(EC.visibility_of_element_located(self.ADD_ADDRESS_BUTTON))

    def is_address_next_disabled(self):
        return not self.driver.find_element(*self.ADDRESS_NEXT).is_enabled()

    def wait_for_address_saved(self):
        self.wait.until(EC.visibility_of_element_located(self.ADDRESS_CARD))
        self.wait.until(EC.element_to_be_clickable(self.ADDRESS_NEXT))

    def are_all_entered_addresses_displayed_as_cards(self):
        self.wait.until(lambda d: len(d.find_elements(*self.ADDRESS_CARD)) == len(self._entered_addresses))
        cards = self.driver.find_elements(*self.ADDRESS_CARD)
        for card, (city, street, building_no, description) in zip(cards, self._entered_addresses):
            title = card.find_element(*self.ADDRESS_CARD_TITLE).text
            detail = card.find_element(*self.ADDRESS_CARD_DETAIL).text
            if title != f"{city}, {street}, {building_no}" or detail != description:
                return False
        return True

    # --- Adım 3: İletişim Kanalı ---
    def enter_email(self, value):
        field = self.driver.find_element(*self.EMAIL)
        field.clear()
        field.send_keys(value)

    def enter_invalid_email_format(self):
        # Hata mesajı sadece BLUR sonrası görünüyor (gerçek uygulamada
        # doğrulandı) - Tab ile başka alana odak kaydırılarak blur
        # tetikleniyor.
        invalid_email = "ahmet.yilmaz@"
        field = self.driver.find_element(*self.EMAIL)
        field.clear()
        field.send_keys(invalid_email)
        field.send_keys(Keys.TAB)
        return invalid_email

    def is_email_error_displayed(self):
        # Mesaj metni dile göre değişebileceğinden (gerçek uygulamada
        # "Geçerli bir e-posta girin; adres .com ile bitmelidir." çıkıyor,
        # manuel case'in paraphrase'i "Geçersiz email formatı" ile birebir
        # aynı değil) yapısal olarak (hata elementinin görünürlüğü) kontrol
        # ediliyor, literal metin karşılaştırılmıyor.
        errors = self.driver.find_elements(*self.EMAIL_ERROR)
        return bool(errors) and errors[0].is_displayed()

    def fix_email_with_faker(self):
        email = f"{fake.user_name()}.{fake.random_number(digits=6, fix_len=True)}@example.com"
        self.enter_email(email)
        self.driver.find_element(*self.EMAIL).send_keys(Keys.TAB)
        # Sabit bir sleep süresi güvenilir değildi (canlı ölçümde gecikme
        # ~0.3-0.6s arasında değişiyordu) - bunun yerine önceki hata
        # elementinin GERÇEKTEN kaybolmasını bekliyoruz. Hiç hata
        # gösterilmiyorsa (element DOM'da yok) EC.invisibility_of_element_
        # located zaten anında True döner, bu yüzden "temiz" email girişini
        # de güvenle kapsıyor.
        self.wait.until(EC.invisibility_of_element_located(self.EMAIL_ERROR))
        return email

    def fill_mobile_phone_with_faker(self):
        mobile_phone = fake.numerify("5#########")
        self.enter_mobile_phone(mobile_phone)
        return mobile_phone

    def enter_invalid_mobile_phone_format(self):
        # 8 haneli değer BİLEREK kullanılıyor: gerçek uygulamada doğrulama
        # kuralı "tam 10 hane olmalı" (hata: "Türkiye (+90) için telefon
        # numarası 10 haneli olmalıdır.") ama 8 hanede GERÇEK BİR BUG var -
        # bu tek uzunlukta hata gösterilmiyor ve Create aktif kalıyor
        # (1/2/6/7/9 hane doğru şekilde reddediliyor). Bu senaryo BİLEREK
        # doğru/beklenen davranışı iddia ediyor, bug düzelene kadar
        # kasıtlı kırmızı kalacak.
        invalid_mobile = "05551234"
        field = self.driver.find_element(*self.MOBILE_PHONE)
        field.clear()
        field.send_keys(invalid_mobile)
        field.send_keys(Keys.TAB)
        return invalid_mobile

    def is_mobile_phone_error_displayed(self):
        errors = self.driver.find_elements(*self.MOBILE_PHONE_ERROR)
        return bool(errors) and errors[0].is_displayed()

    def enter_home_phone(self, value):
        field = self.driver.find_element(*self.HOME_PHONE)
        field.clear()
        field.send_keys(value)

    def enter_mobile_phone(self, value):
        field = self.driver.find_element(*self.MOBILE_PHONE)
        field.clear()
        field.send_keys(value)
        # Mobile Phone genelde İletişim Kanalı adımının SON alanı oluyor -
        # enter_identity_number()'daki aynı gecikmeli form-validity
        # gerekçesiyle blur + kısa bekleme ekleniyor.
        field.send_keys(Keys.TAB)
        time.sleep(0.3)

    def enter_fax(self, value):
        field = self.driver.find_element(*self.FAX)
        field.clear()
        field.send_keys(value)

    def wait_for_contact_step(self):
        self.wait.until(EC.visibility_of_element_located(self.EMAIL))

    def get_email_value(self):
        return self.driver.find_element(*self.EMAIL).get_attribute("value")

    def get_mobile_phone_value(self):
        return self.driver.find_element(*self.MOBILE_PHONE).get_attribute("value")

    def fill_contact_step_with_faker(self):
        # Email için domain BİLEREK "example.com" olarak sabitleniyor: gerçek
        # uygulamada denendi, form validasyonu email'in ".com" ile bitmesini
        # zorunlu kılıyor ("Geçerli bir e-posta girin; adres .com ile
        # bitmelidir.") - fake.email()'in varsayılanı bazen .org/.net gibi
        # başka TLD'ler üretip bu validasyona takılıyordu. Ayrıca backend
        # email'in benzersiz olmasını zorunlu kılıyor (bkz. "Uçtan Uca Müşteri
        # Yaratma" senaryosundaki 400 "already registered" bulgusu), bu yüzden
        # rastgele bir sayı eklenerek çalıştırmalar arası çakışma riski
        # azaltılıyor. Mobile Phone alanı yalnızca rakam kabul ediyor ve
        # Türkiye GSM formatına (5 ile başlayan 10 hane) uygun olması
        # gerekiyor - Faker'ın genel phone_number() sağlayıcısı boşluk/
        # parantez içerdiğinden kullanılmıyor, bunun yerine numerify ile
        # format zorlanıyor.
        email = f"{fake.user_name()}.{fake.random_number(digits=6, fix_len=True)}@example.com"
        mobile_phone = fake.numerify("5#########")
        self.enter_email(email)
        self.enter_mobile_phone(mobile_phone)
        self._last_email = email
        self._last_mobile_phone = mobile_phone
        return email, mobile_phone

    def fill_contact_step_with_all_fields_via_faker(self):
        # fill_contact_step_with_faker()'dan farklı olarak, OPSİYONEL
        # alanları (Home Phone, Fax) da dolduruyor - "tüm alanlar
        # (opsiyonel dahil) doldurulduğunda müşterinin eksiksiz
        # oluşturulması" senaryosuna özel.
        email = f"{fake.user_name()}.{fake.random_number(digits=6, fix_len=True)}@example.com"
        mobile_phone = fake.numerify("5#########")
        home_phone = fake.numerify("2#########")
        fax = fake.numerify("2#########")
        self.enter_email(email)
        self.enter_mobile_phone(mobile_phone)
        self.enter_home_phone(home_phone)
        self.enter_fax(fax)
        self._last_email = email
        self._last_mobile_phone = mobile_phone
        return {
            "email": email,
            "mobile_phone": mobile_phone,
            "home_phone": home_phone,
            "fax": fax,
        }

    def click_contact_back(self):
        self.wait.until(EC.element_to_be_clickable(self.CONTACT_BACK)).click()

    def are_contact_values_displayed(self):
        return self.get_email_value() == self._last_email and self.get_mobile_phone_value() == self._last_mobile_phone

    def is_submit_disabled(self):
        return not self.driver.find_element(*self.SUBMIT).is_enabled()

    def click_submit(self):
        self.wait.until(EC.element_to_be_clickable(self.SUBMIT)).click()

    def wait_for_navigated_to_customer_info(self):
        self.wait.until(lambda d: "/customers/" in d.current_url and "/customers/new" not in d.current_url)
        self.wait.until(EC.visibility_of_element_located(self.CUSTOMER_DETAIL_HEADER))

    def get_customer_info_gender_value(self):
        return self.driver.find_element(*self.CUSTOMER_INFO_GENDER).text.strip()

    def get_customer_info_second_name_value(self):
        return self.driver.find_element(*self.CUSTOMER_INFO_SECOND_NAME).text.strip()

    def get_customer_info_father_name_value(self):
        return self.driver.find_element(*self.CUSTOMER_INFO_FATHER_NAME).text.strip()

    def get_customer_info_mother_name_value(self):
        return self.driver.find_element(*self.CUSTOMER_INFO_MOTHER_NAME).text.strip()

    def get_contact_home_phone_value(self):
        return self.driver.find_element(*self.CONTACT_INFO_HOME_PHONE).text.strip()

    def get_contact_fax_value(self):
        return self.driver.find_element(*self.CONTACT_INFO_FAX).text.strip()

    def are_optional_fields_displayed_correctly(self, demographic_data, contact_data):
        # Telefon değerleri görüntüleme modunda sabit "+90" öneki ile
        # gösterildiğinden (canlı doğrulandı) tam eşitlik yerine substring
        # kontrolü yapılıyor - address_update/contact_update'teki AYNI
        # desen. Home Phone/Fax "İletişim Kanalı" sekmesinde olduğundan
        # (varsayılan/iniş sekmesi "Müşteri Bilgisi") önce o sekmeye
        # geçiliyor.
        demographic_ok = (
            self.get_customer_info_second_name_value() == demographic_data["second_name"]
            and self.get_customer_info_father_name_value() == demographic_data["father_name"]
            and self.get_customer_info_mother_name_value() == demographic_data["mother_name"]
        )
        self.wait.until(EC.element_to_be_clickable(self.TAB_CONTACT)).click()
        self.wait.until(EC.visibility_of_element_located(self.CONTACT_INFO_HOME_PHONE))
        contact_ok = (
            contact_data["home_phone"] in self.get_contact_home_phone_value()
            and contact_data["fax"] in self.get_contact_fax_value()
        )
        return demographic_ok and contact_ok
