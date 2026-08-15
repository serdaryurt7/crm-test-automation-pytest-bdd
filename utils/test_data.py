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

# Tek paylaşılan örnek. Faker örnekleri birbirinden bağımsız rastgele
# akışlardır; tek bir örneği paylaşmak davranışı değiştirmez (hiçbiri
# seed'lenmiyordu) ama iki örneğin aynı diziyi üretme ihtimalini de
# tamamen ortadan kaldırır.
fake = Faker("tr_TR")


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
