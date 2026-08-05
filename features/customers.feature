Feature: Müşteri Arama
  Kullanıcının müşteri kayıtlarını arayabilmesi

  Background:
    Given kullanıcı müşteri arama sayfasındadır

  Scenario: Arama Kriteri Girilmeden Ara Butonunun Pasif Kalması
    When kullanıcı arama kriteri girmez
    Then Ara butonu pasif kalır

  Scenario: Ekran Açıldığında B2C Segmentinin Varsayılan Seçili Gelmesi ve Filtre Formunun Görüntülenmesi
    Then sistem tüm arama alanlarını görüntüler
    And sistem Search ve Clear butonlarını görüntüler
    And B2C sekmesi aktif, B2B sekmesi pasif görüntülenir

  Scenario: B2B Sekmesinin Prototipte Pasif (Disabled) ve İşlevsiz Olması
    When kullanıcı B2B sekmesine tıklamayı dener
    Then B2C sekmesi aktif, B2B sekmesi pasif görüntülenir

  Scenario: Geçerli 11 Haneli ID Number ile Tam Eşleşen Müşterinin Bulunması
    When kullanıcı ID Number alanına "10000000146" değerini girer
    Then ID Number alanında "10000000146" değeri görüntülenir
    And Search butonu aktif hale gelir
    When kullanıcı Search butonuna tıklar
    Then girilen ID Number'a sahip müşteri kaydı sonuç tablosunda görüntülenir

  Scenario: ID Number Alanının Yalnızca Rakam Kabul Etmesi ve 11 Hane Sınırını Aşmaması
    When kullanıcı ID Number alanına "abc!@#123" değerini girmeyi dener
    Then ID Number alanında "123" değeri görüntülenir
    When kullanıcı ID Number alanına "123456789012345" değerini girmeyi dener
    Then ID Number alanı yalnızca ilk 11 haneyi kabul eder

  Scenario: ID Number Alanına 11 Haneden Az Rakam Girildiğinde Validasyon Hatası Gösterilmesi
    When kullanıcı ID Number alanına "1000000014" değerini girer
    Then ID Number alanında "1000000014" değeri görüntülenir
    When kullanıcı Search butonuna tıklar
    Then "Please enter a valid 11-digit ID number." mesajı görüntülenir

  Scenario: Customer ID Aramasının Tam Eşleşme (Exact Match) ile Çalışması
    When kullanıcı Customer ID alanına "5" değerini girer
    And kullanıcı Search butonuna tıklar
    Then yalnızca bu Customer ID'ye tam eşleşen tek müşteri kaydı sonuç listesinde görüntülenir

  Scenario: Customer ID Alanının Yalnızca Rakam Kabul Etmesi ve 20 Hane Sınırı
    When kullanıcı Customer ID alanına "abc!@#123" değerini girer
    Then Customer ID alanında "123" değeri görüntülenir
    When kullanıcı Customer ID alanına "123456789012345678901234" değerini girer
    Then Customer ID alanı 20 üzeri karakter alamaz

  Scenario: GSM Alanının Yalnızca Rakam Kabul Etmesi ve Ülkelere Göre Karakter Sınırı
    When kullanıcı GSM alanına "abc!@#123" değerini girer
    Then GSM alanında "123" değeri görüntülenir
    When kullanıcı GSM alanına "12345678901234" değerini girer
    Then GSM alanı en fazla 10 haneyi kabul eder
