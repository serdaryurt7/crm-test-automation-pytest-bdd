import random

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage


class ProductConfigurationPage(BasePage):
    # "İleri" ile Teklif Seçimi'nden ulaşılan "Ürün Konfigürasyonu" ekranı -
    # OfferSelectionPage/SalesSetupPage ile AYNI "has-a, is-a değil"
    # tasarım kararı: kavramsal olarak ayrı bir ekran, inheritance ilişkiyi
    # bozar. Yeni adres formu alt-bileşeni billing_account_create_page.py
    # ile AYNI CSS testid'lerini kullanıyor (canlı doğrulandı - aynı
    # paylaşılan "Yeni Adres Ekle" bileşeni) - kasıtlı küçük bir tekrar,
    # bu sayfa kavramsal olarak bir "adres sayfası" DEĞİL.

    CONFIG_CARD = (By.CSS_SELECTOR, "[data-testid='sales-config-target']")
    CONFIG_OFFER_ID = (By.CSS_SELECTOR, "[data-testid='sales-config-offer-id']")
    CONFIG_OFFER_NAME = (By.CSS_SELECTOR, "[data-testid='sales-config-offer-name']")
    CONFIG_FIELD = (By.CSS_SELECTOR, "[data-testid='sales-config-field']")

    ADDRESS_CARD = (By.CSS_SELECTOR, "[data-testid='address-card']")
    ADDRESS_CARD_TITLE = (By.CSS_SELECTOR, "[data-testid='address-card-title']")
    ADDRESS_CARD_PRIMARY = (By.CSS_SELECTOR, "[data-testid='address-card-primary']")
    ADD_ADDRESS_BUTTON = (By.CSS_SELECTOR, "[data-testid='sales-config-add-address']")

    NEW_ADDRESS_CITY_BUTTON = (By.ID, "address-city")
    NEW_ADDRESS_CITY_LIST = (By.ID, "address-city-list")
    NEW_ADDRESS_STREET_INPUT = (By.CSS_SELECTOR, "[data-testid='address-street']")
    NEW_ADDRESS_BUILDING_INPUT = (By.CSS_SELECTOR, "[data-testid='address-building-no']")
    NEW_ADDRESS_DESCRIPTION_INPUT = (By.CSS_SELECTOR, "[data-testid='address-description']")
    NEW_ADDRESS_SAVE_BUTTON = (By.CSS_SELECTOR, "[data-testid='address-save']")

    BACK_BUTTON = (By.CSS_SELECTOR, "[data-testid='sales-config-back']")
    NEXT_BUTTON = (By.CSS_SELECTOR, "[data-testid='sales-config-next']")

    def __init__(self, driver):
        super().__init__(driver)
        self.wait.until(EC.visibility_of_element_located(self.CONFIG_FIELD))

    # --- Konfigürasyon kartları ---
    def get_config_cards(self):
        return self.driver.find_elements(*self.CONFIG_CARD)

    def get_config_card_count(self):
        return len(self.get_config_cards())

    def get_config_card_offer_names(self):
        return [card.find_element(*self.CONFIG_OFFER_NAME).text.strip() for card in self.get_config_cards()]

    def fill_all_required_text_fields_with_dummy_values(self):
        # Canlı doğrulandı: hiçbir config alanında GERÇEK bir format/regex
        # validasyonu yok (bkz. TC-015-06 bulgusu) - bu yüzden herhangi bir
        # dolu değer yeterli. Yalnızca <input> etiketli alanlar dolduruluyor
        # (bazı şablonlarda - ör. "Ev İnterneti Fiber 1000" - bir <app-select>
        # bant genişliği alanı da olabiliyor, o zaten varsayılan bir değerle
        # geliyor - bu metod SADECE bu projede kullanılan basit, tek-tip
        # (yalnızca <input>) şablonlu teklifler için tasarlandı - YAGNI).
        fields = self.driver.find_elements(*self.CONFIG_FIELD)
        for index, field in enumerate(fields):
            if field.tag_name == "input":
                field.send_keys(f"{5000000000 + index}")

    def is_next_button_enabled(self):
        return self.driver.find_element(*self.NEXT_BUTTON).is_enabled()

    # --- Hizmet adresi ---
    def get_address_titles(self):
        return [card.find_element(*self.ADDRESS_CARD_TITLE).text for card in self.driver.find_elements(*self.ADDRESS_CARD)]

    def get_address_selection_states(self):
        return [
            card.find_element(*self.ADDRESS_CARD_PRIMARY).is_selected()
            for card in self.driver.find_elements(*self.ADDRESS_CARD)
        ]

    def is_default_address_preselected(self):
        states = self.get_address_selection_states()
        return bool(states) and states[0] is True and states.count(True) == 1

    def select_address_by_index(self, index):
        radios = self.driver.find_elements(*self.ADDRESS_CARD_PRIMARY)
        self.driver.execute_script("arguments[0].click();", radios[index])
        self.wait.until(lambda d: d.find_elements(*self.ADDRESS_CARD_PRIMARY)[index].is_selected())

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

    def is_newest_address_added_and_selected(self):
        # billing_account_create_page.py'deki AYNI "yeni adres listenin
        # SONUNA eklenir VE otomatik seçilir" davranışı (canlı doğrulandı -
        # PAYLAŞILAN bileşen, aynı davranış).
        titles = self.get_address_titles()
        states = self.get_address_selection_states()
        last_title = titles[-1]
        return (
            self._new_address_street in last_title
            and self._new_address_building_no in last_title
            and states[-1] is True
        )

    # --- Navigasyon ---
    def click_back_and_wait_for_offer_selection(self):
        self.wait.until(EC.element_to_be_clickable(self.BACK_BUTTON)).click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='sales-offer-row']")))

    def click_next_and_wait_for_summary(self):
        self.wait.until(EC.element_to_be_clickable(self.NEXT_BUTTON)).click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='sales-summary-line']")))
