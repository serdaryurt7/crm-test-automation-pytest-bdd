# UC-EACRML-015 — Ürün Konfigürasyonu — Konsolide Final Test Seti

## Durum Özeti

- Kaynak: kullanıcının 9 senaryolu spesifikasyonu + `features/product_configuration.feature`'daki 6 canlı doğrulanmış senaryo.
- Canlı keşifle 6 gerçek config template'i tespit edildi (Fiber, Mobil, Superbox, TV, Sabit Hat, Fiber Modem) — hiçbirinde gerçek format/regex validasyonu yok, yalnızca "boş olmama" kontrol ediliyor (TC-015-02 bunu zaten kapsıyor).
- 015-05'e canlı keşifle pozitif bir ek bulgu eklendi: "Geri" ile Teklif Seçimi'ne dönülüp tekrar "İleri"ye basıldığında, daha önce girilmiş teknik konfigürasyon değerleri de (sadece sepet değil) korunuyor.

## Gherkin — Final Senaryo Seti

```gherkin
Feature: Ürün Konfigürasyonu

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
```

## Kapsam Dışı / Askıda Kalanlar

| TC ID | Durum | Gerekçe |
|---|---|---|
| TC-EACRML-015-06 [ŞABLON — dokümanın kendisi de belirsiz işaretlemişti] | Kapsam dışı, bulgu belgelendi | 6 config template'inin HİÇBİRİNDE gerçek format/regex validasyonu yok — MSISDN alanına "abcXYZ!!!" yazılıp diğer alanlar doldurulunca sistem hiçbir uyarı vermeden kabul etti. TC-015-02 zaten "boş olmama" kuralını kapsıyor; format validasyonu eklenirse ayrı senaryolar yazılmalı. |
| TC-EACRML-015-07 (CT-06, konfigürasyon gerektirmeyen ürün) | Kapsam dışı | 11 katalog teklifi + 3 kampanyanın tamamı tarandı, sıfır konfigürasyon alanlı tek bir ürün/kampanya yok — önkoşulu karşılayacak gerçek veri bu ortamda mevcut değil. |
| TC-EACRML-015-08 (servis adresi seçilmeden Next'e basılması) | Kapsam dışı | Müşterinin kayıtlı adresi her zaman en az 1 tane var (framework kuralı) ve Config ekranına girildiğinde adres her zaman otomatik ön-seçili geliyor — "adres seçilmemiş" durumu normal kullanıcı akışıyla hiç oluşturulamıyor. |

## Notlar

- Hizmet adresi alt-bileşeni burada da (TC-015-04) `address_update.md`/`address_add.md` ile **aynı paylaşılan bileşen**dir — adres sınır değer kontrolleri tekrar edilmedi.
- Demografik/İletişim sınır değer kontrolleri bu UC'nin kapsamında değil.
