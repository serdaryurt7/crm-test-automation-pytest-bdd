"""Dil bağımsız metin karşılaştırma yardımcıları.

Python'un `str.lower()`'ı Türkçe'ye özgü harfleri beklendiği gibi
ele almaz. En sinsi durum `İ`:

    >>> len("İ".lower())
    2                       # 'i' + U+0307 (birleşen nokta)

Bu yüzden `"internet" in "Ev İnterneti Fiber 1000".lower()` **False**
döner. Karşılaştırma uygulamanın kendi eşleştirme toleransından daha
katı olduğunda, sonuç kümesinde hiçbir gerçek hata yokken test kırmızı
verir.
"""

_TURKISH_FOLD_MAP = str.maketrans(
    {
        "ı": "i", "İ": "i", "I": "i",
        "ğ": "g", "Ğ": "g",
        "ş": "s", "Ş": "s",
        "ç": "c", "Ç": "c",
        "ö": "o", "Ö": "o",
        "ü": "u", "Ü": "u",
    }
)


def turkish_fold(text):
    """Metni Türkçe'ye duyarsız karşılaştırma için normalize eder.

    Karşılaştırmanın HER İKİ tarafına da uygulanmalıdır:

        turkish_fold(aranan) in turkish_fold(satır_metni)

    Yalnızca bir tarafa uygulamak sorunu çözmez.
    """
    return text.translate(_TURKISH_FOLD_MAP).lower()


def parse_price(text):
    """Arayüzdeki para metnini sayıya çevirir: "1,299.90 TL" -> 1299.90.

    Virgül binlik ayırıcı olarak atılıyor, "TL" soneki kaldırılıyor.
    Bu dönüşüm 2 sayfa dosyasında 4 kez birebir tekrarlanıyordu; para
    biçimi değişirse (ör. "₺" simgesi ya da ondalık virgül) tek yer
    güncellenecek.
    """
    return float(text.replace("TL", "").replace(",", "").strip())
