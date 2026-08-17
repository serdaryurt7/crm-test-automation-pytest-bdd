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

# --- ALAN SINIRLARI ---
# Uygulamanın kabul ettiği azami uzunluklar (canlı doğrulandı).
#
# NEDEN ÇIPLAK SAYI DEĞİL DE ALAN ADIYLA: bugün username, first_name ve
# last_name'in üçü de 50. Tek bir MAX_50 sabitine bağlamak, ilgisiz
# alanları birbirine kenetlerdi - biri değişince diğerleri de sessizce
# değişirdi (SOLID/tek sorumluluk).
#
# NEDEN ÖNEMLİ: sınır testleri "limit" ve "limit+1" değerlerini BİRLİKTE
# kullanıyor. Bu ikisi ayrı ayrı yazıldığında (50 ve 51) biri güncellenip
# diğeri unutulabilir; o durumda test kırılmaz, sessizce YANLIŞ sınırı
# doğrulamaya başlar. Artık "limit+1" ifadesi FIELD_LIMITS'ten türetiliyor.
FIELD_LIMITS = {
    "username": 50,
    "password": 50,
    "first_name": 50,
    "last_name": 50,
    # İkinci Ad / Baba Adı / Anne Adı - create_customer'ın opsiyonel alanları
    "optional_name": 100,
    "identity_number": 11,
    "gsm": 10,
    "customer_id": 20,
    # Biçimlendirilmiş doğum tarihi uzunluğu (gg/aa/yyyy) - azami sınır
    # DEĞİL, beklenen tam uzunluk.
    "birth_date_formatted": 10,
}


# --- KATALOG VERİSİ ---
# Bu adlar uygulamanın teklif kataloğundan gelir; testler onları
# üretmez, VAR OLDUKLARINI varsayar. Katalog değişirse burası tek
# güncelleme noktasıdır. Her sabitin YANINDA neden o teklifin seçildiği
# yazıyor - yoksa bir sonraki kişi rastgele başka bir teklifle değiştirir
# ve senaryo sessizce farklı bir şey test etmeye başlar.

# Zorunlu tamamlayıcı ürün İSTEMEYEN, en az adımda satın alınabilen
# teklif (canlı doğrulandı). Kurulum amaçlı senaryoların varsayılanı.
SIMPLE_OFFER = "Mobil 20GB Paket"

# SIMPLE_OFFER'ın arama filtresinde kullanılan ÖN EKİ. Tam ad DEĞİL:
# "içeren" aramasının çalıştığı test edildiği için bilinçli olarak kısa.
SIMPLE_OFFER_SEARCH_TERM = "Mobil 20GB"

# Yalnızca <input> alanı içeren (dropdown İÇERMEYEN) ikinci basit
# şablonlu teklif - "sepette birden fazla teklif" senaryolarında
# SIMPLE_OFFER ile birlikte kullanılıyor.
SECOND_SIMPLE_OFFER = "Superbox 50GB"

# Fatura hesabı ürün listesinde ikinci ürün olarak kullanılıyor.
SECOND_PRODUCT_OFFER = "TV Başlangıç Paketi"

# Mükerrer sepete ekleme senaryosunun (TC-014-13) teklifi.
DUPLICATE_TEST_OFFER = "Ev İnterneti Fiber 100"

# Tek paylaşılan örnek. Faker örnekleri birbirinden bağımsız rastgele
# akışlardır; tek bir örneği paylaşmak davranışı değiştirmez (hiçbiri
# seed'lenmiyordu) ama iki örneğin aynı diziyi üretme ihtimalini de
# tamamen ortadan kaldırır.
fake = Faker("tr_TR")


# --- TEST VERİSİNİN İZLENEBİLİRLİĞİ ---
# Testler her koşumda gerçek müşteri kaydı oluşturuyor ve bunlar
# SİLİNMİYOR (bkz. mimari.md K4b - otomatik temizlik api_client'a bağlı).
# Faker gerçekçi Türkçe adlar ürettiği için bu kayıtlar bugüne kadar
# gerçek müşterilerden AYIRT EDİLEMİYORDU: elle temizlemek isteyen biri
# bile hangilerinin test artığı olduğunu bulamazdı.
#
# Bu işaret, üretilen her e-postaya konuyor. Taşıyıcı olarak e-posta
# ÖLÇÜLEREK seçildi: (a) zaten sentetik ("example.com"), (b) hiçbir
# assertion biçimine bağlı değil, (c) ad/soyad gibi arama testlerinin
# kullandığı alanlara dokunmuyor.
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
