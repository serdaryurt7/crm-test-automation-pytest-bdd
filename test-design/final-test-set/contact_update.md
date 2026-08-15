# UC-EACRML-009 — Kontakt Bilgilerinin Güncellenmesi — Konsolide Final Test Seti

## Durum Özeti

- Kaynak: `features/contact_update.feature`'daki 10 canlı doğrulanmış senaryo (email benzersizliği — 009-09 — dahil, client-side/anlık doğrulama olarak zaten teyitli).
- **Bu turda YENİ eklenen (kullanıcının istediği "iletişim bilgileri için sınır değer kontrolleri"):** Mobile Phone alanı için mevcut TC-EACRML-009-04 (8 haneli, bilinen bug) bir sınır-değer testi DEĞİL, spesifik bir defekt-regresyon testidir — gerçek sınır çifti (9 hane = geçersiz / 10 hane = geçerli) ile 10 hanelik input-seviyesi üst sınır kapağı ayrıca test edilmemişti. Bu boşluk TC-009-11/12/13 ile kapatıldı. Ayrıca Email (maxlength yok) ve Home Phone/Fax (maxlength=10, aynı maskeleme) için de yeni sınır senaryoları eklendi.
- **Canlı doğrulanan DOM sınırları:** `customer-contact-mobile-phone` → `maxlength=10` (appdigitsonly); `customer-contact-email` → `maxlength` yok (create sihirbazındaki `new-contact-email` alanında doğrulandı — Contact Update sekmesindeki alan aynı bileşen/validator setini paylaştığından aynı davranış bekleniyor, ayrıca teyit önerilir, bkz. Notlar); `customer-contact-home-phone` / `customer-contact-fax` → `maxlength=10`.

## Gherkin — Final Senaryo Seti

