Feature: Ürün Konfigürasyonu

  # KAPSAM DIŞI BIRAKILAN 3 SENARYO (kullanıcının kendi spesifikasyonunda
  # zaten belirsiz/şablon olarak işaretlenmişti - canlı keşifle netleştirildi):
  #
  # TC-EACRML-015-06 [ŞABLON]: 11 katalog teklifi + 3 kampanya taranarak 6
  # GERÇEK config template'i bulundu (Fiber: Fiber No/ONT Seri No, Mobil:
  # MSISDN/SIM No, Superbox: Cihaz Seri No/SIM No, TV: STB Seri No/Akıllı
  # Kart No, Sabit Hat: Hat No/Port No, Fiber Modem: yalnızca ONT Seri No).
  # AMA hiçbirinde GERÇEK bir format/regex doğrulaması yok - MSISDN alanına
  # "abcXYZ!!!" gibi tamamen geçersiz bir değer yazılıp diğer alanlar
  # doldurulduğunda sistem hiçbir uyarı göstermeden kabul etti, İleri aktif
  # oldu (sadece "boş olmama" kontrol ediliyor). Dokümanın kendisi bu
  # senaryonun bir şablon olduğunu ve gerçek validasyon tablosuna erişimin
  # olmadığını zaten belirtiyordu - kullanıcı kararıyla suite'e alınmadı,
  # BA/dev'e iletilmesi gereken bir madde olarak belgelendi.
  #
  # TC-EACRML-015-07 (CT-06, konfigürasyon gerektirmeyen ürün): 11 katalog
  # teklifinin VE 3 kampanyanın TAMAMI canlı tarandı - hiçbiri sıfır
  # konfigürasyon alanıyla gelmiyor, hepsi en az 1 alan istiyor. Önkoşulu
  # karşılayacak gerçek bir ürün bu ortamda yok (TC-013-02'deki kampanyasız
  # ürün eksikliğiyle aynı kapsam boşluğu) - kullanıcı kararıyla suite'e
  # alınmadı.
  #
  # TC-EACRML-015-08 (servis adresi seçilmeden Next'e basılması): Canlı
  # doğrulandı - müşterinin kayıtlı adresi her zaman en az 1 tane var (bu
  # framework'ün kendi kuralı) VE Config ekranına girildiğinde adres HER
  # ZAMAN otomatik olarak ön-seçili geliyor (ilk adres varsayılan seçili
  # radio buton). Kullanıcı hiçbir aksiyon almadan bile bir adres zaten
  # seçili olduğundan, "servis adresi seçilmemiş" durumu normal kullanıcı
  # akışıyla hiç oluşturulamıyor (TC-011-05/TC-013-05'teki gibi önkoşulu
  # gerçek uygulamada kurulamayan bir senaryo) - kullanıcı kararıyla
  # suite'e alınmadı.

  Scenario: TC-EACRML-015-01 - Sepetteki her teklif için ayrı bir konfigürasyon kartının görüntülenmesi
    Given kullanıcı sepete birden fazla teklif ekleyip İleri ile Ürün Konfigürasyonu ekranına geçmiştir
    Then sepetteki her teklif için ayrı bir konfigürasyon kartı (Ürün Teklif ID/Adı ile) görüntülenir

  Scenario: TC-EACRML-015-02 - Zorunlu konfigürasyon alanları boşken "İleri" butonunun pasif kalması
    Given kullanıcı Ürün Konfigürasyonu ekranındadır
    When zorunlu konfigürasyon alanları boş bırakılır
    Then İleri butonu pasif kalır

  Scenario: TC-EACRML-015-03 - Konfigürasyon ekranında hizmet adresi olarak müşterinin kayıtlı adreslerinden birinin seçilmesi
    Given kullanıcının birden fazla kayıtlı adresi olduğu Ürün Konfigürasyonu ekranındadır
    When müşterinin kayıtlı adreslerinden biri hizmet adresi olarak seçilir
    Then seçim işaretli olarak görüntülenir

  Scenario: TC-EACRML-015-04 - "Yeni Adres Ekle" ile konfigürasyon sırasında yeni bir hizmet adresinin eklenip seçilebilmesi
    Given kullanıcı Ürün Konfigürasyonu ekranındadır
    When "Yeni Adres Ekle" ile yeni bir hizmet adresi eklenir
    Then yeni adres seçili olarak listeye eklenir

  Scenario: TC-EACRML-015-05 - "Geri" butonuyla Teklif Seçimi ekranına dönüldüğünde sepetin ve girilen değerlerin korunması
    Given kullanıcı Ürün Konfigürasyonu ekranında konfigürasyon alanlarını doldurmuştur
    When "Geri" butonuna tıklanır
    Then Teklif Seçimi ekranına dönülür ve sepet korunur
    When kullanıcı tekrar İleri butonuna tıklar
    Then daha önce girilmiş teknik konfigürasyon değerleri korunmuş olarak görüntülenir

  Scenario: TC-EACRML-015-09 - Tüm zorunlu alanlar doldurulduğunda "İleri" butonunun aktif hale gelip Sipariş Özetine geçilmesi
    Given tüm zorunlu konfigürasyon alanları doldurulmuştur
    When İleri butonuna tıklanır
    Then Sipariş Özeti (Sipariş Gönder) ekranına geçilir
