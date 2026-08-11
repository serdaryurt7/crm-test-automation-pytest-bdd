from selenium.common.exceptions import ElementClickInterceptedException
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
