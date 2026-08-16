import random

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage
from utils.test_data import fake


class BillingAccountCreatePage(BasePage):
    # "Fatura Hesabı Oluştur" formu (panel-heading canlı doğrulandı), Adres
    # sekmesindeki adres ekleme formuyla AYNI alt-bileşeni ("Yeni Adres
    # Ekle") gömülü olarak kullanıyor - bu yüzden NEW_ADDRESS_* locator'ları
    # pages/address_add_page.py'deki karşılıklarıyla BİREBİR aynı CSS
    # değerlerine sahip (kasıtlı küçük bir tekrar - bu sayfa kavramsal
    # olarak bir "adres sayfası" DEĞİL, inheritance burada "is-a" ilişkisini
    # bozacağından tercih edilmedi).

    TAB_ACCOUNT = (By.CSS_SELECTOR, "[data-testid='tab-account']")
    CREATE_BUTTON = (By.CSS_SELECTOR, "[data-testid='customer-account-create']")
    EMPTY_STATE = (By.CSS_SELECTOR, "[data-testid='empty-state']")
    EMPTY_STATE_MESSAGE = (By.CSS_SELECTOR, "[data-testid='empty-state-message']")

    ACCOUNT_NAME_INPUT = (By.CSS_SELECTOR, "[data-testid='account-name']")
    ACCOUNT_NAME_ERROR = (By.CSS_SELECTOR, "[data-testid='account-name-error']")
    ACCOUNT_DESCRIPTION_INPUT = (By.CSS_SELECTOR, "[data-testid='account-description']")
    ACCOUNT_DESCRIPTION_ERROR = (By.CSS_SELECTOR, "[data-testid='account-description-error']")

    ADDRESS_CARD = (By.CSS_SELECTOR, "[data-testid='address-card']")
    ADDRESS_CARD_TITLE = (By.CSS_SELECTOR, "[data-testid='address-card-title']")
    # Bu formda ayni radio bileseni "hizmet adresi secimi" anlaminda
    # kullaniliyor (Adres sekmesindeki "Primary" anlaminin AKSINE - canli
    # dogrulandi, ayni testid farkli baglamda tekrar kullaniliyor).
    ADDRESS_SERVICE_SELECT = (By.CSS_SELECTOR, "[data-testid='address-card-primary']")
    ADD_ADDRESS_BUTTON = (By.CSS_SELECTOR, "[data-testid='account-add-address']")

    NEW_ADDRESS_CITY_BUTTON = (By.ID, "address-city")
    NEW_ADDRESS_CITY_LIST = (By.ID, "address-city-list")
    NEW_ADDRESS_STREET_INPUT = (By.CSS_SELECTOR, "[data-testid='address-street']")
    NEW_ADDRESS_BUILDING_INPUT = (By.CSS_SELECTOR, "[data-testid='address-building-no']")
    NEW_ADDRESS_DESCRIPTION_INPUT = (By.CSS_SELECTOR, "[data-testid='address-description']")
    NEW_ADDRESS_SAVE_BUTTON = (By.CSS_SELECTOR, "[data-testid='address-save']")

    CANCEL_BUTTON = (By.CSS_SELECTOR, "[data-testid='account-cancel']")
    SAVE_BUTTON = (By.CSS_SELECTOR, "[data-testid='account-save']")

    ACCOUNT_ROW = (By.CSS_SELECTOR, "[data-testid='account-row']")
    ACCOUNT_ROW_TOGGLE = (By.CSS_SELECTOR, "[data-testid='account-row-toggle']")
    ACCOUNT_ROW_NUMBER = (By.CSS_SELECTOR, "[data-testid='account-row-number']")
    ACCOUNT_ROW_NAME = (By.CSS_SELECTOR, "[data-testid='account-row-name']")
    ACCOUNT_ROW_TYPE = (By.CSS_SELECTOR, "[data-testid='account-row-type']")
    PAGINATION = (By.CSS_SELECTOR, "[data-testid='pagination']")

    def __init__(self, driver):
        super().__init__(driver)
        self.driver.find_element(*self.TAB_ACCOUNT).click()
        self.wait.until(EC.visibility_of_element_located(self.CREATE_BUTTON))

    def get_account_row_count(self):
        return len(self.driver.find_elements(*self.ACCOUNT_ROW))

    def is_empty_state_displayed(self):
        # Mesaj metni dile göre değişebileceğinden yapısal olarak (mesaj
        # elementinin görünür VE dolu olması) kontrol ediliyor - projedeki
        # diğer empty-state kontrolleriyle (search/delete_customer) tutarlı.
        # Bir silme işleminin HEMEN ardından çağrıldığında Angular'ın
        # DOM'u yeniden render etmesiyle (boş durum bileşeninin
        # oluşturulmasıyla) yarışabiliyor (canlı doğrulandı - ara sıra
        # StaleElementReferenceException) - bu yüzden anlık tek bir
        # find_elements yerine, stale durumunu KENDİ İÇİNDE tolere edip
        # yeniden deneyen dinamik bir WebDriverWait predicate'i kullanılıyor.
        def _message_visible_and_filled(driver):
            try:
                message = driver.find_element(*self.EMPTY_STATE_MESSAGE)
                return message.is_displayed() and bool(message.text.strip())
            except (NoSuchElementException, StaleElementReferenceException):
                return False

        try:
            return self.wait.until(_message_visible_and_filled)
        except TimeoutException:
            return False

    def click_create_account(self):
        self.wait.until(EC.element_to_be_clickable(self.CREATE_BUTTON)).click()
        self.wait.until(EC.visibility_of_element_located(self.ACCOUNT_NAME_INPUT))

    def is_create_form_open(self):
        return bool(self.driver.find_elements(*self.ACCOUNT_NAME_INPUT))

    def fill_account_name(self, value):
        self.fill(self.ACCOUNT_NAME_INPUT, value)

    def fill_account_description(self, value):
        self.fill(self.ACCOUNT_DESCRIPTION_INPUT, value)

    def _generate_account_name_and_description(self):
        name = f"Hesap {fake.word().title()} {fake.random_number(digits=4, fix_len=True)}"
        description = fake.sentence(nb_words=4)
        return name, description

    def fill_required_fields_with_faker(self):
        # Adres alanı dışarıda bırakılıyor - müşterinin en az 1 kayıtlı
        # adresi her zaman olduğundan (create_customer akışının garantisi)
        # ve formda İLK adres varsayılan olarak zaten seçili geldiğinden
        # (canlı doğrulandı) ayrıca bir seçim yapmaya gerek yok.
        name, description = self._generate_account_name_and_description()
        self.fill_account_name(name)
        self.fill_account_description(description)
        return name, description

    def clear_account_name(self):
        self.fill(self.ACCOUNT_NAME_INPUT, blur=True)

    def _is_error_displayed(self, locator):
        try:
            self.wait.until(EC.visibility_of_element_located(locator))
        except TimeoutException:
            return False
        return bool(self.driver.find_element(*locator).text.strip())

    def is_account_name_error_displayed(self):
        return self._is_error_displayed(self.ACCOUNT_NAME_ERROR)

    def is_save_button_disabled(self):
        return not self.driver.find_element(*self.SAVE_BUTTON).is_enabled()

    def attempt_click_disabled_save(self):
        try:
            self.driver.find_element(*self.SAVE_BUTTON).click()
        except (ElementNotInteractableException, ElementClickInterceptedException):
            pass

    def get_address_selection_states(self):
        return [r.is_selected() for r in self.driver.find_elements(*self.ADDRESS_SERVICE_SELECT)]

    def get_address_card_titles(self):
        return [e.text for e in self.driver.find_elements(*self.ADDRESS_CARD_TITLE)]

    def select_service_address_by_index(self, index):
        # Radio görsel olarak gizli (Adres sekmesindeki Primary radio ile
        # aynı bileşen/desen) - native .click() ElementClickIntercepted
        # veriyor, JS click kullanılıyor (canlı doğrulandı).
        radios = self.driver.find_elements(*self.ADDRESS_SERVICE_SELECT)
        self.driver.execute_script("arguments[0].click();", radios[index])
        self.wait.until(lambda d: d.find_elements(*self.ADDRESS_SERVICE_SELECT)[index].is_selected())

    def add_new_service_address(self, street, building_no, description):
        before_count = len(self.driver.find_elements(*self.ADDRESS_CARD))
        self.wait.until(EC.element_to_be_clickable(self.ADD_ADDRESS_BUTTON)).click()
        self.wait.until(EC.visibility_of_element_located(self.NEW_ADDRESS_STREET_INPUT))

        self.driver.find_element(*self.NEW_ADDRESS_CITY_BUTTON).click()
        self.wait.until(EC.visibility_of_element_located(self.NEW_ADDRESS_CITY_LIST))
        options = self.driver.find_elements(By.CSS_SELECTOR, "#address-city-list li[role='option']")
        random.choice(options).click()

        self.driver.find_element(*self.NEW_ADDRESS_STREET_INPUT).send_keys(street)
        self.driver.find_element(*self.NEW_ADDRESS_BUILDING_INPUT).send_keys(building_no)
        self.driver.find_element(*self.NEW_ADDRESS_DESCRIPTION_INPUT).send_keys(description)
        self.driver.find_element(*self.NEW_ADDRESS_SAVE_BUTTON).click()
        self.wait.until(lambda d: len(d.find_elements(*self.ADDRESS_CARD)) > before_count)
        self._new_address_street = street
        self._new_address_building_no = building_no

    def is_newest_address_selected_as_service_address(self):
        # Canlı doğrulandı: yeni eklenen adres listenin SONUNA ekleniyor
        # VE otomatik olarak hizmet adresi olarak seçili hale geliyor.
        titles = self.get_address_card_titles()
        states = self.get_address_selection_states()
        last_title = titles[-1]
        return (
            self._new_address_street in last_title
            and self._new_address_building_no in last_title
            and states[-1] is True
        )

    def click_save(self):
        self.wait.until(EC.element_to_be_clickable(self.SAVE_BUTTON)).click()

    def click_cancel(self):
        self.wait.until(EC.element_to_be_clickable(self.CANCEL_BUTTON)).click()

    def create_account_and_wait(self, name=None, description=None):
        # name/description BAĞIMSIZ olarak varsayılana düşer - önceki
        # sürümde "ikisinden biri eksikse İKİSİNİ DE Faker'a ez" gibi
        # yanlış bir "or" mantığı vardı: sadece name verilip description
        # verilmediğinde name'in KENDİSİ de rastgele bir değerle
        # değiştiriliyordu (canlı çalıştırmada AttributeError/satır
        # bulunamama olarak ortaya çıktı - gerçek bir bug, sahte-PASS
        # değil ama sessizce yanlış veri üretiyordu).
        self.click_create_account()
        faker_name, faker_description = self._generate_account_name_and_description()
        used_name = name if name is not None else faker_name
        used_description = description if description is not None else faker_description
        self.fill_account_name(used_name)
        self.fill_account_description(used_description)
        before_count = self.get_account_row_count()
        self.click_save()
        self.wait.until(lambda d: len(d.find_elements(*self.ACCOUNT_ROW)) > before_count)
        return used_name

    def find_account_row_by_name(self, name):
        # Bir silme/oluşturma işleminin HEMEN ardından çağrıldığında,
        # Angular listeyi yeniden render ederken (satır ekleniyor/
        # kaldırılıyorken) find_elements ile toplanan satır referansları
        # ARALARINDA stale kalabiliyor (canlı doğrulandı - ara sıra
        # StaleElementReferenceException). Bu, "satır bulunamadı" (None)
        # durumundan YAPISAL OLARAK FARKLI bir durum - bu yüzden sadece
        # GEÇİCİ stale hatasında taramanın TAMAMI (sabit, küçük bir üst
        # sınırla) yeniden deneniyor; "gerçekten bulunamadı" sonucu
        # (None) beklenmeden hemen döndürülüyor (absence testleri için
        # yanlışlıkla sonsuz beklemeye girmemek adına).
        for _ in range(5):
            try:
                for row in self.driver.find_elements(*self.ACCOUNT_ROW):
                    if row.find_element(*self.ACCOUNT_ROW_NAME).text == name:
                        return row
                return None
            except StaleElementReferenceException:
                continue
        return None

    def is_account_listed_with_generated_number_and_status(self, name):
        row = self.find_account_row_by_name(name)
        if row is None:
            return False
        number_text = row.find_element(*self.ACCOUNT_ROW_NUMBER).text.strip()
        status_text = row.find_element(*self.ACCOUNT_ROW_TOGGLE).text.strip()
        # Hesap numarasının GERÇEKTEN otomatik/dinamik üretildiğini (sabit/
        # hardcoded bir değer olmadığını) doğrulamak için sayısal karakter
        # içerdiği kontrol ediliyor - "Aktif" gibi dile bağlı bir literal
        # metinle KARŞILAŞTIRILMIYOR, sadece durum bilgisinin dolu/
        # görüntüleniyor olması yeterli sayılıyor.
        return bool(number_text) and any(ch.isdigit() for ch in number_text) and bool(status_text)

    def wait_for_account_persisted_after_reload(self, name):
        # address_add/address_delete'teki reload-tabanlı kalıcılık
        # deseniyle tutarlı: gerçek bir backend yazımının kanıtı olarak
        # sayfa TAMAMEN yenilendikten SONRA da hesabın hâlâ listede
        # olduğu dinamik WebDriverWait polling ile doğrulanıyor.
        detail_url = self.driver.current_url

        def account_present_after_reload(driver):
            driver.get(detail_url)
            self.wait.until(EC.element_to_be_clickable(self.TAB_ACCOUNT)).click()
            self.wait.until(
                lambda d: d.find_elements(*self.ACCOUNT_ROW) or d.find_elements(*self.EMPTY_STATE_MESSAGE)
            )
            return self.find_account_row_by_name(name) is not None

        try:
            return self.wait.until(account_present_after_reload)
        except TimeoutException:
            return False

    def type_long_account_name(self, length):
        # Adres Açıklaması alanında daha önce kullanılan JS native
        # value-setter tekniğinin AYNISI - klavye ile binlerce karakter
        # yazmak yerine performans için tercih ediliyor.
        field = self.driver.find_element(*self.ACCOUNT_NAME_INPUT)
        self.driver.execute_script(
            "const el = arguments[0];"
            "const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;"
            "setter.call(el, arguments[1]);"
            "el.dispatchEvent(new Event('input', {bubbles: true}));",
            field,
            "a" * length,
        )
        return field.get_attribute("value")

    def has_defined_columns_for_row(self, name):
        # "Sütunlar" yapısal olarak doğrulanıyor (dilden bağımsız): ilgili
        # satırda Hesap Adı/Numarası/Tipi/Durum alanlarının HEPSİNİN
        # görüntülenir olması, tablo başlığı metnine bakılmıyor.
        row = self.find_account_row_by_name(name)
        if row is None:
            return False
        return (
            row.find_element(*self.ACCOUNT_ROW_NAME).is_displayed()
            and row.find_element(*self.ACCOUNT_ROW_NUMBER).is_displayed()
            and row.find_element(*self.ACCOUNT_ROW_TYPE).is_displayed()
            and row.find_element(*self.ACCOUNT_ROW_TOGGLE).is_displayed()
        )

    def is_pagination_displayed_and_functional(self):
        paginations = self.driver.find_elements(*self.PAGINATION)
        if not paginations or not paginations[0].is_displayed():
            return False
        page_buttons = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid^='pagination-page-']")
        if len(page_buttons) < 2:
            return False
        rows_before = {
            row.find_element(*self.ACCOUNT_ROW_NAME).text for row in self.driver.find_elements(*self.ACCOUNT_ROW)
        }
        self.wait.until(EC.element_to_be_clickable(page_buttons[1])).click()
        self.wait.until(
            lambda d: {
                row.find_element(*self.ACCOUNT_ROW_NAME).text for row in d.find_elements(*self.ACCOUNT_ROW)
            }
            != rows_before
        )
        rows_after = {
            row.find_element(*self.ACCOUNT_ROW_NAME).text for row in self.driver.find_elements(*self.ACCOUNT_ROW)
        }
        return bool(rows_after) and not (rows_after & rows_before)

    def is_table_hidden_when_empty(self):
        return self.is_empty_state_displayed() and self.get_account_row_count() == 0
