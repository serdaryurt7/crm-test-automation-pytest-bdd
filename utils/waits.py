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
