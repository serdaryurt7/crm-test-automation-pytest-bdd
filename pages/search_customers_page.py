import random
import re

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage
from utils.waits import poll_until

# Türkçe alfabeye özgü büyük/küçük harf ve aksan farklarını (İ/I/ı/i,
# ğ/Ğ, ş/Ş, ç/Ç, ö/Ö, ü/Ü) normalize eden dönüşüm tablosu. Canlı olarak
# doğrulandı: uygulamanın kendi arama motoru ZATEN bu şekilde aksan/harf
# duyarsız eşleştiriyor (ör. "Yılmaz" araması hem "Yılmaz" hem "Yilmaz"
# yazılışını döndürüyor - gerçek veride, muhtemelen Faker'ın tr_TR
# sağlayıcısının ara sıra üreteceği ASCII-transliterasyonlu bir kayıttan
# ötürü) - testin karşılaştırması bunu YAKALAYAMADIĞINDA (Python'ın
# varsayılan str eşitliği/`.startswith()` aksan DUYARLI) sonuç kümesi
# içeriğinde hiçbir gerçek hata yokken TimeoutException ile FAILED
# veriyordu (bkz. bugsbunny.txt madde 10-14). Kök neden veri SAYISI drifti
# değil, karşılaştırmanın uygulamanın kendi eşleştirme toleransından DAHA
# KATI olmasıydı - düzeltme test verisini değiştirmek değil, karşılaştırmayı
# uygulamayla AYNI toleransa getirmek.
_TURKISH_FOLD_MAP = str.maketrans(
    {
        "ı": "i", "İ": "i", "I": "i",
        "ğ": "g", "Ğ": "g",
        "ş": "s", "Ş": "s",
        "ç": "c", "Ç": "c",
        "ö": "o", "Ö": "o",
        "ü": "u", "Ü": "u",
    }
)


def _turkish_fold(text):
    return text.translate(_TURKISH_FOLD_MAP).lower()


