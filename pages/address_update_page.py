from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage
from utils.waits import poll_until


class AddressUpdatePage(BasePage):
    TAB_ADDRESS = (By.CSS_SELECTOR, "[data-testid='tab-address']")
    ADD_ADDRESS_BUTTON = (By.CSS_SELECTOR, "[data-testid='customer-address-add']")

    ADDRESS_CARD = (By.CSS_SELECTOR, "[data-testid='address-card']")
    ADDRESS_CARD_TITLE = (By.CSS_SELECTOR, "[data-testid='address-card-title']")
    ADDRESS_CARD_DETAIL = (By.CSS_SELECTOR, "[data-testid='address-card-detail']")
    ADDRESS_CARD_MENU = (By.CSS_SELECTOR, "[data-testid='address-card-menu']")
    ADDRESS_CARD_EDIT = (By.CSS_SELECTOR, "[data-testid='address-card-edit']")
    ADDRESS_CARD_DELETE = (By.CSS_SELECTOR, "[data-testid='address-card-delete']")
    ADDRESS_CARD_PRIMARY = (By.CSS_SELECTOR, "[data-testid='address-card-primary']")

    CITY_BUTTON = (By.ID, "address-city")
    CITY_LIST = (By.ID, "address-city-list")
    STREET_INPUT = (By.CSS_SELECTOR, "[data-testid='address-street']")
    BUILDING_INPUT = (By.CSS_SELECTOR, "[data-testid='address-building-no']")
    DESCRIPTION_INPUT = (By.CSS_SELECTOR, "[data-testid='address-description']")
    SAVE_BUTTON = (By.CSS_SELECTOR, "[data-testid='address-save']")
    CANCEL_BUTTON = (By.CSS_SELECTOR, "[data-testid='address-cancel']")

    # Metin tabanlı zorunlu alanlar - Şehir bir combobox (dropdown) olduğu
    # için her zaman bir değere sahip olmak zorunda, "boşaltma" kavramı
    # metin input'ları için geçerli (canlı doğrulandı).
    REQUIRED_TEXT_FIELD_LOCATORS = {
        "Sokak": STREET_INPUT,
        "Bina No": BUILDING_INPUT,
        "Açıklama": DESCRIPTION_INPUT,
    }

    def __init__(self, driver):
        super().__init__(driver)
        self.driver.find_element(*self.TAB_ADDRESS).click()
        self.wait.until(EC.visibility_of_element_located(self.ADDRESS_CARD))
        self._pre_edit_city = None
        self._pre_edit_street = None
        self._pre_edit_building_no = None
        self._pre_edit_description = None

    def get_card_count(self):
        return len(self.driver.find_elements(*self.ADDRESS_CARD))

    def _first_card_title_parts(self):
        title = self.driver.find_element(*self.ADDRESS_CARD_TITLE).text
        city, street, building_no = [p.strip() for p in title.split(",", 2)]
        return city, street, building_no

    def click_edit_first_card(self):
        city, street, building_no = self._first_card_title_parts()
        self._pre_edit_city = city
        self._pre_edit_street = street
        self._pre_edit_building_no = building_no
        self._pre_edit_description = self.driver.find_element(*self.ADDRESS_CARD_DETAIL).text
        self.wait.until(EC.element_to_be_clickable(self.ADDRESS_CARD_MENU)).click()
        self.wait.until(EC.element_to_be_clickable(self.ADDRESS_CARD_EDIT)).click()
        self.wait.until(EC.visibility_of_element_located(self.STREET_INPUT))

    def is_form_prefilled_correctly(self):
        city_value = self.driver.find_element(*self.CITY_BUTTON).text.strip()
        return (
            city_value == self._pre_edit_city
            and self.driver.find_element(*self.STREET_INPUT).get_attribute("value") == self._pre_edit_street
            and self.driver.find_element(*self.BUILDING_INPUT).get_attribute("value") == self._pre_edit_building_no
            and self.driver.find_element(*self.DESCRIPTION_INPUT).get_attribute("value") == self._pre_edit_description
        )

    def update_street_and_building(self, new_street, new_building_no):
        street_field = self.driver.find_element(*self.STREET_INPUT)
        street_field.click()
        street_field.send_keys(Keys.CONTROL + "a")
        street_field.send_keys(Keys.BACK_SPACE)
        street_field.send_keys(new_street)

        building_field = self.driver.find_element(*self.BUILDING_INPUT)
        building_field.click()
        building_field.send_keys(Keys.CONTROL + "a")
        building_field.send_keys(Keys.BACK_SPACE)
        building_field.send_keys(new_building_no)
        building_field.send_keys(Keys.TAB)

        self._new_street = new_street
        self._new_building_no = new_building_no

    def click_save(self):
        self.wait.until(EC.element_to_be_clickable(self.SAVE_BUTTON)).click()

    def click_cancel(self):
        self.wait.until(EC.element_to_be_clickable(self.CANCEL_BUTTON)).click()

    def is_edit_form_open(self):
        return bool(self.driver.find_elements(*self.STREET_INPUT))

    def is_card_updated_with_new_values(self):
        self.wait.until(
            lambda d: self._new_street in d.find_element(*self.ADDRESS_CARD_TITLE).text
        )
        title = self.driver.find_element(*self.ADDRESS_CARD_TITLE).text
        return self._new_street in title and self._new_building_no in title

    def is_card_showing_original_values(self):
        title = self.driver.find_element(*self.ADDRESS_CARD_TITLE).text
        return (
            not self.is_edit_form_open()
            and title == f"{self._pre_edit_city}, {self._pre_edit_street}, {self._pre_edit_building_no}"
        )

    def is_card_title_and_detail_well_formed(self):
        # "Şehir, Sokak, No" formatı + açıklamanın eksiksiz görüntülenmesini
        # dil/içerikten bağımsız, YAPISAL olarak doğruluyor: başlıkta TAM
        # OLARAK 2 virgül (3 parça: şehir/sokak/no) olmalı, açıklama boş
        # olmamalı.
        title = self.driver.find_element(*self.ADDRESS_CARD_TITLE).text
        detail = self.driver.find_element(*self.ADDRESS_CARD_DETAIL).text
        parts = [p.strip() for p in title.split(",")]
        return len(parts) == 3 and all(parts) and bool(detail.strip())

    def clear_required_text_field(self, field_label):
        locator = self.REQUIRED_TEXT_FIELD_LOCATORS[field_label]
        field = self.driver.find_element(*locator)
        field.click()
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACK_SPACE)
        field.send_keys(Keys.TAB)

    def is_save_button_disabled(self):
        return not self.driver.find_element(*self.SAVE_BUTTON).is_enabled()

    def attempt_to_type_long_description(self, length):
        # Klavye ile binlerce karakter yazmak çok yavaş olacağından, native
        # value setter + input event ile JS üzerinden yazılıyor (gerçek
        # kullanıcı deneyimini DOM/Angular seviyesinde birebir simüle
        # ediyor - session boyunca doğrulanmış bir teknik).
        field = self.driver.find_element(*self.DESCRIPTION_INPUT)
        self.driver.execute_script(
            "const el = arguments[0];"
            "const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;"
            "setter.call(el, arguments[1]);"
            "el.dispatchEvent(new Event('input', {bubbles: true}));",
            field,
            "a" * length,
        )
        return field.get_attribute("value")

    def attempt_to_type_long_value_in_text_field(self, field_label, length):
        # attempt_to_type_long_description() ile AYNI JS native value-setter
        # tekniği (klavye ile binlerce karakter yazmak yerine performans
        # için) - ama STREET_INPUT/BUILDING_INPUT birer <input>
        # (DESCRIPTION_INPUT'un <textarea> olmasının aksine), bu yüzden
        # HTMLInputElement prototype kullanılıyor
        # (billing_account_create_page.py'deki type_long_account_name() ile
        # AYNI desen). REQUIRED_TEXT_FIELD_LOCATORS dict'i yeniden
        # kullanılıyor - Sokak/Bina No/Açıklama etiketleri zaten orada
        # tanımlı (DRY, TC-EACRML-006-03 ile AYNI dinamik eşleme).
        locator = self.REQUIRED_TEXT_FIELD_LOCATORS[field_label]
        field = self.driver.find_element(*locator)
        self.driver.execute_script(
            "const el = arguments[0];"
            "const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;"
            "setter.call(el, arguments[1]);"
            "el.dispatchEvent(new Event('input', {bubbles: true}));",
            field,
            "a" * length,
        )
        return field.get_attribute("value")

    def click_add_address(self):
        self.wait.until(EC.element_to_be_clickable(self.ADD_ADDRESS_BUTTON)).click()
        self.wait.until(EC.visibility_of_element_located(self.STREET_INPUT))

    def add_address_with_faker(self, street, building_no, description):
        import random

        # before_count'a göre ARTIŞ bekleniyor (sabit ">= 2" değil) -
        # ikinciden fazla adres eklenen senaryolarda (ör. 3. adres) sabit
        # ">= 2" koşulu, gerçek ekleme gerçekleşmeden ÖNCE bile zaten
        # doğru dönüp sahte-PASS'e yol açabilirdi.
        before_count = len(self.driver.find_elements(*self.ADDRESS_CARD))
        self.driver.find_element(*self.CITY_BUTTON).click()
        self.wait.until(EC.visibility_of_element_located(self.CITY_LIST))
        options = self.driver.find_elements(By.CSS_SELECTOR, "#address-city-list li[role='option']")
        random.choice(options).click()
        self.driver.find_element(*self.STREET_INPUT).send_keys(street)
        self.driver.find_element(*self.BUILDING_INPUT).send_keys(building_no)
        self.driver.find_element(*self.DESCRIPTION_INPUT).send_keys(description)
        self.click_save()
        self.wait.until(lambda d: len(d.find_elements(*self.ADDRESS_CARD)) > before_count)

    def get_primary_states(self):
        radios = self.driver.find_elements(*self.ADDRESS_CARD_PRIMARY)
        return [r.is_selected() for r in radios]

    def mark_second_address_as_primary(self):
        radios = self.driver.find_elements(*self.ADDRESS_CARD_PRIMARY)
        # Radio görsel olarak gizli (sr-only), yalnızca CSS ile stilize
        # edilmiş bir gösterge görünür - native .click() elementin
        # kendisine ulaşamıyor (ElementClickIntercepted, canlı doğrulandı),
        # bu yüzden JS click kullanılıyor.
        self.driver.execute_script("performance.clearResourceTimings();")
        self.driver.execute_script("arguments[0].click();", radios[1])
        self.wait.until(lambda d: d.find_elements(*self.ADDRESS_CARD_PRIMARY)[1].is_selected())

        # DÜZELTME (bugsbunny.txt madde 18 - TC-006-06b flaky'sinin GERÇEK
        # kök nedeni, Performance API ile canlı ÖLÇÜLDÜ):
        #   tıklama            -> +0.00sn
        #   DOM radio checked  -> +0.04sn   (yukarıdaki bekleme burada biter)
        #   PATCH /v1/addresses/{id} tamamlandı -> +0.33sn
        # Yani metot, istek daha UÇUŞTAYKEN dönüyordu. Çağıran taraf hemen
        # driver.get() yapınca navigasyon isteği İPTAL ediyor ve değişiklik
        # hiç kaydedilmiyordu - reload'ları ne kadar tekrarlarsak
        # tekrarlayalım durum asla düzelmiyordu (izole koşumda 2/3 FAILED).
        #
        # DOM'da radio'nun "checked" olması İSTEMCİ TARAFI bir durumdur ve
        # sunucuya yazıldığı anlamına GELMEZ. Bu yüzden istek gerçekten
        # tamamlanana kadar bekleniyor - sabit bir süre değil, olayın
        # kendisi yoklanıyor (responseEnd, iptal edilen isteklerde 0 kalır).
        self.wait.until(
            lambda d: d.execute_script(
                "return performance.getEntriesByType('resource')"
                "  .some(e => /\\/addresses\\/\\d+/.test(e.name) && e.responseEnd > 0);"
            )
        )

    def wait_for_primary_states_to_persist(self, expected_states):
        # Canlı doğrulandı: Primary değişikliği backend'e ANINDA değil,
        # ASENKRON/gecikmeli persist ediliyor - tıklamadan hemen sonra
        # yapılan bir reload'da HÂLÂ eski durum görünüyor, birkaç saniye
        # sonraki bir reload'da ise doğru/beklenen durum görünüyor. Bu,
        # sabit bir time.sleep ile "tahmin edilen" bir süre beklemek
        # yerine, eylemi (reload) tekrarlayan bir yoklama döngüsüyle durum
        # GERÇEKTEN beklenen hale gelene kadar bekleniyor - hem gecikmeli
        # persist'i adil şekilde tolere ediyor hem de GERÇEKTEN hiç
        # kaydedilmiyorsa (gerçek bug) denemeler tükenince FAIL veriyor.
        #
        # DÜZELTME (bugsbunny.txt madde 18 - tam suite koşumunda flaky
        # olarak yakalandı): eski implementasyon reload'ı WebDriverWait
        # predicate'inin İÇİNDE yapıyordu, yani ~0.5sn'lik polling
        # aralığıyla SIKI/hızlı ardışık reload. Bu tam olarak
        # delete_customer_page.py'de canlı yakalanıp terk edilen desen:
        # hızlı ardışık reload'lar uygulamanın token-yenileme mantığını
        # zorluyor ve asenkron persist'e yeterli zaman TANIMIYOR. Çözüm
        # orada kanıtlanmış olanla aynı: poll_until ile BİLEREK DAHA
        # SEYREK (varsayılan 2sn arayla, en fazla 6 deneme) yoklamak.
        detail_url = self.driver.current_url
        self._last_reload_primary_states = None

        def _reload_address_tab():
            self.driver.get(detail_url)
            self.wait.until(EC.element_to_be_clickable(self.TAB_ADDRESS)).click()
            self.wait.until(EC.visibility_of_element_located(self.ADDRESS_CARD_PRIMARY))

        def _states_match():
            self._last_reload_primary_states = self.get_primary_states()
            return self._last_reload_primary_states == expected_states

        poll_until(condition=_states_match, action=_reload_address_tab)
        # Durum döndürülüyor, iddia step katmanında (bkz. §4.2b) - eşleşme
        # olmasa dahi SON okunan durum döner, böylece hata mesajı gerçekte
        # ne görüldüğünü gösterir.
        return self._last_reload_primary_states

    def is_single_address_primary_and_unchangeable(self):
        radios = self.driver.find_elements(*self.ADDRESS_CARD_PRIMARY)
        # "Değiştirilemez" iddiası teknik bir disabled özniteliği DEĞİL,
        # mantıksal bir sonuç (canlı doğrulandı: radio disabled değil) -
        # değiştirilecek İKİNCİ bir adres/radio hiç yok, bu yüzden tek
        # mevcut seçenek zaten Primary olmak ZORUNDA.
        return len(radios) == 1 and radios[0].is_selected()
