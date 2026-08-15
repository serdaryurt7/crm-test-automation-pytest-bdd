import os

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Zaman aşımı artık TEK yerden yönetiliyor. Yavaş bir CI ortamında
# DEFAULT_TIMEOUT ortam değişkenini yükseltmek, 13 sayfa dosyasına
# dokunmadan tüm beklemeleri etkiler.
DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", "10"))
SLOW_TIMEOUT = int(os.getenv("SLOW_TIMEOUT", "30"))

# StaleElementReferenceException, Angular gibi DOM'u sürekli yeniden çizen
# framework'lerde en yaygın flaky kaynağıdır: WebDriverWait bir elemanı
# bulur, aradan Angular'ın change detection'ı geçer, eleman DOM'dan
# koparılıp yenisiyle değiştirilir ve sonraki erişim patlar.
#
# Bu koruma daha önce SADECE create_customer_page ve search_customers_page
# içinde vardı; diğer 11 sayfada yoktu. offer_selection_page'deki
# TC-014-12 flaky'sinin kök nedeni tam olarak buydu. Korumayı tek tek
# sayfalara eklemek yerine ortak ataya koymak, yeni eklenen bir sayfada
# UNUTULMASINI imkansız kılıyor.
_IGNORED = (StaleElementReferenceException,)


class BasePage:
    """Tüm page object'lerin ortak atası.

    Sorumluluğu iki şeyle sınırlı:
      1. driver ve wait örneklerini tek ve tutarlı biçimde kurmak
      2. her sayfada tekrarlanan temel etkileşimleri sunmak

    Alt sınıflar kendi __init__'lerini KORUR; yalnızca ortak iki satırı
    super().__init__(driver) ile değiştirirler. Sayfaya özel hazır-olma
    beklemeleri ve durum alanları alt sınıfta kalmaya devam eder.

    Not: poll_frequency bilerek Selenium'un varsayılanında (0.5sn)
    bırakıldı. Bu bir REFACTOR'dır - yapı değişir, davranış değişmez.
    Yoklama sıklığını değiştirmek ölçülmemiş bir zamanlama değişikliği
    getirirdi ve refactor'un regresyon ürettiğini ayırt etmeyi zorlaştırırdı.
    """

    def __init__(self, driver, timeout=None):
        self.driver = driver
        self.wait = WebDriverWait(
            driver,
            timeout or DEFAULT_TIMEOUT,
            ignored_exceptions=_IGNORED,
        )
        # Asenkron backend işlemleri (ör. silme isteğinin arka planda
        # tamamlanması) için; kısa bekleme yetersiz kaldığında kullanılır.
        self.slow_wait = WebDriverWait(
            driver,
            SLOW_TIMEOUT,
            ignored_exceptions=_IGNORED,
        )

    # ------------------------------------------------------------------
    # Eleman bulma
    # ------------------------------------------------------------------
    def find(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def find_visible(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def find_all(self, locator):
        """Beklemeden anlık liste döndürür - 'hiç yok' da geçerli bir cevaptır."""
        return self.driver.find_elements(*locator)

    def count(self, locator):
        return len(self.driver.find_elements(*locator))

    # ------------------------------------------------------------------
    # Etkileşim
    # ------------------------------------------------------------------
    def click(self, locator):
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def js_click(self, locator):
        """Selenium'un hesapladığı tıklama noktası bir kaplama (overlay)
        nedeniyle şaştığında kullanılır - login-password-toggle'da
        kanıtlanmış bir ihtiyaç."""
        self.driver.execute_script("arguments[0].click();", self.find(locator))

    def type(self, locator, text, clear=True):
        field = self.find_visible(locator)
        if clear:
            field.clear()
        if text:
            field.send_keys(text)
        return field

    # ------------------------------------------------------------------
    # Okuma
    # ------------------------------------------------------------------
    def text_of(self, locator):
        """find + .text'i TEK bir retry'lanan lambda içinde yapar.

        Bunları ayrı ayrı yapmak (önce visibility_of_element_located, sonra
        .text) aradaki DOM yenilenmesinde stale hatası üretir - bu hata
        daha önce canlı olarak yaşandı.
        """
        return self.wait.until(lambda d: d.find_element(*locator).text)

    def value_of(self, locator):
        return self.find(locator).get_attribute("value") or ""

    def attribute_of(self, locator, name):
        return self.find(locator).get_attribute(name)

    def is_displayed(self, locator):
        elements = self.find_all(locator)
        return bool(elements) and elements[0].is_displayed()

    def is_enabled(self, locator):
        return self.find(locator).is_enabled()

    def is_disabled(self, locator):
        return not self.is_enabled(locator)

    # ------------------------------------------------------------------
    # Beklemeler
    # ------------------------------------------------------------------
    def wait_until_visible(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def wait_until_gone(self, locator):
        return self.wait.until(EC.invisibility_of_element_located(locator))

    def wait_for_url_contains(self, fragment):
        return self.wait.until(lambda d: fragment in d.current_url)

    def wait_for_count(self, locator, expected):
        return self.wait.until(lambda d: len(d.find_elements(*locator)) == expected)

    # ------------------------------------------------------------------
    # Tarayıcı
    # ------------------------------------------------------------------
    def open(self, url):
        self.driver.get(url)
        return self

    def refresh(self):
        self.driver.refresh()
        return self

    @property
    def current_url(self):
        return self.driver.current_url

    def browser_logs(self):
        """JS hatalarını yakalamanın en ucuz yolu; her tarayıcı desteklemez."""
        try:
            return self.driver.get_log("browser")
        except Exception:
            return []
