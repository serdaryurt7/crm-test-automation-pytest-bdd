# UC-EACRML-011 — Fatura Hesabı Güncelleme — Konsolide Final Test Seti

## Durum Özeti

- Kaynak: `features/billing_account_update.feature`'daki 5 canlı doğrulanmış senaryo. Dokümanın 3 senaryosu da (011-01/02/03 karşılığı) karşılanmış, kritik çelişki yok.
- **TC-011-05 (Aktif/Pasif toggle butonu) bilinçli olarak dışarıda bırakıldı:** doküman böyle bağımsız bir toggle kontrolünün var olup olmadığını sormuştu (durum değişimi yalnızca UC-012'nin silme akışı üzerinden mi oluyor?) — canlı keşifle KESİN olarak netleşti: böyle bağımsız bir toggle **YOK**. Bu, açık sorular listesindeki 6. maddeyi kapatıyor.
- **Bilinen defekt (kasıtlı kırmızı, `bugsbunny.txt` kategori 1):** TC-EACRML-011-02 ve TC-EACRML-011-04 — hesap düzenleme formunda **hizmet adresi değişikliği kaydedilmiyor** (Hesap Adı değişikliği doğru kaydediliyor, adres değişikliği sessizce kayboluyor). İki senaryo da spesifikasyonun doğru/beklenen davranışını assert ediyor ve şu an FAILED vermesi beklenen durum — düzeltilirse otomatik PASS'e dönecek.

## Gherkin — Final Senaryo Seti

```gherkin
Feature: Fatura Hesabı Güncelleme

  Scenario: TC-EACRML-011-01 - Hesap satırındaki Edit seçeneğiyle "Fatura Hesabını Düzenle" formunun mevcut bilgilerle açılması
    Given kullanıcı Müşteri Hesabı sekmesinde bir hesap satırı görüntülemektedir
    When kullanıcı Edit butonuna tıklar
    Then "Fatura Hesabını Düzenle" formu mevcut Hesap Adı/Açıklaması/Adres bilgileriyle önceden dolu açılır

  Scenario: TC-EACRML-011-02 [DEFEKT ADAYI] - Hesap Adı ve Adres güncellenip kaydedildiğinde listedeki satırın yeni bilgilerle yenilenmesi
    # KASITLI KIRMIZI (canlı doğrulandı): Hesap Adı değişikliği kaydediliyor,
    # adres değişikliği SESSİZCE kayboluyor. bugsbunny.txt kategori 1.
    Given kullanıcı hesap düzenleme formundadır
    When Hesap Adı ve Adres alanları (geçerli değerlerle) güncellenip Kaydet'e tıklanır
    Then satır listede yeni bilgiyle yenilenir

  Scenario: TC-EACRML-011-03 - Güncelleme formunda Hesap Adı boşaltıldığında güncellemenin engellenmesi
    Given kullanıcı hesap düzenleme formundadır
    When Hesap Adı alanı boşaltılır
    Then ilgili alan hatalı olarak işaretlenir
    And güncelleme gerçekleştirilmez, kullanıcı düzenleme ekranında kalır

  Scenario: TC-EACRML-011-04 [DEFEKT ADAYI] - Hesabın bağlı olduğu hizmet adresinin güncelleme formunda değiştirilebilmesi
    # Aynı kök nedenin (adres kalıcılık bug'ı) ikinci tezahürü - kasıtlı kırmızı.
    Given kullanıcı hesap düzenleme formundadır
    When hizmet adresi müşterinin başka bir kayıtlı adresiyle değiştirilir
    Then kaydedildiğinde hesap yeni adresle ilişkilendirilir

  Scenario: TC-EACRML-011-06 - Güncelleme formunda İptal edilince hesap bilgilerinin değişmeden kalması
    Given kullanıcı formda değişiklik yapmıştır
    When İptal butonuna tıklanır
    Then hesap bilgileri değişmeden kalır
```

## Notlar

- Hesap Adı alanı bu formda `billing_account_create.md`'deki (TC-010-09a/b) ile **birebir aynı bileşen**dir (`BillingAccountUpdatePage`, `BillingAccountCreatePage`'den türetiliyor) — "üst karakter sınırı yok" bulgusu burada tekrar test edilmedi (DRY).
- TC-011-02/04'teki adres kalıcılık defekti düzeltildiğinde, aynı kök nedene bağlı olabilecek `billing_account_products.md` ve satış akışı senaryolarının da yeniden gözden geçirilmesi önerilir.
