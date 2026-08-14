# UC-EACRML-010 — Yeni Fatura Hesabı Oluşturma — Konsolide Final Test Seti

## Durum Özeti

- Kaynak: `features/billing_account_create.feature`'daki 13 canlı doğrulanmış senaryo.
- Dokümanın 3 bulgusu da zaten kapatılmış: (1) Address'in de zorunlu olduğu 010-04/010-01 kapsamında görünür kılınmış (Address alanı yapısal olarak her zaman bir varsayılanla dolu geldiğinden — müşterinin en az 1 adresi garanti — "boşaltma" senaryosu Şehir ile aynı gerekçeyle uygulanmıyor, bkz. Notlar), (2) 010-02 numaralandırma çakışması çözülmüş, (3) 010-03 click-then-error/disabled belirsizliği net bir tek ifadeyle ("alan hatalı işaretlenir + buton pasif kalır") kapatılmış, (4) tablo/sayfalama boşluğu 010-10a/b/c ile kapanmış.
- Hesap Adı alanı için sınır-değer çifti (010-09a kabul / 010-09b — gerçek uygulamada üst sınır YOK, kasıtlı kırmızı) zaten mevcut; bu UC'de kullanıcının istediği 3 yeni kategoriden (demografik/adres/iletişim) hiçbiri doğrudan uygulanmıyor — Address alt-bileşeni zaten `address_update.md`'de kapsanan aynı Sokak/Bina No/Açıklama alanlarını kullanıyor (bkz. Notlar), tekrar test edilmedi.

## Gherkin — Final Senaryo Seti

```gherkin
Feature: Yeni Fatura Hesabı Oluşturma

  Scenario: TC-EACRML-010-01 - "Yeni Hesap Oluştur" ile Hesap Adı ve Adres girilip fatura hesabının oluşturulması
    Given kullanıcı bir müşterinin Müşteri Hesabı sekmesindedir
    When kullanıcı "Yeni Hesap Oluştur" butonuna tıklayıp Hesap Adı ve Adres (hizmet adresi) alanlarını doldurup Oluştur'a tıklar
    Then sistem fatura hesabını kalıcı olarak oluşturur (sayfa yenilense dahi listede görünür)

  Scenario: TC-EACRML-010-02 - İlk hesap oluşturulmadan önce boş durum mesajının görüntülenmesi
    Given müşterinin hiç kayıtlı fatura hesabı yoktur
    When Müşteri Hesabı sekmesi açılır
    Then hesap bulunamadı durumunu belirten bir mesaj görüntülenir

  Scenario: TC-EACRML-010-03 - Hesap Adı boşken hesabın oluşturulamaması
    Given kullanıcı hesap oluşturma formundadır
    When Hesap Adı alanı boşaltılır
    Then ilgili alan hatalı olarak işaretlenir
    And Oluştur butonu pasif kalır, fatura hesabı oluşturulmaz

  Scenario: TC-EACRML-010-04 - Hesap oluşturma formunda müşterinin kayıtlı adreslerinden birinin hizmet adresi olarak seçilebilmesi
    Given müşterinin birden fazla kayıtlı adresi vardır
    When kullanıcı hesap formunda ikinci adresi hizmet adresi olarak seçer
    Then seçim formda işaretli görüntülenir

  Scenario: TC-EACRML-010-05 - Formda "Yeni Adres Ekle" ile hesap oluşturma sırasında yeni bir adresin de eklenebilmesi
    Given kullanıcı hesap oluşturma formundadır
    When "Yeni Adres Ekle" ile yeni bir adres eklenir
    Then yeni adres formda seçili hizmet adresi olarak görüntülenir

  Scenario: TC-EACRML-010-06 - Oluşturulan hesabın listede otomatik üretilen hesap numarası ve durum bilgisiyle görüntülenmesi
    Given kullanıcı bir fatura hesabı oluşturmuştur
    When Müşteri Hesabı listesi görüntülenir
    Then yeni hesap otomatik üretilmiş bir hesap numarasıyla listelenir
    And hesabın durum bilgisi görüntülenir

  Scenario: TC-EACRML-010-07 - Aynı müşteriye birden fazla fatura hesabı açılabilmesi
    Given müşterinin zaten bir fatura hesabı vardır
    When ikinci bir hesap daha oluşturulur
    Then her iki hesap da birbirinden bağımsız ayrı satırlar olarak listelenir

  Scenario: TC-EACRML-010-08 - Hesap oluşturma formu iptal edildiğinde herhangi bir hesabın oluşturulmaması
    Given kullanıcı formu doldurmuştur
    When İptal butonuna tıklanır
    Then hiçbir hesap oluşturulmaz

  Scenario: TC-EACRML-010-09a - Hesap Adı alanının herhangi bir üst karakter sınırı olmadan uzun metni kabul etmesi
    Given kullanıcı hesap oluşturma formundadır
    When Hesap Adı alanına 2000 karakterlik bir metin girilir
    Then alan girilen metnin tamamını kabul eder

  Scenario: TC-EACRML-010-09b - Hesap Adı alanının tanımlı bir üst karakter sınırını aşan girişi reddetmesi
    Given kullanıcı hesap oluşturma formundadır
    When Hesap Adı alanına 2000 karakterlik bir metin girilir
    Then alan tanımlı karakter sınırını aşan girişi kabul etmez

  Scenario: TC-EACRML-010-10a - Fatura hesapları tablosunun tanımlı sütunlarla (Hesap Adı, Hesap Numarası, Hesap Tipi, Durum) gösterilmesi
    Given müşteriye ait en az bir fatura hesabı vardır
    When Müşteri Hesabı sekmesi görüntülenir
    Then tablo Hesap Adı, Hesap Numarası, Hesap Tipi ve Durum bilgilerini içeren sütunlarla gösterilir

  Scenario: TC-EACRML-010-10b - Hesap sayısı sayfa başına limiti aştığında sayfalama kontrollerinin doğru çalışması
    Given müşteriye ait sayfa başına limiti aşan sayıda fatura hesabı vardır
    When Müşteri Hesabı sekmesi görüntülenir
    Then sayfalama kontrolleri görüntülenir ve doğru çalışır

  Scenario: TC-EACRML-010-10c - Hiç fatura hesabı yokken tablonun görüntülenmemesi
    Given müşterinin hiç kayıtlı fatura hesabı yoktur
    When Müşteri Hesabı sekmesi görüntülenir
    Then hesap tablosu görüntülenmez
```

## Notlar

- Hesap formundaki adres alt-bileşeni ("Yeni Adres Ekle") `address_update.md`/`address_add.md` ile **aynı paylaşılan bileşen**dir (Şehir/Sokak/Bina No/Açıklama) — adres sınır değer kontrolleri orada tek seferde kapsandığından burada tekrar edilmedi.
- Bu UC dokümana göre tam kapsanmış durumda; kullanıcının istediği 3 yeni sınır-değer kategorisinden (demografik/adres/iletişim) hiçbiri bu UC'ye özgü yeni bir alan getirmiyor.