```gherkin
Feature: Kontakt Bilgilerinin Güncellenmesi

  Scenario: TC-EACRML-009-01 - İletişim Kanalı sekmesinde Edit ile Email/Telefon bilgilerinin güncellenip kaydedilmesi
    Given kullanıcı bir müşterinin İletişim Kanalı sekmesindedir
    When Edit ile Email/Mobile Phone alanları güncellenip Kaydet'e tıklanır
    Then güncelleme kaydedilir ve görüntüleme modunda yeni bilgiler yansır

  Scenario: TC-EACRML-009-02 - Geçersiz formatta email girildiğinde uyarı gösterilmesi
    Given kullanıcı düzenleme formundadır
    When Email alanına geçersiz formatta bir değer girilir
    Then geçersiz format hatası gösterilir ve güncelleme gerçekleştirilmez

  Scenario Outline: TC-EACRML-009-03 - Email veya Mobile Phone zorunlu alanı boş bırakıldığında güncellemenin engellenmesi
    Given kullanıcı düzenleme formundadır
    When "<alan>" alanı boşaltılır
    Then ilgili alan hatalı olarak işaretlenir
    And güncelleme gerçekleştirilmez

    Examples:
      | alan          |
      | Email         |
      | Mobile Phone  |

  Scenario: TC-EACRML-009-04 [DEFEKT ADAYI] - Mobile Phone alanına tam 8 haneli geçersiz değer girildiğinde doğrulamanın çalışması
    # Bilinen bug (UC-003-14 ile aynı kök neden): SADECE 8 hanede doğrulama
    # atlanıyor (1/2/6/7/9 hane doğru reddediliyor). Sınır-değer testi DEĞİL,
    # spesifik bir regresyon guard'ı - gerçek BVA çifti için bkz. 009-11/12.
    Given kullanıcı düzenleme formundadır
    When Mobile Phone alanına "05551234" (8 haneli) girilir
    Then hata gösterilir ve Kaydet butonu pasif kalır

  Scenario: TC-EACRML-009-05 - Contact Medium sekmesinin açılması ve iletişim bilgilerinin salt okunur görüntülenmesi
    Given müşterinin kayıtlı iletişim bilgileri mevcuttur
    When kullanıcı İletişim Kanalı sekmesini açar
    Then iletişim bilgileri salt okunur (read-only) görüntülenir
    And başlığın yanında Edit ikonu bulunur

  Scenario: TC-EACRML-009-06 - Edit ikonuyla iletişim bilgileri düzenleme formunun açılması
    Given "İletişim Kanalı" sekmesi açıktır ve Edit ikonu görünmektedir
    When kullanıcı Edit ikonuna tıklar
    Then sistem iletişim bilgilerini düzenlemek için formu açar

  Scenario: TC-EACRML-009-07 - Home Phone ve Fax alanlarının opsiyonel olması ve boş bırakılabilmesi
    Given kullanıcı düzenleme formundadır
    When Home Phone ve Fax alanları boş bırakılıp yalnızca zorunlu alanlar doldurulur
    Then güncelleme başarıyla tamamlanır

  Scenario: TC-EACRML-009-08 - Edit formunda İptal edilince girilen değişikliklerin kaydedilmeden atılması
    Given kullanıcı formda değişiklik yapmıştır
    When İptal butonuna tıklanır
    Then değişiklikler kaydedilmez, önceki bilgiler korunur

  Scenario: TC-EACRML-009-09 - Aynı email adresinin başka bir müşteride zaten kayıtlı olması durumunda güncellemenin reddedilmesi
    Given müşterinin dışında (başka bir müşteride) zaten kayıtlı bir email vardır
    When kullanıcı bu emaili Email alanına girer
    Then sistem güncellemeyi reddeder, ilgili alan hatalı olarak işaretlenir

  Scenario: TC-EACRML-009-10 - Ülke kodu (+90) sabit alanının telefon numarasından bağımsız olarak değişmemesi
    Given kullanıcı düzenleme formundadır
    When telefon numarası değiştirilir
    Then Mobile/Home Phone/Fax alanlarının önünde sabit "+90" ülke kodu değişmeden görüntülenmeye devam eder

  Scenario: TC-EACRML-009-11 [YENİ - Sınır Değer] - Mobile Phone Alanına 9 Haneli (Bir Eksik) Değer Girildiğinde Doğrulama Hatasının Gösterilmesi
    Given kullanıcı düzenleme formundadır
    When Mobile Phone alanına 9 haneli geçerli formatta bir değer girilir
    Then hata gösterilir ve Kaydet butonu pasif kalır

  Scenario: TC-EACRML-009-12 [YENİ - Sınır Değer] - Mobile Phone Alanına Tam 10 Haneli Değer Girildiğinde Doğrulamanın Başarıyla Geçmesi
    Given kullanıcı düzenleme formundadır
    When Mobile Phone alanına tam 10 haneli geçerli bir değer girilir
    Then herhangi bir doğrulama hatası gösterilmez ve Kaydet butonu aktif hale gelir

  Scenario: TC-EACRML-009-13 [YENİ - Sınır Değer] - Mobile Phone Alanına 10 Haneden Fazla Rakam Girilmeye Çalışıldığında Fazla Hanelerin Kabul Edilmemesi
    Given kullanıcı düzenleme formundadır
    When Mobile Phone alanına 11 haneli bir değer girilmeye çalışılır
    Then alan yalnızca ilk 10 haneyi kabul eder, 11. hane yazılamaz

  Scenario: TC-EACRML-009-14 [YENİ - Sınır Değer] - Email Alanının Çok Uzun Bir Değeri HTML Seviyesinde Bir Üst Karakter Sınırı Olmadan Kabul Etmesi
    Given kullanıcı düzenleme formundadır
    When Email alanına formatça geçerli ama çok uzun (150+ karakter) bir değer girilir
    Then alan girilen değerin tamamını kabul eder, herhangi bir HTML seviyesi kısıtlama uygulanmaz

  Scenario: TC-EACRML-009-15 [YENİ - Sınır Değer] - Home Phone ve Fax Alanlarının (Girilirse) En Fazla 10 Hane Kabul Etmesi
    Given kullanıcı düzenleme formundadır
    When Home Phone alanına 11 haneli bir değer girilmeye çalışılır
    Then alan yalnızca ilk 10 haneyi kabul eder
    When Fax alanına 11 haneli bir değer girilmeye çalışılır
    Then alan yalnızca ilk 10 haneyi kabul eder
```

## Notlar

- **TC-009-14 için teyit notu:** Email'in `maxlength` içermediği bilgisi, canlı olarak Müşteri Oluşturma sihirbazının İletişim Kanalı adımındaki (`new-contact-email`) alanda doğrulandı. Contact Update sekmesindeki (`customer-contact-email`) alan aynı Angular bileşen/validator setini paylaşıyor olması muhtemel (proje genelinde bu desen — Mobile Phone'un 10 hane kuralı, +90 sabit öneki — hem create hem update ekranlarında birebir aynı çıkmıştı), ama bu spesifik alan bağımsız olarak yeniden doğrulanmadı; ilk otomasyona alımda bir kerelik teyit önerilir.
- Email formatındaki ".com ile bitmelidir" kısıtlaması (create sihirbazı testinde keşfedildi — `.org`/`.net` gibi geçerli ama `.com` olmayan bir TLD reddediliyor) bu ekranda ayrıca test edilmedi; gerçekten bir iş kuralı mı yoksa dar bir regex mi olduğu BA ile teyit edilip TC-009-16 olarak eklenmesi değerlendirilebilir.
