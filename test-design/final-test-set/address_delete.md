# UC-EACRML-008 — Müşteri Adresinin Silinmesi — Konsolide Final Test Seti

## Durum Özeti

- Kaynak: `features/address_delete.feature`'daki 6 canlı doğrulanmış senaryo.
- Dokümanın iki kritik çelişkisi (008-01 hard-delete varsayımı, 008-03 "tek adres silinebilir" varsayımı) önceki oturumda çözüldü: 008-01 artık implementasyon detayına değil gözlemlenebilir kalıcılığa referans veriyor, 008-03 doğru şekilde "tek adresken Delete pasif" olarak düzeltilmiş durumda (dokümanla uyumlu).
- 008-05 canlı olarak doğrulandı: bir adres aktif bir Fatura Hesabının hizmet adresi olsa dahi **herhangi bir engelleme olmadan serbestçe siliniyor** — bu, potansiyel bir veri bütünlüğü açığı olarak ayrıca BA/dev'e bildirilmesi gereken bir bulgu (test kasıtlı kırmızı değil, gerçek/gözlemlenen davranışı doğruluyor).
- **Bu turda yapılan tek değişiklik:** TC-EACRML-008-04'ün Then ifadesi, artık kesinleşmiş canlı bulguyu yansıtacak şekilde açık uçlu ("doğrulanır") ifadeden kesin ifadeye güncellendi — `pages/address_delete_page.py`'deki `is_remaining_address_auto_primary()` zaten bu kesin sonucu (kalan tek adresin otomatik Primary olması) assert ediyor, sadece Gherkin metni bunu yansıtmıyordu.

## Gherkin — Final Senaryo Seti

```gherkin
Feature: Müşteri Adresinin Silinmesi

  Scenario: TC-EACRML-008-01 - Adres kartı menüsünden Delete seçeneğiyle kayıtlı bir adresin silinmesi
    Given kullanıcı, birden fazla adresi olan bir müşterinin adres kartını görüntülemektedir
    When kullanıcı kart menüsünden "Sil"i seçer
    Then sistem adresi kalıcı olarak siler (sayfa yenilense dahi adres listede görünmez)

  Scenario: TC-EACRML-008-02 - Silinen adres kartının ekrandaki listeden onay penceresi olmadan anında kaldırılması
    Given kullanıcı "Sil" seçeneğine tıklamıştır
    Then herhangi bir onay penceresi GÖRÜNTÜLENMEZ
    And kart listeden anında kaldırılır

  Scenario: TC-EACRML-008-03 - Müşterinin tek adresi varken Delete seçeneğinin pasif (disabled) görüntülenmesi
    Given müşterinin yalnızca 1 kayıtlı adresi vardır
    When kullanıcı adres kartı menüsünü açar
    Then Delete seçeneği pasif (disabled) olarak görüntülenir
    And tıklansa dahi adres silinemez

  Scenario: TC-EACRML-008-04 [GÜNCELLENDİ] - Primary adres silindiğinde kalan tek adresin otomatik olarak Primary'e dönüşmesi
    Given müşterinin birden fazla adresi ve Primary işaretli biri vardır
    When Primary adres silinir
    Then kalan tek adres otomatik olarak Primary olarak işaretlenir

  Scenario: TC-EACRML-008-06 - Adres silme isteğinin tekrarlanmasının güvenli şekilde reddedilmesi
    Given bir adres silinmiştir
    When kullanıcı aynı adresi (artık silinmiş, stale bir referansla) tekrar silmeyi dener
    Then sistem ikinci denemeyi güvenli şekilde reddeder, uygulama tutarlı durumda kalır

  Scenario: TC-EACRML-008-05 - Fatura hesabının hizmet adresi olarak kullanılan bir adresin silinmeye çalışılması durumunun doğrulanması
    Given bir adres, aktif bir Fatura Hesabının hizmet adresi olarak kullanılmaktadır
    When kullanıcı bu adresi silmeyi dener
    Then sistemin gerçek davranışı doğrulanır: adres herhangi bir engelleme veya uyarı olmadan serbestçe silinir
```

## Notlar

- **Veri bütünlüğü bulgusu (TC-008-05):** Fatura hesabı → hizmet adresi ilişkisi, adres silinirken hiçbir şekilde korunmuyor. Hesap artık var olmayan bir adrese referans veriyor olabilir — BA/PO'ya ayrıca bildirilmesi önerilen bir bulgu, otomasyon kapsamında değil.
- Adres alanları için sınır değer kontrolleri bu UC'nin kapsamında değil (silme akışı, alan girişi yok) — bkz. `address_update.md`.
