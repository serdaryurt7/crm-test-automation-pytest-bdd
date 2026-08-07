import random
from faker import Faker
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait

fake = Faker("tr_TR")

class CreateCustomerPage:
    PAGE_TITLE = (By.CSS_SELECTOR, "[data-testid='page-title']")

    STEPPER_STEP_1 = (By.CSS_SELECTOR, "[data-testid='stepper-step-1']")
    STEPPER_STEP_2 = (By.CSS_SELECTOR, "[data-testid='stepper-step-2']")
    STEPPER_STEP_3 = (By.CSS_SELECTOR, "[data-testid='stepper-step-3']")

    # --- Adım 1: Demografik Bilgi ---
    FIRST_NAME = (By.ID, "firstName")
    SECOND_NAME = (By.ID, "secondName")
    LAST_NAME = (By.ID, "lastName")
    BIRTH_DATE = (By.ID, "birthDate")
    GENDER = (By.ID, "gender")
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

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10, ignored_exceptions=(StaleElementReferenceException,))
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
        # value: "DD/MM/YYYY" (manuel test case'lerdeki gösterim). HTML date
        # input'u Selenium send_keys ile MM/DD/YYYY tuş sırası bekliyor (ampirik
        # olarak doğrulandı - 07/22/1992 -> value="1992-07-22" oluyor), bu yüzden
        # burada dönüştürülüyor.
        day, month, year = value.split("/")
        field = self.driver.find_element(*self.BIRTH_DATE)
        field.clear()
        field.send_keys(f"{month}/{day}/{year}")

    def is_birth_date_native_date_picker(self):
        # Birth Date gerçek uygulamada native <input type="date"> - tıklanınca
        # açılan takvim tarayıcı/OS seviyesinde render ediliyor, DOM'a
        # hiçbir calendar/datepicker paneli eklenmiyor (ampirik olarak
        # doğrulandı). Bu yüzden Selenium'la gerçek takvim gün hücrelerine
        # tıklamak mümkün değil - type="date" olması native picker'ın var
        # olacağının garantisi.
        return self.driver.find_element(*self.BIRTH_DATE).get_attribute("type") == "date"

    def enter_birth_date_with_faker(self):
        birth_date = fake.date_of_birth(minimum_age=18, maximum_age=90).strftime("%d/%m/%Y")
        self.enter_birth_date(birth_date)
        self._last_entered_birth_date = birth_date
        return birth_date

    def get_birth_date_iso_value(self):
        return self.driver.find_element(*self.BIRTH_DATE).get_attribute("value")

    def is_birth_date_displayed_correctly(self):
        day, month, year = self._last_entered_birth_date.split("/")
        expected_iso = f"{year}-{month}-{day}"
        return self.get_birth_date_iso_value() == expected_iso

    def click_gender_field(self):
        self.driver.find_element(*self.GENDER).click()

    def get_gender_options(self):
        return [o.text for o in Select(self.driver.find_element(*self.GENDER)).options]

    def select_gender(self, value):
        Select(self.driver.find_element(*self.GENDER)).select_by_visible_text(value)

    def enter_father_name(self, value):
        field = self.driver.find_element(*self.FATHER_NAME)
        field.clear()
        field.send_keys(value)

    def enter_mother_name(self, value):
        field = self.driver.find_element(*self.MOTHER_NAME)
        field.clear()
        field.send_keys(value)

    def enter_identity_number(self, value):
        field = self.driver.find_element(*self.IDENTITY_NUMBER)
        field.clear()
        field.send_keys(value)
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
        # veriliyor, Faker ile rastgele SEÇİLMİYOR: bu alan gerçek bir bug
        # içeriyor (ne seçilirse seçilsin sistem her zaman "Erkek" kaydediyor
        # - bkz. "Uçtan Uca Müşteri Yaratma" senaryosu). Senaryo hem "Kadın"
        # hem "Erkek" ile bilerek ayrı ayrı çalıştırılıyor ki bug'ın ASİMETRİK
        # doğası (Kadın seçilince FAIL, Erkek seçilince PASS - çünkü sistem
        # zaten hep Erkek yazıyor) net şekilde kanıtlansın.
        first_name = fake.first_name_female() if gender == "Kadın" else fake.first_name_male()
        last_name = fake.last_name()
        birth_date = fake.date_of_birth(minimum_age=18, maximum_age=90).strftime("%d/%m/%Y")
        identity_number = fake.numerify("###########")
        self.fill_demographic_step(first_name, last_name, birth_date, gender, identity_number)
        return first_name, last_name, birth_date, identity_number

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
        return last_name

    def get_first_name_value(self):
        return self.driver.find_element(*self.FIRST_NAME).get_attribute("value")

    def get_last_name_value(self):
        return self.driver.find_element(*self.LAST_NAME).get_attribute("value")

    def get_identity_number_value(self):
        return self.driver.find_element(*self.IDENTITY_NUMBER).get_attribute("value")

    def get_selected_gender_text(self):
        return Select(self.driver.find_element(*self.GENDER)).first_selected_option.text

    def are_demographic_values_displayed(self):
        day, month, year = self._last_birth_date.split("/")
        expected_iso_birth_date = f"{year}-{month}-{day}"
        return (
            self.get_first_name_value() == self._last_first_name
            and self.get_last_name_value() == self._last_last_name
            and self.driver.find_element(*self.BIRTH_DATE).get_attribute("value") == expected_iso_birth_date
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
        city_field = self.wait.until(EC.visibility_of_element_located(self.ADDRESS_CITY))
        Select(city_field).select_by_visible_text(city_name)
        # Not: native <select>'te Selenium'un select_by_visible_text'i her zaman
        # formun beklediği change/blur event'ini tetiklemiyor - tetiklenmezse
        # Kaydet butonu "Bu alan zorunludur" hatasıyla pasif kalmaya devam ediyor.
        self.driver.execute_script(
            "arguments[0].dispatchEvent(new Event('change', {bubbles:true}));"
            "arguments[0].dispatchEvent(new Event('input', {bubbles:true}));"
            "arguments[0].dispatchEvent(new Event('blur', {bubbles:true}));",
            city_field,
        )

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
        # Şehir Faker'dan DEĞİL, ekrandaki gerçek <select> seçeneklerinden
        # rastgele seçiliyor: address-city alanı yalnızca kendi option
        # listesindeki 81 il adından biriyle TAM eşleşirse kabul ediyor,
        # Faker'ın ürettiği bir şehir adının bu listeyle birebir eşleşeceği
        # garanti edilemez (örn. ilçe/kısaltma farkı).
        self.click_add_address()
        city_field = self.wait.until(EC.visibility_of_element_located(self.ADDRESS_CITY))
        real_city_options = [o.text for o in Select(city_field).options if o.get_attribute("value")]
        city = random.choice(real_city_options)
        street = fake.street_name()
        building_no = fake.building_number()
        description = fake.sentence(nb_words=4)
        self.select_address_city(city)
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
        real_city_options = [o.text for o in Select(city_field).options if o.get_attribute("value")]
        city = random.choice(real_city_options)
        self.select_address_city(city)
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
        city_value = Select(self.driver.find_element(*self.ADDRESS_CITY)).first_selected_option.text
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
