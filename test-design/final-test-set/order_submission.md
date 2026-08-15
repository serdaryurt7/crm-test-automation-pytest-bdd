# UC-EACRML-016 — Siparişin Tamamlanması — Konsolide Final Test Seti

## Durum Özeti

- Kaynak: kullanıcının 8 senaryolu spesifikasyonu + `features/order_submission.feature`'daki 7 canlı doğrulanmış senaryo.
- **016-02 [DEFEKT ADAYI] netleşti:** UC-014-08 ile aynı ekranı/kök nedeni test ediyor — canlı olarak toplam 5 ayrı denemede (3'ü UC-014, 2'si bu UC'de) hiç yeniden üretilemedi. Spesifikasyonun doğru davranışını assert eden bir regresyon-guard'ı olarak bırakıldı (bilinçli olarak UC-014-08 ile yapısal tekrar — INVEST/Independent: her UC kendi feature dosyasında bağımsız kanıt sunabilsin diye).
- **016-05 KESİN olarak netleşti (doküman bunu teyit edemiyordu):** sipariş gönderildiğinde kullanıcı Müşteri Hesabı'na otomatik yönlendirilmiyor — "Sipariş oluşturuldu!" başlıklı ayrı bir başarı ekranında (Sipariş ID + "Müşteri Aramaya Dön" linkiyle) kalıyor.
- **016-06 YENİ TEKNİK ile otomasyona alındı:** Chrome DevTools Protocol (`Network.emulateNetworkConditions(offline=True)`) ile gerçek bir ağ/sunucu hatası simüle edildi — uygulama düzgün ele alıyor, "Sipariş gönderilemedi. Lütfen tekrar deneyin." mesajı gösteriliyor, başarı ekranına yanlışlıkla geçilmiyor.
- **016-08 (benzersiz Order ID) canlı doğrulandı:** art arda 3 sipariş oluşturulduğunda 3 farklı 8 haneli Sipariş ID'si üretiliyor.

## Gherkin — Final Senaryo Seti

```gherkin
Feature: Siparişin Tamamlanması

  Scenario: TC-EACRML-016-01 - Sipariş Gönder ekranında seçilen tekliflerin, hizmet adresinin ve toplam tutarın özet olarak görüntülenmesi
    Given kullanıcı Ürün Konfigürasyonu adımını tamamlamıştır
    When Sipariş Gönder ekranına geçilir
    Then seçilen teklifler, hizmet adresi ve toplam tutar özet olarak görüntülenir

  Scenario: TC-EACRML-016-02 [DEFEKT ADAYI - yeniden üretilemedi] - Sepete tek kez eklenen bir teklifin sipariş özetinde de tam bir kez görüntülenmesi
    Given kullanıcı sepete yalnızca bir kez bir teklif eklemiştir
    Then özet listesinde bu teklif TAM 1 KEZ, doğru toplam tutarla görüntülenmelidir

  Scenario: TC-EACRML-016-03 - "Gönder" butonuna tıklandığında siparişin oluşturulup ilgili ürünlerin fatura hesabına eklenmesi
    Given kullanıcı Sipariş Gönder ekranındadır
    When "Gönder" butonuna tıklanır
    Then sipariş oluşturulur, ürünler ilgili fatura hesabına eklenir

  Scenario: TC-EACRML-016-04 - "Geri" butonuyla Ürün Konfigürasyonu ekranına dönülüp bilgilerin korunması
    Given kullanıcı Sipariş Gönder ekranındadır
    When "Geri" butonuna tıklanır
    Then Ürün Konfigürasyonu ekranına dönülür ve girilen bilgiler korunur

  Scenario: TC-EACRML-016-05 [NETLEŞTİRİLDİ] - Sipariş başarıyla tamamlandıktan sonra ayrı bir başarı ekranının ve Sipariş ID'sinin gösterilmesi
    Given kullanıcı siparişi başarıyla göndermiştir
    Then "Sipariş oluşturuldu!" başlıklı bir başarı ekranı görüntülenir
    And bir Sipariş ID'si gösterilir

  Scenario: TC-EACRML-016-06 - Sipariş gönderimi sırasında bir iletişim/sunucu hatası oluşması durumunda kullanıcıya anlamlı bir hata mesajı gösterilmesi
    Given kullanıcı Sipariş Gönder ekranındadır
    When "Gönder" isteği sırasında bir sunucu/ağ hatası simüle edilir
    Then kullanıcıya anlamlı bir hata mesajı gösterilir
    And yanlış bir başarı yönlendirmesi yapılmaz

  Scenario: TC-EACRML-016-08 - Submit Order ekranında benzersiz Order ID üretilmesi
    Given "Product Configuration" tamamlanmış ve "Submit Order" ekranı açılmıştır
    When art arda birden fazla sipariş oluşturulur
    Then her siparişin Order ID'si birbirinden farklıdır
```

## Kapsam Dışı / Askıda Kalanlar

| TC ID | Durum | Gerekçe |
|---|---|---|
| TC-EACRML-016-07 (ana + tamamlayıcı ürün toplam tutarı) | Askıda | UC-014-06/07'deki AYNI onaylanmamış "tamamlayıcı ürün" kavramına bağımlı — o kavram netleşmeden bu test de anlamsız. |

## Notlar

- Sınır değer kontrolleri bu UC'nin kapsamında değil (özet/gönderim akışı, alan girişi yok).
