from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.billing_account_delete_page import BillingAccountDeletePage
from utils.waits import poll_until


class BillingAccountProductsPage(BillingAccountDeletePage):
    # Hesap satırı/listesi bileşeni "Fatura Hesabı Sil" ile AYNI sayfa/
    # component - gerçek bir "is-a" ilişkisi olduğundan BillingAccount
    # DeletePage'den türetildi (projedeki diğer hesap alt-sayfaları
    # zincirindeki AYNI mantık). Canlı DOM incelemesiyle doğrulandı:
    # "Hesap Ürünleri" paneli account-row-toggle ile AÇILAN bir şey
    # DEĞİL, hesap oluşturulduğunda VARSAYILAN OLARAK ZATEN AÇIK
    # (aria-expanded="true") - toggle'a tıklamak paneli KAPATIYOR.

    PRODUCT_ROW = (By.CSS_SELECTOR, "[data-testid='product-row']")
    PRODUCT_ROW_ID = (By.CSS_SELECTOR, "[data-testid='product-row-id']")
    PRODUCT_ROW_NAME = (By.CSS_SELECTOR, "[data-testid='product-row-name']")
    PRODUCT_ROW_CAMPAIGN_NAME = (By.CSS_SELECTOR, "[data-testid='product-row-campaign-name']")
    PRODUCT_ROW_CAMPAIGN_ID = (By.CSS_SELECTOR, "[data-testid='product-row-campaign-id']")
    PRODUCT_ROW_DELETE = (By.CSS_SELECTOR, "[data-testid='product-row-delete']")
    PRODUCT_ROW_PREVIEW = (By.CSS_SELECTOR, "[data-testid='product-row-preview']")

    PRODUCT_PREVIEW = (By.CSS_SELECTOR, "[data-testid='product-preview']")
    PRODUCT_PREVIEW_NAME = (By.CSS_SELECTOR, "[data-testid='product-preview-name']")
    PRODUCT_PREVIEW_OFFER_ID = (By.CSS_SELECTOR, "[data-testid='product-preview-offer-id']")
    PRODUCT_PREVIEW_OFFER_NAME = (By.CSS_SELECTOR, "[data-testid='product-preview-offer-name']")
    PRODUCT_PREVIEW_SPEC_ID = (By.CSS_SELECTOR, "[data-testid='product-preview-spec-id']")
    PRODUCT_PREVIEW_CHARACTERISTICS = (By.CSS_SELECTOR, "[data-testid='product-preview-characteristics']")
    PRODUCT_PREVIEW_CLOSE = (By.CSS_SELECTOR, "[data-testid='product-preview-close']")

    def get_products_panel_id(self):
        # Her senaryo fresh, tek kullanımlık bir müşteri/hesapla
        # çalıştığından (bu projedeki diğer *_delete.feature'larla
        # tutarlı) her zaman TEK bir account-row/toggle var - global
        # bir sorgu bu yüzden güvenli.
        toggle = self.wait.until(EC.visibility_of_element_located(self.ACCOUNT_ROW_TOGGLE))
        return toggle.get_attribute("aria-controls")

    def _get_panel(self, panel_id):
        return self.wait.until(EC.presence_of_element_located((By.ID, panel_id)))

    def get_product_rows(self, panel_id):
        panel = self._get_panel(panel_id)
        return panel.find_elements(*self.PRODUCT_ROW)

    def get_product_row_count(self, panel_id):
        return len(self.get_product_rows(panel_id))

    def is_products_table_displayed(self, panel_id):
        return self.get_product_row_count(panel_id) > 0

    def get_product_row_names(self, panel_id):
        return [row.find_element(*self.PRODUCT_ROW_NAME).text.strip() for row in self.get_product_rows(panel_id)]

    def wait_for_products_persisted_after_reload(self, customer_url, minimum_count=1):
        # DÜZELTME (bugsbunny.txt madde 20 - flaky olarak yakalandı, izole
        # koşumda 3 denemede 1 FAILED): sipariş gönderimi ile ürünün fatura
        # hesabında GÖRÜNMESİ arasında asenkron bir gecikme var. Eski
        # implementasyon müşteri detayına dönüp ürün satırlarını HEMEN
        # sayıyordu; backend henüz yazmamışsa 0 görüyordu.
        #
        # Bu, TC-005-03 / TC-012-03 / TC-006-06b ile AYNI aile: "backend
        # mutasyonu kabul ediliyor ama saniyeler sonra tamamlanıyor".
        # Çözüm de aynı ve kanıtlanmış: reload'ı tekrarlayan seyrek bir
        # yoklama döngüsü. Tek bir DOM beklemesi yetmez - veri ancak yeni
        # bir sayfa yüklemesiyle geliyor.
        def _reload_account_tab():
            self.driver.get(customer_url)
            self.wait.until(EC.element_to_be_clickable(self.TAB_ACCOUNT)).click()

        def _products_visible():
            # Global sorgu: her senaryo fresh, tek kullanımlık bir
            # müşteri/hesapla çalıştığından TEK bir hesap var
            # (get_products_panel_id'deki AYNI gerekçe). Panel, hesap
            # oluşturulduğunda varsayılan olarak zaten açık.
            return len(self.driver.find_elements(*self.PRODUCT_ROW)) >= minimum_count

        return poll_until(condition=_products_visible, action=_reload_account_tab)

    def wait_for_product_row_count_at_least(self, panel_id, minimum_count):
        try:
            self.wait.until(lambda d: self.get_product_row_count(panel_id) >= minimum_count)
            return True
        except TimeoutException:
            return False

    def has_no_campaign_fields_displayed(self, panel_id, row_index=0):
        # Kampanyasız bir üründe kampanya alanlarının dile bağlı bir
        # literal ("—", "-", "N/A"...) yerine YAPISAL olarak "dolu ama
        # ürün/kampanya adından FARKLI kısa bir yer tutucu" olduğu
        # kontrol ediliyor - canlı doğrulandı: em-dash ("—") gösteriliyor.
        row = self.get_product_rows(panel_id)[row_index]
        campaign_name = row.find_element(*self.PRODUCT_ROW_CAMPAIGN_NAME).text.strip()
        campaign_id = row.find_element(*self.PRODUCT_ROW_CAMPAIGN_ID).text.strip()
        product_name = row.find_element(*self.PRODUCT_ROW_NAME).text.strip()
        return bool(campaign_name) and bool(campaign_id) and campaign_name != product_name and len(campaign_name) <= 3

    def each_row_has_preview_icon(self, panel_id):
        rows = self.get_product_rows(panel_id)
        return bool(rows) and all(row.find_elements(*self.PRODUCT_ROW_PREVIEW) for row in rows)

    def each_row_has_delete_icon(self, panel_id):
        rows = self.get_product_rows(panel_id)
        return bool(rows) and all(row.find_elements(*self.PRODUCT_ROW_DELETE) for row in rows)

    def click_preview_on_row(self, panel_id, row_index=0):
        row = self.get_product_rows(panel_id)[row_index]
        row.find_element(*self.PRODUCT_ROW_PREVIEW).click()
        self.wait.until(EC.visibility_of_element_located(self.PRODUCT_PREVIEW))

    def is_preview_displayed_readonly_with_offer_fields(self):
        # "Salt okunur" yapısal olarak doğrulanıyor: alanlar <dd>/<p>
        # metin elemanları (input/textarea DEĞİL) ve hepsi dolu.
        preview = self.driver.find_element(*self.PRODUCT_PREVIEW)
        if preview.find_elements(By.CSS_SELECTOR, "input, textarea, select"):
            return False
        offer_id = self.driver.find_element(*self.PRODUCT_PREVIEW_OFFER_ID).text.strip()
        offer_name = self.driver.find_element(*self.PRODUCT_PREVIEW_OFFER_NAME).text.strip()
        spec_id = self.driver.find_element(*self.PRODUCT_PREVIEW_SPEC_ID).text.strip()
        characteristics = self.driver.find_element(*self.PRODUCT_PREVIEW_CHARACTERISTICS).text.strip()
        return bool(offer_id) and bool(offer_name) and bool(spec_id) and bool(characteristics)

    def close_preview(self):
        self.wait.until(EC.element_to_be_clickable(self.PRODUCT_PREVIEW_CLOSE)).click()
        self.wait.until(EC.invisibility_of_element_located(self.PRODUCT_PREVIEW))

    def is_preview_closed_and_list_visible(self, panel_id):
        return bool(self.driver.find_elements(*self.PRODUCT_PREVIEW)) is False and self.is_products_table_displayed(panel_id)

    def attempt_delete_on_row(self, panel_id, row_index=0):
        row = self.get_product_rows(panel_id)[row_index]
        deleted_product_name = row.find_element(*self.PRODUCT_ROW_NAME).text.strip()
        row.find_element(*self.PRODUCT_ROW_DELETE).click()
        return deleted_product_name

    def is_delete_action_ineffective(self, panel_id, before_count, before_names):
        # Delete ikonu tıklamasının HERHANGİ bir gözlemlenebilir etkisi
        # olmadığı doğrulanıyor: onay penceresi YOK, satır sayısı/isim
        # listesi DEĞİŞMEDİ - canlı doğrulandı (013-04, "işlevsiz" davranış).
        no_confirm_dialog = not self.is_confirm_dialog_present()
        same_count = self.get_product_row_count(panel_id) == before_count
        same_names = self.get_product_row_names(panel_id) == before_names
        return no_confirm_dialog and same_count and same_names

    def is_data_unchanged_after_reload(self, panel_id, expected_names):
        detail_url = self.driver.current_url

        def unchanged(driver):
            driver.get(detail_url)
            self.wait.until(EC.element_to_be_clickable(self.TAB_ACCOUNT)).click()
            new_panel_id = self.get_products_panel_id()
            return self.get_product_row_names(new_panel_id) == expected_names

        try:
            return self.wait.until(unchanged)
        except TimeoutException:
            return False

    def click_toggle_and_wait_collapsed(self, panel_id):
        self.wait.until(EC.element_to_be_clickable(self.ACCOUNT_ROW_TOGGLE)).click()
        self.wait.until(lambda d: not d.find_elements(By.ID, panel_id))

    def click_toggle_and_wait_expanded(self, panel_id):
        self.wait.until(EC.element_to_be_clickable(self.ACCOUNT_ROW_TOGGLE)).click()
        self.wait.until(EC.presence_of_element_located((By.ID, panel_id)))

    def is_panel_collapsed(self, panel_id):
        return not self.driver.find_elements(By.ID, panel_id)