class CustomersPage(BasePage):
    # Sayfa başlığı
    PAGE_TITLE = (By.CSS_SELECTOR, "[data-testid='page-title']")
    PAGE_SUBTITLE = (By.CSS_SELECTOR, "[data-testid='page-subtitle']")

    # Arama formu (gerçek HTML id'si olanlar By.ID, olmayanlar data-testid CSS selector)
    SEARCH_FORM = (By.CSS_SELECTOR, "[data-testid='customer-search-form']")
    TYPE_B2C = (By.CSS_SELECTOR, "[data-testid='customer-type-b2c']")
    TYPE_B2B = (By.CSS_SELECTOR, "[data-testid='customer-type-b2b']")
    IDENTITY_NUMBER = (By.ID, "identityNumber")
    CUSTOMER_ID = (By.ID, "customerId")
    ACCOUNT_NUMBER = (By.ID, "accountNumber")
    GSM = (By.ID, "gsm")
    GSM_COUNTRY = (By.CSS_SELECTOR, "[data-testid='customer-search-gsm-country']")
    FIRST_NAME = (By.ID, "firstName")
    LAST_NAME = (By.ID, "lastName")
    ORDER_NUMBER = (By.ID, "orderNumber")
    SEARCH_CLEAR = (By.CSS_SELECTOR, "[data-testid='customer-search-clear']")
    SEARCH_SUBMIT = (By.CSS_SELECTOR, "[data-testid='customer-search-submit']")

    SEARCH_FIELDS = (
        IDENTITY_NUMBER,
        CUSTOMER_ID,
        ACCOUNT_NUMBER,
        GSM,
        FIRST_NAME,
        LAST_NAME,
        ORDER_NUMBER,
    )

    # Sonuç tablosu
    RESULTS_TABLE = (By.CSS_SELECTOR, "[data-testid='customer-results']")
    RESULTS_COUNT = (By.CSS_SELECTOR, "[data-testid='customer-results-count']")
    RESULTS_RANGE = (By.CSS_SELECTOR, "[data-testid='customer-results-range']")
    EMPTY_STATE = (By.CSS_SELECTOR, "[data-testid='empty-state']")
    EMPTY_STATE_MESSAGE = (By.CSS_SELECTOR, "[data-testid='empty-state-message']")
    CREATE_CUSTOMER_BUTTON = (By.CSS_SELECTOR, "a[data-testid='customer-results-create']")
    SORT_CUSTOMER_ID = (By.CSS_SELECTOR, "[data-testid='customer-results-sort-customerId']")
    SORT_FIRST_NAME = (By.CSS_SELECTOR, "[data-testid='customer-results-sort-firstName']")
    SORT_SECOND_NAME = (By.CSS_SELECTOR, "[data-testid='customer-results-sort-secondName']")
    SORT_LAST_NAME = (By.CSS_SELECTOR, "[data-testid='customer-results-sort-lastName']")
    SORT_ROLE = (By.CSS_SELECTOR, "[data-testid='customer-results-sort-role']")
    SORT_NATIONALITY_ID = (By.CSS_SELECTOR, "[data-testid='customer-results-sort-nationalityId']")

    # Sayfalama (sayfa numarası butonları sonuç sayısına göre değiştiği için
    # sabit locator yerine page_button(n) metoduyla dinamik üretiliyor)
    PAGINATION = (By.CSS_SELECTOR, "[data-testid='customer-results-pagination']")
    PREV_PAGE = (By.CSS_SELECTOR, "[data-testid='customer-results-prev-page']")
    NEXT_PAGE = (By.CSS_SELECTOR, "[data-testid='customer-results-next-page']")

    # Satır şablonu: DOM'da her biri sayfadaki satır sayısı kadar (15x) tekrar
    # ediyor, TEK BAŞINA unique DEĞİL - find_elements ile veya bir <tr>
    # WebElement'i üzerinden relative aramada kullanılmalı.
    ROW = (By.CSS_SELECTOR, "[data-testid='customer-row']")
    ROW_LINK = (By.CSS_SELECTOR, "[data-testid='customer-row-link']")
    ROW_FIRST_NAME = (By.CSS_SELECTOR, "[data-testid='customer-row-first-name']")
    ROW_SECOND_NAME = (By.CSS_SELECTOR, "[data-testid='customer-row-second-name']")
    ROW_LAST_NAME = (By.CSS_SELECTOR, "[data-testid='customer-row-last-name']")
    ROW_ROLE = (By.CSS_SELECTOR, "[data-testid='customer-row-role']")
    ROW_IDENTITY = (By.CSS_SELECTOR, "[data-testid='customer-row-identity']")

    # Sıralanabilir sütun etiketi -> (sort header locator / satır değeri
    # locator) eşlemesi. Etiketler ekrandaki o an aktif dilin metnine değil
    # sabit bir Python sözlüğüne bağlı (create_customer_page.py'deki
    # GENDER_VALUE_MAP ile aynı desen) - hangi UI dili aktifken koşulursa
    # koşulsun aynı data-testid'ler tıklanır/okunur, dilden bağımsız.
    # "Rol" kasıtlı olarak dahil edilmedi - bkz. search_customers.feature
    # üst yorumu (mevcut veride tüm kayıtların Role'ü aynı, sıra değişikliği
    # gözlemlenemez).
    SORT_LOCATORS = {
        "Customer ID": SORT_CUSTOMER_ID,
        "Ad": SORT_FIRST_NAME,
        "İkinci Ad": SORT_SECOND_NAME,
        "Soyad": SORT_LAST_NAME,
        "Kimlik No": SORT_NATIONALITY_ID,
    }
    SORT_ROW_VALUE_LOCATORS = {
        "Customer ID": ROW_LINK,
        "Ad": ROW_FIRST_NAME,
        "İkinci Ad": ROW_SECOND_NAME,
        "Soyad": ROW_LAST_NAME,
        "Kimlik No": ROW_IDENTITY,
    }

    # Müşteri Detayı (Customer Info) ekranı
    CUSTOMER_DETAIL_HEADER = (By.CSS_SELECTOR, "[data-testid='customer-detail-header']")

    def __init__(self, driver):
        # Not: BasePage zaten ignored_exceptions=(StaleElementReferenceException,)
        # kuruyor - bu sayfada ELDE EDİLEN davranış birebir aynı, yalnızca
        # tanım tek yere taşındı.
        super().__init__(driver)
        self.wait.until(EC.visibility_of_element_located(self.SEARCH_SUBMIT))
        self._last_identity_number = None
        self._last_customer_id = None

    def is_search_button_disabled(self):
        return not self.driver.find_element(*self.SEARCH_SUBMIT).is_enabled()

    def clear_all_search_fields(self):
        for locator in self.SEARCH_FIELDS:
            field = self.driver.find_element(*locator)
            if field.get_attribute("value"):
                field.clear()

    def page_button(self, page_number):
        return (By.CSS_SELECTOR, f"[data-testid='customer-results-page-{page_number}']")

    def are_all_search_fields_visible(self):
        return all(self.driver.find_element(*locator).is_displayed() for locator in self.SEARCH_FIELDS)

    def are_search_buttons_visible(self):
        return (
            self.driver.find_element(*self.SEARCH_SUBMIT).is_displayed()
            and self.driver.find_element(*self.SEARCH_CLEAR).is_displayed()
        )

    def is_b2c_active(self):
        return self.driver.find_element(*self.TYPE_B2C).get_attribute("aria-pressed") == "true"

    def is_b2b_inactive(self):
        return not self.driver.find_element(*self.TYPE_B2B).is_enabled()

    def try_click_b2b(self):
        self.driver.find_element(*self.TYPE_B2B).click()

    def enter_identity_number(self, value):
        field = self.driver.find_element(*self.IDENTITY_NUMBER)
        field.clear()
        field.send_keys(value)
        self._last_identity_number = value

    def get_identity_number_value(self):
        return self.driver.find_element(*self.IDENTITY_NUMBER).get_attribute("value")

    def submit_search(self):
        self.wait.until(EC.element_to_be_clickable(self.SEARCH_SUBMIT)).click()

    def wait_for_matching_customer(self):
        self.wait.until(
            lambda d: [e.text.strip() for e in d.find_elements(*self.ROW_IDENTITY)] == [self._last_identity_number]
        )

    def wait_for_empty_state_message(self, expected_text):
        self.wait.until(lambda d: d.find_element(*self.EMPTY_STATE_MESSAGE).text == expected_text)

    def wait_for_identity_number_length_validation_error(self):
        # Dilden bağımsız: TR ("...11 haneli...") ve EN (muhtemelen
        # "...11-digit...") mesaj metinleri farklı kelimelerle yazılsa da
        # İKİSİNDE DE ORTAK olan tek değişmez unsur "11" rakamının kendisi -
        # literal kelime karşılaştırması yerine bu doğrulanıyor. Aynı
        # EMPTY_STATE_MESSAGE elementi "sonuç bulunamadı" durumuyla da
        # paylaşıldığından ("Arama kriterlerine uygun müşteri bulunamadı."
        # mesajında "11" GEÇMİYOR), yalnızca "boş değil" kontrolü yeterince
        # ayırt edici olmazdı - "11" içeriği bu iki durumu güvenle ayırıyor.
        # Not: EC.visibility_of_element_located() ile elementi BULUP sonra
        # ayrı bir adımda .text okumak, Angular'ın ilk render'dan hemen
        # sonra elementi yeniden oluşturması durumunda StaleElementReference
        # Exception'a yakalanabiliyor (canlı olarak görüldü) - find_element +
        # .text okumasının TAMAMI, self.wait'in zaten ignore ettiği
        # StaleElementReferenceException'ı her pollingde TAZE bir sorguyla
        # otomatik yeniden deneyecek şekilde TEK BİR lambda içine alındı
        # (wait_for_empty_state_message ile aynı desen).
        self.wait.until(lambda d: "11" in d.find_element(*self.EMPTY_STATE_MESSAGE).text)

    def wait_for_no_results_state(self):
        self.wait.until(EC.visibility_of_element_located(self.EMPTY_STATE))
        assert self.get_row_count() == 0, "Sonuç bulunamadı durumu beklenirken hâlâ satırlar görüntüleniyor"

    def wait_for_customer_id_search_to_show_no_results(self, customer_id, max_attempts=6, poll_interval_seconds=2):
        # DÜZELTME (canlı olarak yakalanan bir yarış durumu -
        # delete_customer_page.py'deki wait_for_deleted_customer_not_
        # found_after_reload() ile AYNI kök neden): silme işlemi HER
        # müşteri için ASENKRON tamamlanıyor - yönlendirme HEMEN oluyor
        # ama backend'deki gerçek silme birkaç saniye sürebiliyor. TEK
        # BİR arama denemesi bu gecikmeyi kaçırıp az önce silinen
        # müşteriyi HÂLÂ sonuçlarda gösterebiliyordu. Bu yüzden arama
        # BİLEREK SEYREK aralıklarla (varsayılan 2sn, en fazla 6 deneme)
        # tekrar deneniyor - delete_customer_page.py'de hızlı ardışık
        # driver.get() denemesinin oturumu düşürdüğü (ayrı bir yan etki)
        # keşfedildiğinden, burada da AYNI temkinli/seyrek kadans tercih
        # edildi.
        def _search_again():
            self.enter_customer_id(customer_id)
            self.submit_search()

        def _no_results():
            return self.get_row_count() == 0 and bool(self.driver.find_elements(*self.EMPTY_STATE))

        return poll_until(
            condition=_no_results,
            action=_search_again,
            attempts=max_attempts,
            interval=poll_interval_seconds,
        )

    def enter_customer_id(self, value):
        field = self.driver.find_element(*self.CUSTOMER_ID)
        field.clear()
        field.send_keys(value)
        self._last_customer_id = value

    def wait_for_matching_customer_id(self):
        self.wait.until(
            lambda d: [e.text.strip() for e in d.find_elements(*self.ROW_LINK)] == [self._last_customer_id]
        )

    def get_customer_id_value(self):
        return self.driver.find_element(*self.CUSTOMER_ID).get_attribute("value")

    def enter_gsm(self, value):
        field = self.driver.find_element(*self.GSM)
        field.clear()
        field.send_keys(value)

    def get_gsm_value(self):
        return self.driver.find_element(*self.GSM).get_attribute("value")

    def enter_long_first_last_name(self, length=60):
        long_text = "a" * length
        self.driver.find_element(*self.FIRST_NAME).send_keys(long_text)
        self.driver.find_element(*self.LAST_NAME).send_keys(long_text)

    def get_first_name_value(self):
        return self.driver.find_element(*self.FIRST_NAME).get_attribute("value")

    def get_last_name_value(self):
        return self.driver.find_element(*self.LAST_NAME).get_attribute("value")

    def enter_last_name(self, value):
        field = self.driver.find_element(*self.LAST_NAME)
        field.clear()
        field.send_keys(value)

    def wait_for_last_name_results(self, expected_last_name):
        expected = _turkish_fold(expected_last_name)
        self.wait.until(
            lambda d: bool(d.find_elements(*self.ROW_LAST_NAME))
            and all(_turkish_fold(e.text.strip()) == expected for e in d.find_elements(*self.ROW_LAST_NAME))
        )

    def enter_first_name(self, value):
        field = self.driver.find_element(*self.FIRST_NAME)
        field.clear()
        field.send_keys(value)

    def wait_for_first_name_results(self, expected_first_name):
        expected = _turkish_fold(expected_first_name)
        self.wait.until(
            lambda d: bool(d.find_elements(*self.ROW_FIRST_NAME))
            and all(_turkish_fold(e.text.strip()) == expected for e in d.find_elements(*self.ROW_FIRST_NAME))
        )

    def wait_for_last_name_results_starting_with(self, prefix):
        folded_prefix = _turkish_fold(prefix)
        self.wait.until(
            lambda d: bool(d.find_elements(*self.ROW_LAST_NAME))
            and all(_turkish_fold(e.text.strip()).startswith(folded_prefix) for e in d.find_elements(*self.ROW_LAST_NAME))
        )

    def wait_for_first_name_results_starting_with(self, prefix):
        folded_prefix = _turkish_fold(prefix)
        self.wait.until(
            lambda d: bool(d.find_elements(*self.ROW_FIRST_NAME))
            and all(_turkish_fold(e.text.strip()).startswith(folded_prefix) for e in d.find_elements(*self.ROW_FIRST_NAME))
        )

    def wait_for_results_matching_first_and_last_name(self, first_name_prefix, last_name_prefix):
        folded_first = _turkish_fold(first_name_prefix)
        folded_last = _turkish_fold(last_name_prefix)
        self.wait.until(
            lambda d: bool(d.find_elements(*self.ROW_LINK))
            and all(_turkish_fold(e.text.strip()).startswith(folded_first) for e in d.find_elements(*self.ROW_FIRST_NAME))
            and all(_turkish_fold(e.text.strip()).startswith(folded_last) for e in d.find_elements(*self.ROW_LAST_NAME))
        )

    def wait_for_results_matching_first_name_or_customer_id(self, first_name_prefix, customer_id):
        folded_prefix = _turkish_fold(first_name_prefix)

        def check(d):
            links = d.find_elements(*self.ROW_LINK)
            firsts = d.find_elements(*self.ROW_FIRST_NAME)
            if not links:
                return False
            matches = [
                _turkish_fold(fn.text.strip()).startswith(folded_prefix) or link.text.strip() == customer_id
                for link, fn in zip(links, firsts)
            ]
            return (
                all(matches)
                and any(link.text.strip() == customer_id for link in links)
                and any(_turkish_fold(fn.text.strip()).startswith(folded_prefix) for fn in firsts)
            )

        self.wait.until(check)

    def get_row_count(self):
        return len(self.driver.find_elements(*self.ROW))

    def get_result_customer_ids(self):
        return [e.text.strip() for e in self.driver.find_elements(*self.ROW_LINK)]

    def is_customer_id_column_sorted_ascending(self):
        # Satırların yüklenmesini bekle - beklemeden hemen okunursa DOM
        # henüz boşken kontrol edilebilir, bu da BOŞ liste için
        # "ids == sorted(ids)" her zaman True döndüğünden testi
        # SESSİZCE ve YANLIŞLIKLA PASS ettirir (hiçbir şeyi
        # doğrulamadan). Boş liste EXPLICIT olarak reddediliyor.
        self.wait.until(lambda d: bool(d.find_elements(*self.ROW_LINK)))
        ids = [int(value) for value in self.get_result_customer_ids()]
        assert ids, "Sıralama kontrol edilirken sonuç listesi boştu - hiçbir kayıt doğrulanamadı"
        return ids == sorted(ids)

    def is_pagination_active(self):
        pagination = self.driver.find_elements(*self.PAGINATION)
        next_buttons = self.driver.find_elements(*self.NEXT_PAGE)
        return bool(pagination) and bool(next_buttons) and next_buttons[0].is_enabled()

    def capture_current_page_customer_ids(self):
        self._first_page_ids = set(self.get_result_customer_ids())

    def go_to_next_page(self):
        self.wait.until(EC.element_to_be_clickable(self.NEXT_PAGE)).click()

    def verify_next_page_records_are_new(self):
        # Not: sayfa gecisi sirasinda Angular DOM'u ANLIK olarak
        # bosaltabiliyor (*ngFor yeniden render edilirken) - "kume eskisinden
        # FARKLI mi" kontrolu tek basina BOS kumeyi de "farkli" say(iyord)u,
        # bu da wait.until'in yeni sayfa GERCEKTEN yuklenmeden ERKEN
        # tatmin olmasina ve testin BOS bir sayfayla YANLIS-POZITIF/gecici
        # FAIL vermesine yol aciyordu (canli olarak yakalandi). Artik hem
        # BOS OLMAMASI hem eskisinden FARKLI OLMASI birlikte bekleniyor.
        self.wait.until(
            lambda d: (ids := {e.text.strip() for e in d.find_elements(*self.ROW_LINK)})
            and ids != self._first_page_ids
        )
        next_page_ids = set(self.get_result_customer_ids())
        assert next_page_ids, "Sonraki sayfada hiç kayıt yok"
        assert not (next_page_ids & self._first_page_ids), (
            "Sonraki sayfada önceki sayfayla çakışan (tekrarlanan) kayıtlar var"
        )

    def is_create_customer_button_visible(self):
        button = self.wait.until(EC.visibility_of_element_located(self.CREATE_CUSTOMER_BUTTON))
        return button.is_displayed() and button.is_enabled()

    def click_create_customer_button(self):
        self.wait.until(EC.element_to_be_clickable(self.CREATE_CUSTOMER_BUTTON)).click()

    def click_customer_row_link(self):
        # Not: sticky topbar (position: sticky, top: 0) satırın üzerine
        # binip normal .click()'i ElementClickIntercepted ile engelliyor -
        # elementi viewport ortasına kaydırıp (topbar'ın arkasından çıkararak)
        # sonra normal .click() ile tıklıyoruz.
        self._window_handle_count_before_click = len(self.driver.window_handles)
        link = self.wait.until(EC.element_to_be_clickable(self.ROW_LINK))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link)
        link.click()

    def verify_navigated_to_customer_detail_same_tab(self, customer_id):
        self.wait.until(lambda d: f"/customers/{customer_id}" in d.current_url)
        assert len(self.driver.window_handles) == self._window_handle_count_before_click, (
            "Müşteri detayına geçişte yeni bir sekme/pencere açıldı"
        )
        assert f"/customers/{customer_id}" in self.driver.current_url
        self.wait.until(EC.visibility_of_element_located(self.CUSTOMER_DETAIL_HEADER))

    def fill_all_search_fields_via_tab_navigation(self):
        identity_number = "".join(random.choices("0123456789", k=11))
        self.driver.find_element(*self.IDENTITY_NUMBER).click()
        actions = ActionChains(self.driver)
        actions.send_keys(identity_number).send_keys(Keys.TAB)  # identityNumber
        actions.send_keys("5").send_keys(Keys.TAB)  # customerId
        actions.send_keys("1234567890").send_keys(Keys.TAB)  # accountNumber
        actions.send_keys(Keys.TAB)  # gsm-country butonu - metin girilmiyor
        actions.send_keys("5551234567").send_keys(Keys.TAB)  # gsm
        actions.send_keys("Ahmet").send_keys(Keys.TAB)  # firstName
        actions.send_keys("Yilmaz").send_keys(Keys.TAB)  # lastName
        actions.send_keys("12345678")  # orderNumber
        actions.perform()

    def click_clear_button(self):
        self.wait.until(EC.element_to_be_clickable(self.SEARCH_CLEAR)).click()

    def verify_all_search_fields_empty(self):
        for locator in self.SEARCH_FIELDS:
            value = self.driver.find_element(*locator).get_attribute("value")
            assert value == "", f"Alan temizlenmedi: {locator} = {value!r}"

    def verify_results_reset_to_default(self):
        self.wait.until(lambda d: len(d.find_elements(*self.ROW)) == 15)

    def get_results_count_number(self):
        # "822 kayıt" / olası "822 records" gibi dile göre değişen bir
        # metinden SADECE sayıyı çıkarıyor - literal kelime karşılaştırması
        # yok, dilden bağımsız.
        el = self.wait.until(EC.visibility_of_element_located(self.RESULTS_COUNT))
        match = re.search(r"\d+", el.text)
        assert match, f"RESULTS_COUNT metninde sayı bulunamadı: {el.text!r}"
        return int(match.group())

    def get_results_range_bounds(self):
        # "822 kayıttan 1–15 arası" / olası EN karşılığı "1-15 of 822
        # records" gibi FARKLI kelime/sayı sırasına sahip olabilecek bir
        # metinden, sayıların METİNDEKİ POZİSYONUNA güvenmeden (dilden
        # bağımsız) alt/üst sınırı çıkarıyor: toplam sayı zaten
        # get_results_count_number()'dan biliniyor, metindeki sayılardan ona
        # eşit OLMAYAN ikisinin küçüğü=alt, büyüğü=üst sınırdır.
        total = self.get_results_count_number()
        range_el = self.wait.until(EC.visibility_of_element_located(self.RESULTS_RANGE))
        numbers = [int(n) for n in re.findall(r"\d+", range_el.text)]
        bounds = [n for n in numbers if n != total]
        assert len(bounds) >= 2, (
            f"RESULTS_RANGE metninde beklenen alt/üst sınır sayıları bulunamadı: {range_el.text!r}"
        )
        return min(bounds), max(bounds)

    def is_results_range_consistent_with_row_count(self):
        lower, upper = self.get_results_range_bounds()
        return (upper - lower + 1) == self.get_row_count()

    def capture_sort_column_values(self, column_label):
        locator = self.SORT_ROW_VALUE_LOCATORS[column_label]
        self.wait.until(lambda d: bool(d.find_elements(*locator)))
        return [e.text.strip() for e in self.driver.find_elements(*locator)]

    def click_sort_column(self, column_label):
        locator = self.SORT_LOCATORS[column_label]
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def wait_for_sort_column_values_to_change(self, column_label, previous_values):
        self.wait.until(lambda d: self.capture_sort_column_values(column_label) != previous_values)
