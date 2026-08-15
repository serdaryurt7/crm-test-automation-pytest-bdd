# UC-EACRML-004 — Müşteri Bilgilerini Güncelleme — Konsolide Final Test Seti

> **Kapsam notu:** Bu UC, orijinal UC-EACRML-005–017 doküman karşılaştırmasının dışında (önceki bir turda ayrıca analiz edilmişti). Bu dosya, kullanıcının bu turda açıkça istediği **"demografik bilgi için sınır değer kontrolleri"** maddesini karşılamak amacıyla ekleniyor — demografik alanların (Ad/Soyad/Kimlik No) DÜZENLENDİĞİ tek ekran burası. Second/Father/Mother Name ve Birth Date yalnızca müşteri OLUŞTURULURKEN girilebiliyor (bu ekranda düzenlenemiyor) — onların sınır değerleri için bkz. `create_customer.md`.

## Durum Özeti

- Kaynak: `features/update_customer.feature`'daki 8 canlı doğrulanmış senaryo.
- **[İMPLEMENTE EDİLDİ] "Demografik bilgi için sınır değer kontrolleri":** Mevcut TC-004-07 yalnızca ÜST sınırın AŞILMASINI (51 karakter → 50'de kesilir) test ediyordu; TAM sınır değerin (50 karakter) sorunsuz kabul edildiğini doğrulayan eşleşen senaryo eksikti (TC-004-09) - eklendi. Ayrıca Nationality ID/Kimlik No alanı için hiç sınır-değer testi yoktu — `identityNumber` input'unun `maxlength=11` olduğu VE gerçek bir "tam 11 hane olmalı" doğrulama mesajının var olduğu (TR: "Kimlik numarası 11 haneli olmalı...", EN: "The identity number must be exactly 11 digits." - TC-017-06 keşfinde bulunmuştu) canlı olarak teyit edildi; tam bir sınır-değer üçlüsü (10 hane geçersiz / 11 hane geçerli / 12. hane input-seviyesinde engellenir) TC-004-10/11/12 ile eklendi. **Dilden bağımsız implementasyon:** hata mesajı, TR/EN'de ORTAK olan "11" rakamı doğrulanarak kontrol ediliyor, literal metin karşılaştırılmıyor (`search_customers.feature`'daki AYNI desen).
- **Doğrulama:** `pytest steps/test_update_customer_steps.py -v` ile izole çalıştırıldı — **5/5 PASSED** (Outline'ın 2 örneği + Nationality ID üçlüsü).

## Gherkin — Final Senaryo Seti

```gherkin
Feature: Müşteri Bilgilerini Güncelleme
  Müşteri Bilgisi ekranında demografik bilgilerin düzenlenip kaydedilmesi

  Background:
    Given kullanıcı bir müşterinin Müşteri Bilgisi ekranındadır

  Scenario: TC-EACRML-004-01 - Müşteri Bilgisi Ekranında Edit ile Demografik Bilgilerin Güncellenip Kaydedilmesi
    When kullanıcı Edit ikonuna tıklar
    Then form mevcut bilgilerle önceden dolu açılır
    When kullanıcı Ad alanını değiştirip Kaydet'e tıklar
    Then ekrandaki müşteri adı yeni değeri yansıtır
    And güncelleme sayfa yenilense dahi kalıcı olarak korunur

  Scenario Outline: TC-EACRML-004-02 - Edit Formunda Zorunlu Alan (Ad/Soyad) Boşaltıldığında Kaydet Butonunun Pasif Kalması
    Given kullanıcı düzenleme formundadır
    When "<alan>" alanı boşaltılır
    Then Kaydet butonu pasif kalır

    Examples:
      | alan  |
      | Ad    |
      | Soyad |

  Scenario: TC-EACRML-004-03 - Nationality ID Başka Bir Müşteriye Ait Olduğunda Anlık Doğrulama Hatası Gösterilip Kaydet Butonunun Pasif Kalması
    Given kullanıcı düzenleme formundadır
    When Nationality ID, başka bir müşteriye zaten kayıtlı bir değerle değiştirilir
    Then Nationality ID alanında bir doğrulama hatası anlık olarak görüntülenir
    And Kaydet butonu pasif kalır

  Scenario: TC-EACRML-004-03b - Mevcut Nationality ID Değiştirilmeden Kaydetmenin Hata Tetiklememesi
    Given kullanıcı düzenleme formundadır
    When kullanıcı Nationality ID alanını değiştirmeden Kaydet'e tıklar
    Then "already exist" hatası tetiklenmez, güncelleme normal şekilde tamamlanır

  Scenario: TC-EACRML-004-04 - Edit Formunda İptal Butonuna Tıklanınca Değişikliklerin Kaydedilmeden Görüntüleme Moduna Dönülmesi
    Given kullanıcı düzenleme formundadır
    When kullanıcı Ad alanını değiştirip İptal butonuna tıklar
    Then form kapanır, görüntüleme moduna dönülür
    And ekran güncelleme öncesi orijinal değerleri gösterir

  Scenario: TC-EACRML-004-05 - Customer Info Ekranının Salt Okunur Görüntülenmesi ve Edit/Delete İkonlarının Bulunması
    Then tüm alanlar salt okunur olarak gösterilir, düzenlenemez
    And başlığın yanında Edit ve Delete ikonları görüntülenir

  Scenario: TC-EACRML-004-06 - Edit Formu Açıldığında Alanların Mevcut Kayıtlı Değerlerle Önceden Doldurulmuş Olması
    When kullanıcı Edit ikonuna tıklar
    Then form mevcut bilgilerle önceden dolu açılır

  Scenario Outline: TC-EACRML-004-07 - Edit Formunda Ad/Soyad Alanlarının 50 Karakter Sınırının Korunması (Üst Sınır Aşımı)
    Given kullanıcı düzenleme formundadır
    When "<alan>" alanına 51 karakterlik değer girilmeye çalışılır
    Then alan en fazla 50 karakteri kabul eder

    Examples:
      | alan  |
      | Ad    |
      | Soyad |

  Scenario Outline: TC-EACRML-004-09 - Ad/Soyad Alanlarının Tam 50 Karakterlik Değeri Sorunsuz Kabul Etmesi
    Given kullanıcı düzenleme formundadır
    When "<alan>" alanına tam 50 karakterlik bir değer girilir
    Then alan girilen 50 karakterin tamamını kabul eder

    Examples:
      | alan  |
      | Ad    |
      | Soyad |

  Scenario: TC-EACRML-004-08 - Edit Formunda Ad Alanına Script Etiketi Girilmeye Çalışıldığında Zararlı Karakterlerin Alana Hiç Yazılamaması
    Given kullanıcı düzenleme formundadır
    When Ad alanına "<script>alert(1)</script>" girilmeye çalışılıp kaydedilir
    Then sistem yalnızca izin verilen karakterleri kabul eder, zararlı karakterler alana hiç yazılamaz
    And herhangi bir script çalıştırılmaz

  # NOT (canlı doğrulandı, TC-017-06 keşfinden): identityNumber-error
  # mesajı dile göre TR'de "Kimlik numarası 11 haneli olmalı..." / EN'de
  # "The identity number must be exactly 11 digits." oluyor - literal metin
  # yerine ikisinde de ORTAK olan "11" rakamı doğrulanarak dilden bağımsız
  # hale getirildi.
  Scenario: TC-EACRML-004-10 - Nationality ID Alanına 10 Haneli (Bir Eksik) Değer Girildiğinde Doğrulama Hatasının Gösterilmesi
    Given kullanıcı düzenleme formundadır
    When Nationality ID alanı 10 haneli bir değerle değiştirilir
    Then alanda 11 hane şartına dair bir doğrulama hatası görüntülenir
    And Kaydet butonu pasif kalır

  Scenario: TC-EACRML-004-11 - Nationality ID Alanına Tam 11 Haneli Geçerli Bir Değer Girildiğinde Doğrulamanın Başarıyla Geçmesi
    Given kullanıcı düzenleme formundadır
    When Nationality ID alanı, başka hiçbir müşteriye ait olmayan tam 11 haneli geçerli bir değerle değiştirilir
    Then herhangi bir doğrulama hatası gösterilmez, Kaydet butonu aktif hale gelir

  Scenario: TC-EACRML-004-12 - Nationality ID Alanına 11 Haneden Fazla Rakam Girilmeye Çalışıldığında Fazla Hanelerin Kabul Edilmemesi
    Given kullanıcı düzenleme formundadır
    When Nationality ID alanına 12 haneli bir değer girilmeye çalışılır
    Then alan yalnızca ilk 11 haneyi kabul eder, 12. hane yazılamaz
```

## Notlar

- `firstName`/`lastName` → `maxlength=50` (canlı doğrulandı, gerçek/uygulanan bir sınır — Açıklama/Hesap Adı/Sokak/Bina No'nun aksine burada sınır GERÇEKTEN var). `identityNumber` → `maxlength=11`.
- Birth Date (`maxlength=10`, gg/aa/yyyy maskeli metin) ve Gender bu ekranda locator seviyesinde mevcut ama proje kararıyla "düzenlenebilir zorunlu alan" setine dahil edilmemiş (`REQUIRED_FIELD_LOCATORS` yalnızca Ad/Soyad içeriyor) — bu ekrandan bağımsız olarak Birth Date'in biçim sınırları `create_customer.md`'de ele alınıyor.
