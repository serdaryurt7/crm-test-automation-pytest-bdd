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

  Scenario: (Var olmayan kullanıcı için) GSM Alanının Geçerli Değer Girilse Dahi Arama Sonuçlarını Filtrelememesi
    When kullanıcı GSM alanına "5551234567" değerini girer
    Then GSM alanında "5551234567" değeri görüntülenir
    And Search butonu aktif hale gelir
    When kullanıcı Search butonuna tıklar
    Then "Arama kriterlerine uygun müşteri bulunamadı." mesajı görüntülenir

  Scenario: First Name ve Last Name Alanlarının 50 Karakter Sınırı
    When kullanıcı First Name ve Last Name alanlarına 60 karakterden uzun değerler girer
    Then First Name ve Last Name alanları en fazla 50 karakter kabul eder

  Scenario: Last Name Alanında Baş/Son Boşlukların Otomatik Temizlenmesi (Auto-Trim)
    When kullanıcı Last Name alanına "  Yılmaz  " değerini girer
    And kullanıcı Search butonuna tıklar
    Then "Yılmaz" soyadına sahip müşteri kayıtları sonuç listesinde görüntülenir

  Scenario Outline: Last Name Aramasının Büyük/Küçük Harf Duyarsız Olması
    When kullanıcı Last Name alanına "<last_name>" değerini girer
    And kullanıcı Search butonuna tıklar
    Then "Yılmaz" soyadına sahip müşteri kayıtları sonuç listesinde görüntülenir

    Examples:
      | last_name |
      | YILMAZ    |
      | yılmaz    |
      | YİLMAZ    |

  Scenario: First Name Alanında Baş/Son Boşlukların Otomatik Temizlenmesi (Auto-Trim)
    When kullanıcı First Name alanına "  İbrahim  " değerini girer
    And kullanıcı Search butonuna tıklar
    Then "İbrahim" adına sahip müşteri kayıtları sonuç listesinde görüntülenir

  Scenario Outline: First Name Aramasının Büyük/Küçük Harf Duyarsız Olması
    When kullanıcı First Name alanına "<first_name>" değerini girer
    And kullanıcı Search butonuna tıklar
    Then "İbrahim" adına sahip müşteri kayıtları sonuç listesinde görüntülenir

    Examples:
      | first_name |
      | IBRAHIM    |
      | ibrahim    |
      | İBRAHİM    |

  Scenario: Last Name Aramasının Baştan Eşleşme (Starts-With) ile Çalışması
    When kullanıcı Last Name alanına "Kar" değerini girer
    And kullanıcı Search butonuna tıklar
    Then "Kar" ile başlayan soyadına sahip müşteri kayıtları sonuç listesinde görüntülenir
    When kullanıcı Last Name alanına "ılmaz" değerini girer
    And kullanıcı Search butonuna tıklar
    Then "Arama kriterlerine uygun müşteri bulunamadı." mesajı görüntülenir

  Scenario: First Name Aramasının Baştan Eşleşme (Starts-With) ile Çalışması
    When kullanıcı First Name alanına "Em" değerini girer
    And kullanıcı Search butonuna tıklar
    Then "Em" ile başlayan adına sahip müşteri kayıtları sonuç listesinde görüntülenir
    When kullanıcı First Name alanına "mine" değerini girer
    And kullanıcı Search butonuna tıklar
    Then "Arama kriterlerine uygun müşteri bulunamadı." mesajı görüntülenir

  Scenario: First Name ve Last Name Birlikte Girildiğinde AND Mantığıyla Değerlendirilmesi
    When kullanıcı First Name alanına "Ahmet" ve Last Name alanına "Yılmaz" değerlerini girer
    And kullanıcı Search butonuna tıklar
    Then yalnızca hem "Ahmet" hem "Yılmaz" kriterine uyan müşteriler sonuç listesinde görüntülenir

  Scenario: İsim Kriteri ile Diğer Arama Kriterlerinin OR Mantığıyla Değerlendirilmesi
    When kullanıcı First Name alanına "İbrahim" ve Customer ID alanına "1" değerlerini girer
    And kullanıcı Search butonuna tıklar
    Then "İbrahim" ismine VEYA "1" Customer ID'sine uyan tüm müşteriler sonuç listesinde görüntülenir

  Scenario: 15 Kaydı Aşan Sonuç Kümesinde İlk Sayfada 15 Kayıt ve Sayfalama
    Then ilk sayfada tam 15 kayıt gösterilir ve sayfalama kontrolleri aktiftir
    When kullanıcı sayfalama kontrolleriyle diğer sayfalara geçer
    Then her sayfada doğru sayıda kayıt gösterilir; hiçbir kayıt kaybolmaz veya tekrarlanmaz

  Scenario: Sonuç Listesinin Varsayılan Olarak Customer ID'ye Göre Artan Sıralanması
    Then sonuç listesi varsayılan olarak Customer ID'ye göre artan sırada listelenir

  Scenario: "No Customer Found" Mesajının ve Create Customer Butonunun Görüntülenmesi
    When kullanıcı ID Number alanına "00000000000" değerini girer
    And kullanıcı Search butonuna tıklar
    Then sonuç bulunamadı durumu görüntülenir
    And Müşteri Oluştur butonu görüntülenir
    When kullanıcı Müşteri Oluştur butonuna tıklar
    Then kullanıcı müşteri oluşturma sayfasına yönlendirilir

  Scenario: Customer ID Linkiyle Customer Info Ekranına Aynı Sekmede Geçiş
    When kullanıcı Customer ID alanına "1" değerini girer
    And kullanıcı Search butonuna tıklar
    And kullanıcı sonuç listesindeki Customer ID linkine tıklar
    Then kullanıcı aynı sekmede "1" numaralı müşterinin Customer Info ekranına yönlendirilir

  Scenario: Clear Butonuyla Tüm Filtrelerin ve Sonuçların Sıfırlanması
    When kullanıcı tüm arama alanlarına Tab ile sırayla değer girer
    And kullanıcı Search butonuna tıklar
    And kullanıcı Clear butonuna tıklar
    Then tüm arama alanları boşalır ve sonuç listesi varsayılan hale döner

