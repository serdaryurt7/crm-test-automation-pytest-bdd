"""Standart WebDriverWait'in karşılamadığı bekleme desenleri.

Buradaki fonksiyonlar "sabit süre bekle" DEĞİLDİR - hepsi bir KOŞUL
yokluyor. Ayrı bir modülde olmalarının sebebi şu: bazı koşullar tek bir
DOM sorgusuyla değerlendirilemez, çünkü koşulun değişmesi için bir
EYLEMİN TEKRARLANMASI gerekir (sayfa yenileme, yeniden arama). WebDriverWait
predicate'i içinde driver.get() çağırmak ise güvenli değildir.
"""
import time


def poll_until(condition, action=None, attempts=6, interval=2.0):
    """Bir eylemi tekrarlayarak koşulun sağlanmasını bekler.

    Her turda sırasıyla: action() -> interval kadar bekle -> condition()

    Beklemenin denemeler ARASINDA değil, eylemle kontrol ARASINDA olması
    kasıtlıdır: asenkron backend işlemlerinde (silme isteği kabul edilir
    ama saniyeler sonra tamamlanır) eylemin etkisinin oturması gerekir.

    Args:
        condition: argümansız çağrılır, doğruluk değeri döndürür.
        action: her turda condition'dan ÖNCE çalıştırılır (opsiyonel).
        attempts: en fazla deneme sayısı.
        interval: her turda eylem ile kontrol arasındaki bekleme (saniye).

    Returns:
        Koşul sağlandıysa True, denemeler tükendiyse False.

    Not: Bilerek exception FIRLATMIYOR. Çağıran sayfa nesneleri bu sonucu
    True/False olarak döndürüp iddiayı step katmanına bırakıyor; burada
    TimeoutException fırlatmak test başarısızlık mesajlarını değiştirirdi.
    """
    for _ in range(attempts):
        if action is not None:
            action()
        time.sleep(interval)
        if condition():
            return True
    return False


def wait_for_dom_settled(driver, root_locator=None, quiet_ms=150, timeout=1.5):
    """DOM belirli bir süre DEĞİŞMEYENE kadar bekler (quiescence).

    Angular gibi framework'lerde bir alana değer girip odak kaydırdıktan
    sonra form geçerliliğinin yeniden hesaplanması ayrı bir change-detection
    turunda gerçekleşir. "Ne bekleneceği" senaryoya göre değiştiğinde
    (bazen bir buton aktifleşmeli, bazen PASİF KALMALI) tek bir
    WebDriverWait koşulu yazılamaz - beklenmesi gereken şey, DOM'un
    DURULMASIDIR.

    Sabit bir time.sleep'e göre iki üstünlüğü var:
      - hızlı makinede quiet_ms kadar sonra ERKEN çıkar
      - yavaş makinede timeout'a kadar beklemeye devam eder

    Args:
        root_locator: gözlenecek kök eleman; None ise document.body.
        quiet_ms: bu kadar süre hiç mutasyon olmazsa "durulmuş" sayılır.
        timeout: en fazla beklenecek toplam süre (saniye).

    Returns:
        DOM durulduysa True, timeout'a takıldıysa False.
    """
    root = driver.find_element(*root_locator) if root_locator else None
    driver.execute_script(
        """
        const [el, quiet] = arguments;
        const target = el || document.body;
        window.__domSettled = false;
        if (window.__domSettleTimer) clearTimeout(window.__domSettleTimer);
        if (window.__domSettleObserver) window.__domSettleObserver.disconnect();

        const arm = () => {
            clearTimeout(window.__domSettleTimer);
            window.__domSettleTimer = setTimeout(() => {
                window.__domSettled = true;
                window.__domSettleObserver.disconnect();
            }, quiet);
        };
        window.__domSettleObserver = new MutationObserver(arm);
        window.__domSettleObserver.observe(target, {
            attributes: true, childList: true, subtree: true,
            characterData: true,
        });
        arm();
        """,
        root, quiet_ms,
    )

    deadline = time.time() + timeout
    while time.time() < deadline:
        if driver.execute_script("return window.__domSettled === true;"):
            return True
        time.sleep(0.05)

    driver.execute_script(
        "if (window.__domSettleObserver) window.__domSettleObserver.disconnect();"
    )
    return False
