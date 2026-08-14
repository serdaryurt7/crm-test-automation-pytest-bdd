Feature: Müşteri Bilgilerini Güncelleme
  Müşteri Bilgisi ekranında demografik bilgilerin düzenlenip kaydedilmesi

  Background:
    Given kullanıcı bir müşterinin Müşteri Bilgisi ekranındadır

  Scenario: Müşteri Bilgisi Ekranında Edit ile Demografik Bilgilerin Güncellenip Kaydedilmesi
    When kullanıcı Edit ikonuna tıklar
    Then form mevcut bilgilerle önceden dolu açılır
    When kullanıcı Ad alanını değiştirip Kaydet'e tıklar
    Then ekrandaki müşteri adı yeni değeri yansıtır
    And güncelleme sayfa yenilense dahi kalıcı olarak korunur

  Scenario Outline: Edit Formunda Zorunlu Alan (Ad/Soyad) Boşaltıldığında Kaydet Butonunun Pasif Kalması
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

  Scenario Outline: TC-EACRML-004-07 - Edit Formunda Ad/Soyad Alanlarının 50 Karakter Sınırının Korunması
    Given kullanıcı düzenleme formundadır
    When "<alan>" alanına 51 karakterlik değer girilmeye çalışılır
    Then alan en fazla 50 karakteri kabul eder

    Examples:
      | alan  |
      | Ad    |
      | Soyad |

  Scenario: TC-EACRML-004-08 - Edit Formunda Ad Alanına Script Etiketi Girilmeye Çalışıldığında Zararlı Karakterlerin Alana Hiç Yazılamaması
    Given kullanıcı düzenleme formundadır
    When Ad alanına "<script>alert(1)</script>" girilmeye çalışılıp kaydedilir
    Then sistem yalnızca izin verilen karakterleri kabul eder, zararlı karakterler alana hiç yazılamaz
    And herhangi bir script çalıştırılmaz

  Scenario Outline: TC-EACRML-004-09 - Ad/Soyad Alanlarının Tam 50 Karakterlik Değeri Sorunsuz Kabul Etmesi
    Given kullanıcı düzenleme formundadır
    When "<alan>" alanına tam 50 karakterlik bir değer girilir
    Then alan girilen 50 karakterin tamamını kabul eder

    Examples:
      | alan  |
      | Ad    |
      | Soyad |

  # NOT (canlı doğrulandı, TC-017-06 keşfinden): identityNumber-error
  # mesajı dile göre TR'de "Kimlik numarası 11 haneli olmalı..." / EN'de
  # "The identity number must be exactly 11 digits." oluyor - literal metin
  # yerine ikisinde de ORTAK olan "11" rakamı doğrulanarak dilden bağımsız
  # hale getirildi (search_customers.feature'daki AYNI desen).
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
