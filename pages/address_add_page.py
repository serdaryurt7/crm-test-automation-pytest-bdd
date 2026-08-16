from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

from pages.address_update_page import AddressUpdatePage


class AddressAddPage(AddressUpdatePage):
    # "Yeni Adres Ekle" formu, adres GÜNCELLEME formuyla AYNI DOM/alan
    # setini kullanıyor (canlı doğrulandı) - bu yüzden locator'lar ve
    # temel doldurma/kaydetme mekaniği AddressUpdatePage'den miras
    # alınıyor, sadece bu Feature'a özgü (Ekle akışına özel) davranışlar
    # burada eklidir.

    def fill_new_address_form(self, street, building_no, description, skip_field=None):
        if skip_field != "Şehir":
            self.select_random_option(self.CITY_BUTTON, self.CITY_LIST, self.CITY_OPTIONS)
        if skip_field != "Sokak":
            self.driver.find_element(*self.STREET_INPUT).send_keys(street)
        if skip_field != "Bina No":
            self.driver.find_element(*self.BUILDING_INPUT).send_keys(building_no)
        if skip_field != "Açıklama":
            self.driver.find_element(*self.DESCRIPTION_INPUT).send_keys(description)

    def save_new_address_and_wait_for_card(self):
        before_count = self.get_card_count()
        self.click_save()
        self.wait.until(lambda d: len(d.find_elements(*self.ADDRESS_CARD)) > before_count)

    def add_new_address_and_wait_for_card(self, street, building_no, description):
        self._pre_add_titles = self.get_all_card_titles()
        self.click_add_address()
        self.fill_new_address_form(street, building_no, description)
        self.save_new_address_and_wait_for_card()
        self._new_street = street
        self._new_building_no = building_no

    def get_all_card_titles(self):
        return [e.text for e in self.driver.find_elements(*self.ADDRESS_CARD_TITLE)]

    def get_all_card_details(self):
        return [e.text for e in self.driver.find_elements(*self.ADDRESS_CARD_DETAIL)]

    def is_new_card_added_as_separate_card(self):
        titles = self.get_all_card_titles()
        return (
            len(titles) == len(self._pre_add_titles) + 1
            and all(t in titles for t in self._pre_add_titles)
            and any(self._new_street in t and self._new_building_no in t for t in titles)
        )

    def is_new_card_last_and_well_formed(self):
        # Canlı doğrulandı: yeni eklenen adres listenin SONUNA ekleniyor
        # (mevcut kartların önüne değil) - bu yüzden "son kart" yeni
        # eklenen kartla eşleştiriliyor.
        titles = self.get_all_card_titles()
        details = self.get_all_card_details()
        last_title = titles[-1]
        last_detail = details[-1]
        parts = [p.strip() for p in last_title.split(",")]
        return (
            self._new_street in last_title
            and self._new_building_no in last_title
            and len(parts) == 3
            and all(parts)
            and bool(last_detail.strip())
        )

    def wait_for_new_address_persisted_after_reload(self):
        # Adres Primary-güncelleme senaryosunda öğrenilen desenin devamı:
        # yeni adresin GERÇEKTEN backend'e kaydedildiğini (sadece iyimser
        # bir istemci-tarafı UI güncellemesi değil) sayfa yenilendikten
        # SONRA da kartın hâlâ mevcut olup olmadığını kontrol ederek
        # doğruluyoruz. Zone.js nedeniyle JS-seviyesi XHR/fetch
        # interception bu projede güvenilmez olduğu için (bu oturumda
        # defalarca doğrulandı), ağı doğrudan dinlemek yerine
        # GÖZLEMLENEBİLİR SONUCU (kalıcılık) WebDriverWait'in dinamik
        # polling mekanizmasıyla doğruluyoruz - sabit bir bekleme değil.
        detail_url = self.driver.current_url
        expected_street = self._new_street
        expected_building_no = self._new_building_no

        def new_card_present_after_reload(driver):
            driver.get(detail_url)
            self.wait.until(EC.element_to_be_clickable(self.TAB_ADDRESS)).click()
            self.wait.until(EC.visibility_of_element_located(self.ADDRESS_CARD))
            return any(
                expected_street in t and expected_building_no in t
                for t in self.get_all_card_titles()
            )

        try:
            return self.wait.until(new_card_present_after_reload)
        except TimeoutException:
            return False

    def open_city_dropdown(self):
        self.driver.find_element(*self.CITY_BUTTON).click()
        self.wait.until(EC.visibility_of_element_located(self.CITY_LIST))

    def is_city_dropdown_restricted_to_defined_provinces(self, expected_count=81):
        # "Serbest metin girişine izin verilmez" yapısal olarak
        # doğrulanıyor: Şehir kontrolü bir <button> (aria-controls ile
        # bir listbox açıyor), <input type="text"> DEĞİL - yani serbest
        # metin girişi için bir alan yapısal olarak hiç mevcut değil
        # (canlı DOM incelemesiyle doğrulandı). 81 = Türkiye'nin sabit il
        # sayısı; bu, uygulamanın değişebilir bir verisi değil, sabit bir
        # coğrafi gerçek olduğu için burada statik kalması kasıtlı/doğru.
        options = self.driver.find_elements(*self.CITY_OPTIONS)
        city_button_tag = self.driver.find_element(*self.CITY_BUTTON).tag_name.lower()
        return len(options) == expected_count and city_button_tag == "button"

    def type_into_building_no(self, value):
        field = self.driver.find_element(*self.BUILDING_INPUT)
        field.click()
        field.send_keys(value)

    def get_building_no_value(self):
        return self.driver.find_element(*self.BUILDING_INPUT).get_attribute("value")

    def snapshot_card_count(self):
        self._snapshot_count = self.get_card_count()

    def card_count_matches_snapshot(self):
        return self.get_card_count() == self._snapshot_count
