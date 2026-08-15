from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage


class LanguageSwitcherPage(BasePage):
    # Sayfa başlığı/nav gibi HER ekranda ortak görünen bir topbar bileşeni
    # (app-language-switcher) - belirli bir sayfaya/akışa ait DEĞİL, bu
    # yüzden projedeki diğer standalone sayfalarla (OfferSelectionPage vb.)
    # AYNI "has-a, is-a değil" tasarım kararı: başka HİÇBİR SAYFADAN
    # inherit ETMİYOR, herhangi bir authenticated ekranda kullanılabilir.
    #
    # BasePage bu karara aykırı değil: o bir sayfa değil, tüm page
    # object'lerin paylaştığı ALTYAPI (driver + wait kurulumu). Sayfalar
    # arası "is-a" ilişkisi kurmuyor.

    TOGGLE = (By.CSS_SELECTOR, "[data-testid='language-switcher-toggle']")
    PANEL = (By.CSS_SELECTOR, "[data-testid='language-switcher-panel']")
    OPTION_ITEMS = (By.CSS_SELECTOR, "[data-testid='language-switcher-panel'] li[role='option']")
    OPTION_TR = (By.CSS_SELECTOR, "[data-testid='language-option-tr']")
    OPTION_EN = (By.CSS_SELECTOR, "[data-testid='language-option-en']")

    def get_current_language_code(self):
        return self.driver.find_element(*self.TOGGLE).text.strip()

    def is_panel_open(self):
        return self.driver.find_element(*self.TOGGLE).get_attribute("aria-expanded") == "true"

    def open_panel(self):
        self.wait.until(EC.element_to_be_clickable(self.TOGGLE)).click()
        self.wait.until(EC.visibility_of_element_located(self.PANEL))

    def close_panel(self):
        self.wait.until(EC.element_to_be_clickable(self.TOGGLE)).click()
        self.wait.until(EC.invisibility_of_element_located(self.PANEL))

    def get_option_codes(self):
        # "language-option-tr" -> "tr" - dilden bağımsız, testid'in kendi
        # yapısından çıkarılıyor (görünen metne bakılmıyor).
        codes = []
        for item in self.driver.find_elements(*self.OPTION_ITEMS):
            button = item.find_element(By.CSS_SELECTOR, "button")
            testid = button.get_attribute("data-testid")
            codes.append(testid.replace("language-option-", ""))
        return codes

    def select_language(self, code):
        before = self.get_current_language_code()
        locator = self.OPTION_TR if code == "tr" else self.OPTION_EN
        self.wait.until(EC.element_to_be_clickable(locator)).click()
        self.wait.until(lambda d: self.get_current_language_code() != before)

    def get_active_option_code(self):
        for item in self.driver.find_elements(*self.OPTION_ITEMS):
            if item.get_attribute("aria-selected") == "true":
                button = item.find_element(By.CSS_SELECTOR, "button")
                return button.get_attribute("data-testid").replace("language-option-", "")
        return None

    def is_language_highlighted_as_active(self, code):
        active_flags = [item.get_attribute("aria-selected") == "true" for item in self.driver.find_elements(*self.OPTION_ITEMS)]
        return self.get_active_option_code() == code and active_flags.count(True) == 1
