import os

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
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
      2. KANITLANMIŞ ortak etkileşimi sunmak (şu an yalnızca `fill`)

    Alt sınıflar kendi __init__'lerini KORUR; yalnızca ortak iki satırı
    super().__init__(driver) ile değiştirirler. Sayfaya özel hazır-olma
    beklemeleri ve durum alanları alt sınıfta kalmaya devam eder.

    Not: poll_frequency bilerek Selenium'un varsayılanında (0.5sn)
    bırakıldı. Bu bir REFACTOR'dır - yapı değişir, davranış değişmez.
    Yoklama sıklığını değiştirmek ölçülmemiş bir zamanlama değişikliği
    getirirdi ve refactor'un regresyon ürettiğini ayırt etmeyi zorlaştırırdı.

    NEDEN BU KADAR KÜÇÜK (Faz J2):
    Bu sınıf ilk yazıldığında 21 yardımcı içeriyordu (`find`, `click`,
    `text_of`, `wait_until_gone`, ...). Sonradan ölçüldü: **19'u hiç
    çağrılmamıştı.** Üstelik biri (`type`) yalnızca ölü değil YANLIŞTI -
    `field.clear()` kullanıyordu ve bu uygulamada Angular doğrulamasını
    tetiklemiyor; kullanılsaydı sahte bulgu üretirdi. Yani kullanılmayan
    yardımcı zararsız değildir: kimse çağırmadığı için kimse hatasını da
    fark etmez.

    Bu yüzden buraya bir yardımcı, ancak **onu çağıran kod ile aynı
    commit'te** eklenmelidir. "Şimdilik dursun, sonra kullanırız" bu
    projede iki kez denendi (`wait_for_dom_settled` ve bu 19 metot),
    ikisi de ölü kod olarak silindi.

    Sayfaların doğrudan `self.driver.find_element` / `self.wait.until`
    kullanması BİLİNÇLİ olarak korunuyor: bunları `find()` gibi bekleme
    EKLEYEN sarmalayıcılara çevirmek 276 çağrı yerinde davranış
    değişikliği olurdu, yapı değişikliği değil.
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


    def fill(self, locator, text=None, blur=False):
        """Alanı temizler, (verilmişse) yeni değeri yazar, (istenirse) odağı kaydırır.

        `field.clear()` BİLEREK KULLANILMIYOR. Bu uygulamada canlı
        doğrulandı: `.clear()` alanın değerini siler ama Angular'ın
        blur/`touched` durumunu tetiklemez - form kendini geçersiz
        saymaz, hata mesajı çıkmaz, Kaydet butonu pasifleşmez. Bu, bir
        oturumda "boş ad kaydedilebiliyor" şeklinde SAHTE bir bulguya yol
        açmıştı; doğru ölçüm (Ctrl+A → Backspace → Tab) uygulamanın
        aslında doğru davrandığını gösterdi.

        Bu yüzden gerçek kullanıcı etkileşimi taklit ediliyor:
        tıkla → tümünü seç → sil → yaz. Bu desen 6 sayfa dosyasında
        18 kez elle tekrarlanıyordu; `offer_selection_page` onu zaten
        yerel bir `_set_field()` yardımcısına çıkarmıştı - yani ihtiyaç
        kanıtlıydı, yalnızca yanlış katmandaydı.

        Args:
            locator: hedef alan.
            text: yazılacak değer; None/boş ise alan yalnızca temizlenir.
            blur: True ise sonunda Tab gönderilir. Angular'ın doğrulamayı
                çalıştırması için alanın `touched` olması gerektiğinden,
                hata mesajı/buton durumu doğrulayan senaryolarda ŞART.

        Returns:
            Alanın WebElement'i - çağıran `get_attribute("value")` ile
            tarayıcının kabul ettiği değeri okuyabilsin diye (sınır değer
            testlerinde kullanılıyor).
        """
        field = self.driver.find_element(*locator)
        field.click()
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACK_SPACE)
        if text:
            field.send_keys(text)
        if blur:
            field.send_keys(Keys.TAB)
        return field


    def wait_for_url_contains(self, fragment):
        return self.wait.until(lambda d: fragment in d.current_url)
