from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class DeleteCustomerPage:
    DETAIL_HEADER = (By.CSS_SELECTOR, "[data-testid='customer-detail-header']")
    STATUS_BADGE = (By.CSS_SELECTOR, "[data-testid='status-badge']")
    DELETE_BUTTON = (By.CSS_SELECTOR, "[data-testid='customer-info-delete']")

    CONFIRM_DIALOG = (By.CSS_SELECTOR, "[data-testid='confirm-dialog']")
    CONFIRM_DIALOG_MESSAGE = (By.CSS_SELECTOR, "[data-testid='confirm-dialog-message']")
    CONFIRM_DIALOG_CANCEL = (By.CSS_SELECTOR, "[data-testid='confirm-dialog-cancel']")
    CONFIRM_DIALOG_CONFIRM = (By.CSS_SELECTOR, "[data-testid='confirm-dialog-confirm']")

    NAV_CUSTOMER_SEARCH = (By.CSS_SELECTOR, "[data-testid='nav-customer-search']")
    EMPTY_STATE_MESSAGE = (By.CSS_SELECTOR, "[data-testid='empty-state-message']")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.wait.until(EC.visibility_of_element_located(self.DETAIL_HEADER))
        self._detail_url = driver.current_url
        self._last_background_click_succeeded = None

    def get_status(self):
        return self.driver.find_element(*self.STATUS_BADGE).text.strip()

    def click_delete(self):
        self.wait.until(EC.element_to_be_clickable(self.DELETE_BUTTON)).click()
        self.wait.until(EC.visibility_of_element_located(self.CONFIRM_DIALOG))

    def is_confirm_dialog_displayed_with_buttons(self):
        # Mesaj metni dile göre değişebileceğinden (TR/EN) literal metin
        # karşılaştırılmıyor - yapısal olarak mesaj elementinin görünür VE
        # boş olmadığı (gerçekten bir mesaj içerdiği) doğrulanıyor.
        message_el = self.driver.find_element(*self.CONFIRM_DIALOG_MESSAGE)
        return (
            self.driver.find_element(*self.CONFIRM_DIALOG).is_displayed()
            and message_el.is_displayed()
            and bool(message_el.text.strip())
            and self.driver.find_element(*self.CONFIRM_DIALOG_CANCEL).is_displayed()
            and self.driver.find_element(*self.CONFIRM_DIALOG_CONFIRM).is_displayed()
        )

    def click_confirm_no(self):
        self.driver.find_element(*self.CONFIRM_DIALOG_CANCEL).click()
        self.wait.until(EC.invisibility_of_element_located(self.CONFIRM_DIALOG))

    def click_confirm_yes(self):
        self.driver.find_element(*self.CONFIRM_DIALOG_CONFIRM).click()

    def is_dialog_open(self):
        dialogs = self.driver.find_elements(*self.CONFIRM_DIALOG)
        return bool(dialogs) and dialogs[0].is_displayed()

    def attempt_background_interaction(self):
        # Dialog acikken arka plandaki bir navigasyon elementine tiklamayi
        # DENIYORUZ - gercek modal davranisinda tarayici bunu
        # ElementClickInterceptedException ile engelliyor (canli
        # dogrulandi), native "is_enabled()" kontrolu bunu YAKALAMAZ.
        try:
            self.driver.find_element(*self.NAV_CUSTOMER_SEARCH).click()
            self._last_background_click_succeeded = True
        except ElementClickInterceptedException:
            self._last_background_click_succeeded = False

    def did_background_click_succeed(self):
        return self._last_background_click_succeeded

    def get_customer_id(self):
        return self._detail_url.rstrip("/").split("/")[-1]

    def wait_for_redirect_to_search(self):
        self.wait.until(lambda d: d.current_url.rstrip("/").endswith("/customers"))

    def reload_detail_url(self):
        # Silinen musterinin eski detay URL'sine dogrudan tekrar gitmek
        # icin - fresh bir navigasyon (driver.get), sayfanin GERCEKTEN
        # sunucudan yeniden yuklendigini garantiler.
        self.driver.get(self._detail_url)

    def is_empty_state_message_displayed(self):
        # Aynı dil-bağımsızlık gerekçesi: mesaj metni değil, mesaj
        # elementinin görünür ve dolu olması (gerçekten bir "bulunamadı"
        # durumu içermesi) kontrol ediliyor.
        message_el = self.wait.until(EC.visibility_of_element_located(self.EMPTY_STATE_MESSAGE))
        return bool(message_el.text.strip())

    def wait_for_delete_rejected(self):
        # KASITLI KIRMIZI (canlı doğrulandı, bkz. bugsbunny.txt madde 17 -
        # customer 854 ile uçtan uca test edildi): sistem şu an "aktif
        # ürünü olan müşteri silinemez" kuralını UYGULAMIYOR - silme
        # engellenmeden gerçekleşiyor, kullanıcı Müşteri Arama ekranına
        # yönlendiriliyor. Bilinen defekt düzelene kadar bu metodun
        # AssertionError ile FAILED vermesi beklenen/istenen sonuçtur.
        #
        # ÖNEMLİ (canlı olarak yakalanan bir tasarım hatası düzeltildi):
        # "current_url hâlâ detay sayfasında mı" şeklinde DOĞRUDAN bir
        # wait.until kontrolü ERKEN/YARIŞ DURUMUNA açıktı - silme isteği
        # asenkron işlenirken, yönlendirme henüz BAŞLAMADAN önceki İLK
        # polling anında "URL değişmedi" durumu YANLIŞLIKLA true dönüp
        # sahte-PASS üretebiliyordu (negatif bir durumu erken kanıtlamaya
        # çalışmanın TC-004-11'de bilinçli olarak kaçınılan AYNI tuzağı).
        # Düzeltme: zaten var olan, kanıtlanmış wait_for_redirect_to_search()
        # metodu (TAM 10 saniyelik standart timeout ile) yönlendirmenin
        # GERÇEKTEN olup olmadığını sonuna kadar bekleyip doğruluyor -
        # yönlendirme olursa (mevcut/bilinen bug) TimeoutException YERİNE
        # bilinçli bir AssertionError'a çevriliyor; yönlendirme GERÇEKTEN
        # hiç olmazsa (düzeltilmiş/beklenen davranış) TimeoutException
        # yutuluyor ve metod sessizce başarıyla dönüyor.
        try:
            self.wait_for_redirect_to_search()
        except TimeoutException:
            return
        raise AssertionError(
            "Beklenen: aktif ürünü olan müşterinin silinmesi reddedilmeli. "
            "Gerçek: sistem müşteriyi sildi ve Müşteri Arama ekranına yönlendirdi "
            "(bilinen defekt, bkz. bugsbunny.txt madde 17)."
        )

    def capture_status_snapshot(self):
        # Dilden bağımsız "değişmedi mi" karşılaştırması için - "Aktif"
        # (TR) / "Active" (EN) gibi literal bir değerle KARŞILAŞTIRMIYORUZ
        # (bu, arayüz dili İngilizce'yken kırılırdı). Bunun yerine, silme
        # denemesinden HEMEN ÖNCEKİ (o an aktif olan dilde okunan) durum
        # metninin birebir AYNISI, denemeden SONRA da hâlâ görüntülenip
        # görüntülenmediği doğrulanıyor - hangi dilde çalıştırılırsa
        # çalıştırılsın aynı mantık geçerli.
        self._status_before_delete_attempt = self.get_status()

    def is_still_on_customer_info_with_status_unchanged(self):
        return (
            bool(self.driver.find_elements(*self.DETAIL_HEADER))
            and self.driver.find_element(*self.DETAIL_HEADER).is_displayed()
            and self.get_status() == self._status_before_delete_attempt
        )
