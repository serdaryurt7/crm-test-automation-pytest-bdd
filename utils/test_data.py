"""Test verisi üretiminin TEK kaynağı.

Buradan önce 11 ayrı modül (7 step + 4 page) kendi `Faker("tr_TR")`
örneğini kuruyordu. Yerel ayarı değiştirmek ya da üretilen veriye ortak
bir kural eklemek (ör. testlerin oluşturduğu kayıtları ayırt etmek için
sabit bir önek) 11 dosyaya dokunmayı gerektiriyordu.

KAPSAM (bilinçli olarak dar tutuldu): burada yalnızca GERÇEKTEN
tekrarlanan şeyler var. mimari.md §6.5'te ayrıca bir `FIELD_LIMITS`
sözlüğü önerilmişti; kodda hiçbir yer onu kullanmadığı (alan sınırları
Gherkin Examples tablolarında yaşıyor) için YAGNI gereği yazılmadı.
"""
from faker import Faker

FIELD_LIMITS = {
    "username": 50,
    "password": 50,
    "first_name": 50,
    "last_name": 50,
    "optional_name": 100,
    "identity_number": 11,
    "gsm": 10,
    "customer_id": 20,
    "birth_date_formatted": 10,
}


SIMPLE_OFFER = "Mobil 20GB Paket"

SIMPLE_OFFER_SEARCH_TERM = "Mobil 20GB"

SECOND_SIMPLE_OFFER = "Superbox 50GB"

SECOND_PRODUCT_OFFER = "TV Başlangıç Paketi"

DUPLICATE_TEST_OFFER = "Ev İnterneti Fiber 100"

fake = Faker("tr_TR")


TEST_DATA_MARKER = "qa-otomasyon"


def new_email():
    """Testlerin oluşturduğu kayıtlar için benzersiz, İŞARETLİ e-posta.

    Alan adı BİLEREK "example.com": canlı doğrulandı, uygulamanın form
    doğrulaması e-postanın ".com" ile bitmesini zorunlu kılıyor
    ("Geçerli bir e-posta girin; adres .com ile bitmelidir.") ve
    `fake.email()` bazen .org/.net üretip bu kurala takılıyordu.

    6 haneli rastgele sayı benzersizlik için: backend e-postanın
    benzersiz olmasını zorunlu kılıyor (koşumlar arası 400 "already
    registered" çakışması canlı yaşandı).
    """
    return f"{TEST_DATA_MARKER}.{fake.user_name()}.{fake.random_number(digits=6, fix_len=True)}@example.com"


def new_mobile_phone():
    """Türkiye GSM formatında numara: 5 ile başlayan 10 hane.

    Faker'ın genel `phone_number()` sağlayıcısı boşluk/parantez
    içerdiğinden kullanılmıyor - alan yalnızca rakam kabul ediyor.
    """
    return fake.numerify("5#########")


def new_address_args(nb_words=4):
    """Yeni adres formu için (sokak, bina no, açıklama) üçlüsü.

    Bu üçlü 4 step dosyasında 12 kez birebir tekrarlanıyordu;
    `test_address_delete_steps.py` onu zaten yerel bir yardımcıya
    çıkarmıştı - burası o yardımcının ait olduğu yer.

    Args:
        nb_words: açıklama alanı için üretilecek kelime sayısı
            (bazı çağrılar 3, çoğu 4 kullanıyor).
    """
    return fake.street_name(), fake.building_number(), fake.sentence(nb_words=nb_words)
