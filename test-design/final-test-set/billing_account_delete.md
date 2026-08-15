# UC-EACRML-012 — Fatura Hesabını Silme — Konsolide Final Test Seti

## Durum Özeti

- Kaynak: `features/billing_account_delete.feature`'daki 6 canlı doğrulanmış senaryo. TC-012-03'ün önkoşulu ("hesaba bağlı aktif ürün") UC-014/015/016'nın tam satış akışını gerektirdiğinden başlangıçta ayrıca ele alınmış, sonradan uçtan uca tamamlanmış.
- **012-04 (tek hesap silinebiliyor mu?)** açık sorusu kapandı: canlı doğrulandı, müşterinin **tek** fatura hesabı da (UC-008'deki adresin aksine) engelsiz silinebiliyor, "Hesap bulunmuyor" boş durumuna dönülüyor.
- **Bilinen tutarsızlık (`bugsbunny.txt` kategori 1):** TC-012-03 (aktif ürünü olan hesap silinemez) — page object tamamlandıktan sonra tutarlı şekilde FAILED veriyor (hesap engellenmeden siliniyor), ama daha önce 2 ayrı ham script ile doğru/beklenen (engellendi) davranış da gözlemlenmişti. **Bu turda UC-005-03'te (müşteri silme, bkz. `delete_customer.md`) AYNI kural canlı olarak tekrar test edildi ve yine engellenmediği doğrulandı** — bu, tek seferlik bir flake olmaktan çok, "aktif ürünü olan varlık silinemez" iş kuralının uygulamada (müşteri VE fatura hesabı seviyesinde) tutarlı biçimde EKSİK olduğuna işaret ediyor. Sistemik bir defekt olarak BA/dev'e birlikte raporlanması önerilir.

## Gherkin — Final Senaryo Seti

```gherkin
Feature: Fatura Hesabını Silme

  Scenario: TC-EACRML-012-01 - Hesap satırındaki Delete seçeneğiyle fatura hesabının silinmesi
    Given kullanıcı, aktif ürünü olmayan bir hesap satırı görüntülemektedir
    When Delete butonuna tıklanır ve onay penceresinde onaylanırsa
    Then hesap aktif hesap listesinden kalıcı olarak kaldırılır

  Scenario: TC-EACRML-012-02 - Silme onay penceresinde "Hayır" butonuna tıklandığında işlemin iptal edilmesi
    Given silme onay penceresi görüntülenmektedir
    When kullanıcı "Hayır" butonuna tıklar
    Then herhangi bir değişiklik yapılmaz, onay penceresi kapanır
    And kullanıcı Müşteri Hesabı ekranında kalır

  Scenario: TC-EACRML-012-03 [DEFEKT ADAYI - Sistemik] - Aktif ürün/aboneliği bulunan bir fatura hesabının silinmeye çalışılması durumunda sistemin uyarı vermesi
    # KASITLI KIRMIZI: bkz. Durum Özeti - UC-005-03 ile aynı sistemik kural
    # eksikliği. Spesifikasyonun doğru davranışını assert ediyor.
    Given hesaba bağlı en az bir aktif ürün vardır
    When kullanıcı hesabı silmeyi dener
    Then hesap listeden kaldırılmaz
    And sistem doğrudan silmek yerine bir uyarı/engelleme mesajı gösterir

  Scenario: TC-EACRML-012-04 - Silinen hesabın aktif hesap listesinden kaldırılması
    Given bir fatura hesabı silinmiştir
    When Müşteri Hesabı sekmesindeki hesap listesi görüntülenir
    Then silinen hesap artık bu listede görüntülenmez

  Scenario: TC-EACRML-012-05 - Müşterinin tek fatura hesabı silindiğinde "Hesap bulunmuyor" boş durumuna dönülmesi
    Given müşterinin yalnızca 1 hesabı vardır
    When bu hesap silinir
    Then "Hesap bulunmuyor" boş durumuna dönülür

  Scenario: TC-EACRML-012-06 - Silme isteğinin tekrarlanmasının güvenli şekilde reddedilmesi
    Given bir hesap silinmiştir
    When kullanıcı aynı hesabı (artık silinmiş, stale bir referansla) tekrar silmeyi dener
    Then sistem ikinci denemeyi güvenli şekilde reddeder, uygulama tutarlı durumda kalır
```

## Notlar

- TC-012-03, UC-008'deki (adres silme, tek adres) "son kaydın korunması" kalıbından FARKLI: burada hesap SAYISI değil hesabın İÇERİĞİ (aktif ürün varlığı) engelleyici olmalıydı — iki kural birbirine karıştırılmamalı.
- Sınır değer kontrolleri bu UC'nin kapsamında değil (silme akışı, alan girişi yok).
