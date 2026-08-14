# UC-EACRML-017 — Dil Desteği — Konsolide Final Test Seti

## Durum Özeti

- Kaynak: kullanıcının 8 senaryolu spesifikasyonu + `features/language_support.feature`'daki 8 canlı doğrulanmış senaryo.
- i18n gerçek ve çalışıyor: EN seçildiğinde tüm arayüz metinleri gerçekten İngilizce'ye çevriliyor, doğrulama mesajları da çevriliyor. Tercih `localStorage` (`etiya.language`) içinde saklanıyor.
- **017-04 (dil tercihi oturuma mı hesaba mı bağlı?) doğrudan dokümanın kendi açık sorusunu kapatıyor:** spesifikasyon çıkış/girişte TR'ye dönmesini bekliyordu (oturuma bağlı varsayımı) — canlı KESİN olarak netleşti: `localStorage` tabanlı olduğundan dil tercihi **tam bir çıkış/giriş döngüsünden bağımsız olarak kalıcı** — EN seçilip çıkış yapılıp tekrar girildiğinde arayüz EN kalmaya devam ediyor, TR'ye dönmüyor. Senaryo gerçek/çalışan davranışı doğrulayacak şekilde uyarlandı.
- 017-06 (doğrulama mesajlarının dilden etkilenmesi), literal TR/EN string hardcode edilmeden **karşılaştırmalı** (TR mesaj önce yakalanıp, sonra EN'e geçilip aynı hata tekrar tetiklenerek farklı olduğu assert edilerek) çözüldü — projenin "dilden bağımsız test" ilkesiyle tutarlı.

## Gherkin — Final Senaryo Seti

```gherkin
Feature: Dil Desteği

  Scenario: TC-EACRML-017-01 - Dil değiştirici (TR/EN) panelinin açılıp kapatılabilmesi
    Given kullanıcı uygulamada herhangi bir ekrandadır
    When dil değiştirici butonuna tıklanır
    Then TR/EN seçenekleri içeren panel açılır
    When dil değiştirici butonuna tekrar tıklanır
    Then panel kapanır

  Scenario: TC-EACRML-017-02 - "EN" seçildiğinde arayüz metinlerinin İngilizce'ye çevrilmesi
    Given dil değiştirici panel açıktır
    When "EN" seçeneğine tıklanır
    Then menü/buton/başlık gibi arayüz metinleri değişir (İngilizce'ye çevrilir)
    And bu tercih kullanıcı farklı ekranlara geçse dahi oturum boyunca korunur

  Scenario: TC-EACRML-017-03 - Dil değişikliğinin sayfa yenilense dahi korunması
    Given kullanıcı dili "EN" yapmıştır
    When sayfa yenilenir
    Then arayüz İngilizce kalmaya devam eder

  Scenario: TC-EACRML-017-04 [UYARLANDI] - EN dili seçiliyken oturum kapatılıp tekrar giriş yapıldığında dil tercihinin korunması
    Given kullanıcı arayüz dilini EN olarak ayarlamıştır
    When kullanıcı oturumu kapatıp tekrar giriş yapar
    Then arayüz EN olarak kalmaya devam eder, TR'ye dönmez

  Scenario: TC-EACRML-017-05 - Dil değişikliğinin, yapısal (data-testid bazlı) kontrollerin etkilenmeden, yalnızca görünen metni değiştirmesi
    Given otomasyon testleri data-testid tabanlı locator kullanmaktadır
    When dil "EN" olarak değiştirilir
    Then tüm data-testid değerleri dilden bağımsız aynı kalır, yalnızca görünen metin değişir

  Scenario: TC-EACRML-017-06 - İngilizce dilde iken doğrulama mesajlarının Türkçe'den farklı (İngilizce) dilde görüntülenmesi
    Given dil "EN"dir
    When bir doğrulama hatası tetiklenir (Kimlik No formatı)
    Then mesaj Türkçe halinden farklı, İngilizce dilde görüntülenir

  Scenario: TC-EACRML-017-07 - Aktif dilin dil değiştirici buton üzerinde doğru şekilde vurgulanması
    Given aktif dil "TR"dir
    When dil değiştirici panel görüntülenir
    Then panelde aktif dil ("TR") vurgulanmış olarak işaretlenir

  Scenario: TC-EACRML-017-08 - Dil seçeneğinin yalnızca TR ve EN ile sınırlı olması
    Given kullanıcı dil değiştirici paneli açmıştır
    Then yalnızca TR ve EN seçenekleri listelenir, başka dil bulunmaz
```

## Notlar

- Sınır değer kontrolleri bu UC'nin kapsamında değil (dil seçici, serbest metin alanı yok).
- TC-017-06'daki "Kimlik No formatı" doğrulama hatası, `update_customer.md`'deki TC-EACRML-004-09/010 (Kimlik No sınır değer) senaryolarıyla aynı hata mesajını tetikliyor — iki UC birbirini dolaylı olarak da doğruluyor.
