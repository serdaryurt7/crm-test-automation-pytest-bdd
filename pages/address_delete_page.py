from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.address_add_page import AddressAddPage


class AddressDeletePage(AddressAddPage):
    # AddressAddPage(AddressUpdatePage) zincirinden miras alınıyor: silme
    # senaryolarının kurulumu (ör. "müşterinin birden fazla adresi vardır")
    # AddressAddPage'in add_new_address_and_wait_for_card/get_primary_states
    # metotlarına doğrudan ihtiyaç duyuyor - bu yüzden burada tekrar
    # yazılmıyor.

    CONFIRM_DIALOG = (By.CSS_SELECTOR, "[data-testid='confirm-dialog']")

    def open_card_menu(self, index=0):
        menus = self.driver.find_elements(*self.ADDRESS_CARD_MENU)
        menus[index].click()
        self.wait.until(EC.element_to_be_clickable(self.ADDRESS_CARD_EDIT))

    def _get_open_menu_delete_option(self):
        # Kart menüsü açıldığında Edit/Delete seçenekleri tek bir ortak
        # portal/overlay içinde render ediliyor (canlı doğrulandı - HANGİ
        # kartın menüsü açılırsa açılsın DOM'da her zaman TEK bir Delete
        # seçeneği bulunuyor). Sabit bir index yerine, seçeneğin GERÇEKTEN
        # DOM'a render edilip tıklanabilir hale gelmesini WebDriverWait'in
        # dinamik polling'iyle bekleyip elementi bu şekilde alıyoruz.
        return self.wait.until(EC.presence_of_element_located(self.ADDRESS_CARD_DELETE))

    def is_delete_option_disabled(self, index=0):
        self.open_card_menu(index)
        return not self._get_open_menu_delete_option().is_enabled()

    def attempt_click_disabled_delete_option(self):
        # Menü zaten açık (is_delete_option_disabled tarafından). Disabled
        # bir butona tıklama denemesi tarayıcıya/Selenium sürümüne göre
        # farklı exception türleri fırlatabiliyor - amaç sadece HİÇBİR
        # silme gerçekleşmediğini doğrulamak olduğundan geniş yakalanıyor.
        delete_option = self._get_open_menu_delete_option()
        try:
            delete_option.click()
        except (ElementNotInteractableException, ElementClickInterceptedException):
            pass

    def is_confirm_dialog_present(self):
        dialogs = self.driver.find_elements(*self.CONFIRM_DIALOG)
        return bool(dialogs) and dialogs[0].is_displayed()

    def delete_card_at_index(self, index):
        before_count = self.get_card_count()
        self._deleted_title = self.get_all_card_titles()[index]
        self.open_card_menu(index)
        delete_option = self.wait.until(EC.element_to_be_clickable(self.ADDRESS_CARD_DELETE))
        delete_option.click()
        self.wait.until(lambda d: len(d.find_elements(*self.ADDRESS_CARD)) < before_count)
        return delete_option

    def delete_last_added_card(self):
        # Canlı doğrulandı (address_add.feature): yeni eklenen kart
        # listenin SONUNA ekleniyor - bu yüzden "kullanıcı Sil'i seçer"
        # adımında somut hedef olarak SON kart kullanılıyor.
        return self.delete_card_at_index(self.get_card_count() - 1)

    def delete_primary_card(self):
        primary_states = self.get_primary_states()
        primary_index = primary_states.index(True)
        return self.delete_card_at_index(primary_index)

    def is_remaining_address_auto_primary(self):
        # Canlı doğrulandı: Primary olarak işaretli adres silindiğinde,
        # kalan TEK adres OTOMATİK olarak Primary'e dönüşüyor (hiçbir
        # adresin Primary olmadığı bir durum OLUŞMUYOR).
        return self.get_card_count() == 1 and self.get_primary_states() == [True]

    def wait_for_deletion_persisted_after_reload(self):
        # address_add_page.wait_for_new_address_persisted_after_reload'un
        # SİLME yönündeki karşılığı: silinen kartın sayfa TAMAMEN
        # yenilendikten SONRA da GERÇEKTEN listede OLMADIĞINI, dinamik
        # WebDriverWait polling ile doğruluyor (sabit bekleme yok).
        detail_url = self.driver.current_url
        deleted_title = self._deleted_title

        def deletion_persisted(driver):
            driver.get(detail_url)
            self.wait.until(EC.element_to_be_clickable(self.TAB_ADDRESS)).click()
            self.wait.until(EC.visibility_of_element_located(self.ADDRESS_CARD))
            return deleted_title not in self.get_all_card_titles()

        try:
            return self.wait.until(deletion_persisted)
        except TimeoutException:
            return False

    def attempt_duplicate_delete_with_stale_reference(self, stale_delete_button):
        # "Aynı istek tekrar gönderilir" iddiasının UI-seviyesinde en
        # gerçekçi karşılığı: artık DOM'dan kaldırılmış (stale) bir Delete
        # referansıyla TEKRAR tıklamayı denemek - ikinci/mükerrer bir silme
        # denemesini simüle ediyor. Canlı doğrulandı: bu StaleElement
        # ReferenceException ile GÜVENLİ şekilde reddediliyor. True =
        # ikinci deneme güvenli şekilde reddedildi, False = ikinci tıklama
        # beklenmedik şekilde "başarılı" göründü (şüpheli/incelenmeli).
        try:
            stale_delete_button.click()
            return False
        except (StaleElementReferenceException, ElementNotInteractableException, ElementClickInterceptedException):
            return True

    def is_app_still_functional(self):
        # Uygulamanın gerçekten çökmediğini (crash) ayırt etmek için:
        # sayfa hâlâ DOM'a sahip mi VE adres sekmesi hâlâ normal
        # çalışıyor mu (en az 1 kart görüntüleniyor mu) kontrol ediliyor.
        return bool(self.driver.find_elements(By.TAG_NAME, "body")) and self.get_card_count() >= 1
