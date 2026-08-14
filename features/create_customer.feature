Feature: Müşteri Oluşturma
  Kullanıcının yeni müşteri kaydı oluşturabilmesi

  Background:
    Given kullanıcı müşteri oluşturma sayfasındadır

  Scenario Outline: Demografik, Adres ve İletişim Bilgileriyle Uçtan Uca Müşteri Yaratma
    When kullanıcı zorunlu Demografik Bilgi alanlarını Gender "<gender>" ile rastgele Faker değerlerle doldurur
    Then girilen değerler ilgili alanlarda görüntülenir
    When kullanıcı Demografik Bilgi adımında İleri butonuna tıklar
    Then sistem Nationality ID'nin kayıtlı olmadığını doğrular ve "Adres Bilgisi" ekranını açar
    And Adres adımında İleri butonu pasiftir
    When kullanıcı Adres alanlarını rastgele Faker değerlerle doldurup Save butonuna tıklar
    Then sistem adresi kart olarak listeler ve İleri butonu aktif hale gelir
    When kullanıcı Adres adımında İleri butonuna tıklar
    Then sistem "İletişim Kanalı" ekranını açar
    When kullanıcı İletişim Kanalı alanlarını rastgele Faker değerlerle doldurur
    Then Create butonu aktif hale gelir
    When kullanıcı Create butonuna tıklar
    Then sistem müşteri kaydını oluşturur ve "Customer Info" ekranını açar
    And müşterinin Cinsiyet bilgisi "<gender>" olarak görüntülenir

    Examples:
      | gender |
      | Kadın  |
      | Erkek  |

  Scenario: Demografik Bilgi Ekranında "Cancel" ile İşlemin İptal Edilmesi
    Given kullanıcı "Demografik Bilgi" ekranında bazı alanları doldurmuştur
    When kullanıcı "Cancel" butonuna tıklar
    Then sistem işlemi iptal eder ve kullanıcıyı müşteri listesi ekranına yönlendirir
    And girilen hiçbir bilgi sistemde kaydedilmez

  Scenario: Adres Bilgi Ekranında Birden Fazla Adres Ekleme
    Given kullanıcı "Adres Bilgi" ekranındadır
    When kullanıcı Adres alanlarını rastgele Faker değerlerle doldurup Save butonuna tıklar
    Then sistem adresi kart olarak listeler ve İleri butonu aktif hale gelir
    When kullanıcı Adres alanlarını rastgele Faker değerlerle doldurup Save butonuna tıklar
    Then her iki adres kartı da ayrı ayrı ve eksiksiz görüntülenir, İleri butonu aktif kalır

  Scenario: "Contact Medium" Ekranında "Previous" ile Adres Bilgi Ekranına Dönüş
    Given kullanıcı "Contact Medium" ekranında iletişim bilgilerini rastgele Faker değerlerle doldurmuştur
    When kullanıcı "Previous" butonuna tıklar
    Then sistem kullanıcıyı "Adres Bilgi" ekranına yönlendirir ve daha önce kaydedilmiş adres kartı eksiksiz görüntülenir
    When kullanıcı Adres adımında İleri butonuna tıklar
    Then sistem "İletişim Kanalı" ekranını açar
    And varsa önceden girilmiş iletişim bilgileri korunur

  Scenario: Demografik Bilgi Ekranında Zorunlu Alan Eksikken Next Butonunun Pasif Kalması
    When kullanıcı zorunlu alanlardan birini "Soyad" boş bırakır
    Then "Next" butonu pasif durumdadır
    When kullanıcı eksik bırakılan zorunlu alanı doldurur
    Then "Next" butonu aktif hale gelir

  Scenario: Adres Girişi Penceresinde Zorunlu Alan Eksikken Save Butonunun Pasif Kalması
    Given kullanıcı adres girişi penceresini açmıştır
    When kullanıcı zorunlu adres alanlarından birini "Şehir" boş bırakır
    Then "Save" butonu pasif durumdadır
    When kullanıcı eksik bırakılan zorunlu adres alanını doldurur
    Then "Save" butonu aktif hale gelir

  Scenario: Contact Medium Ekranında Geçersiz Email Formatı Girildiğinde Create Butonunun Pasif Kalması
    Given kullanıcı "Contact Medium" ekranındadır
    When kullanıcı email alanına geçersiz formatta bir değer girer
    Then sistem geçersiz email formatı uyarısını görüntüler
    And Create butonu pasif durumdadır
    When kullanıcı email alanını geçerli formatta bir değerle günceller
    Then Create butonu aktif hale gelir

  Scenario: Birth Date ve Gender Alan Davranışlarının Doğrulanması
    Then "Birth Date" alanı gün,ay,yıl formatında maskeli bir metin giriş alanıdır
    When kullanıcı "Birth Date" alanına bir tarih girer
    Then seçilen tarih "Birth Date" alanına doğru şekilde yazılır
    And "Gender" alanı ekrana ilk geldiğinde varsayılan olarak "Erkek" seçili görüntülenir
    When kullanıcı "Gender" alanını açar
    Then sistem tanımlı cinsiyet seçeneklerini listeler
    When kullanıcı listeden "Kadın" seçeneğini seçer
    Then "Gender" alanı "Kadın" olarak güncellenir

  Scenario: Adres Bilgisi Ekranında Adres Kartı Edit/Delete Aksiyonları ve Next Butonu Aktiflik Davranışı
    Given kullanıcı "Adres Bilgi" ekranındadır
    Then Adres adımında İleri butonu pasiftir
    When kullanıcı Adres alanlarını rastgele Faker değerlerle doldurup Save butonuna tıklar
    Then sistem adresi kart olarak listeler ve İleri butonu aktif hale gelir
    When kullanıcı adres kartındaki "Edit" seçeneğine tıklar
    Then adres bilgileri güncellenmek üzere form olarak açılır
    When kullanıcı adres form penceresini kapatır
    And kullanıcı adres kartındaki "Delete" seçeneğine tıklar
    Then adres kartı listeden kaldırılır
    And listede başka kayıtlı adres kalmadığı için İleri butonu tekrar pasif hale gelir

  Scenario: Kaydedilen Adresin "City, Street Name..." Formatında Kart Olarak Görüntülenmesi
    Given kullanıcı "Adres Bilgi" ekranında Şehir "İstanbul", Sokak "Bağdat Caddesi", No "45/2" ile bir adres formu doldurmuştur
    When kullanıcı "Save" butonuna tıklar
    Then adres kart olarak listelenir ve tamamı bina-daire no dahil okunabilir şekilde görüntülenir

  Scenario: Adres Kartında Edit Seçeneğiyle Mevcut Adresin Güncellenmesi
    Given kullanıcının "Adres Bilgi" ekranında kayıtlı bir adres kartı bulunmaktadır
    When kullanıcı adres kartındaki "Edit" seçeneğine tıklar
    Then adres bilgileri güncellenmek üzere form olarak açılır
    When kullanıcı "Sokak" alanını "Fenerbahçe Caddesi" olarak günceller
    And kullanıcı "Save" butonuna tıklar
    Then adres kartı güncellenmiş bilgilerle listelenir

  Scenario: Adres Kartında Delete Seçeneğiyle Adresin Status-Update Olarak Silinmesi
    Given kullanıcının "Adres Bilgi" ekranında kayıtlı bir adres kartı bulunmaktadır
    When kullanıcı adres kartındaki "Delete" seçeneğine tıklar
    Then adres kartı listeden kaldırılır

  Scenario: Contact Medium Ekranında Geçersiz Mobile Phone Formatı Girildiğinde Create Butonunun Pasif Kalması
    Given kullanıcı "Contact Medium" ekranındadır
    When kullanıcı "Mobile Phone" alanına geçersiz formatta bir değer girer
    Then sistem geçersiz telefon formatı uyarısını görüntüler
    And Create butonu pasif durumdadır
    When kullanıcı "Mobile Phone" alanını geçerli formatta bir değerle günceller
    Then Create butonu aktif hale gelir

  Scenario: Zorunlu ve Opsiyonel Tüm Alanlar Doldurulduğunda Müşterinin Eksiksiz Oluşturulması
    When kullanıcı Demografik Bilgi adımındaki zorunlu ve opsiyonel tüm alanları rastgele Faker değerleriyle doldurur
    And kullanıcı Demografik Bilgi adımında İleri butonuna tıklar
    And kullanıcı Adres alanlarını rastgele Faker değerlerle doldurup Save butonuna tıklar
    And kullanıcı Adres adımında İleri butonuna tıklar
    And kullanıcı İletişim Kanalı adımındaki zorunlu ve opsiyonel tüm alanları rastgele Faker değerleriyle doldurur
    Then Create butonu aktif hale gelir
    When kullanıcı Create butonuna tıklar
    Then sistem müşteri kaydını oluşturur ve "Customer Info" ekranını açar
    And opsiyonel alanlar dahil girilen tüm bilgiler eksiksiz ve doğru şekilde görüntülenir

  Scenario Outline: Second Name/Father Name/Mother Name Alanlarının 100 Karakter Sınırının Korunması
    When "<alan>" alanına 101 karakterlik değer girilmeye çalışılır
    Then alan en fazla 100 karakteri kabul eder

    Examples:
      | alan        |
      | Second Name |
      | Father Name |
      | Mother Name |

  Scenario Outline: Second Name/Father Name/Mother Name Alanlarının Tam 100 Karakterlik Değeri Kabul Etmesi
    When "<alan>" alanına tam 100 karakterlik bir değer girilir
    Then alan girilen 100 karakterin tamamını kabul eder

    Examples:
      | alan        |
      | Second Name |
      | Father Name |
      | Mother Name |

  # NOT (canlı doğrulandı): Birth Date maskesi basit "ilk N rakamı al"
  # mekanizması DEĞİL - gün/ay geçerliliğini ANLIK doğrulayan daha karmaşık
  # bir maske (ör. "123456789" yazılınca ay basamağı geçersiz kaldığından
  # bazı rakamlar sessizce filtreleniyor, sonuç girilen rakamların birebir
  # ilk 8'i OLMUYOR - "12/03/4567" gibi beklenmedik bir değer çıkıyor). Bu
  # yüzden senaryo GERÇEKTEN geçerli, belirsizlik yaratmayan bir tarihle
  # (15/06/1990) test ediliyor - kesin ara rakam dizisini değil, yalnızca
  # 10 karakterlik (8 rakam + 2 ayraç) üst sınırın korunduğunu ve fazla
  # rakamın hiçbir etkisi olmadığını doğruluyor. Dilden bağımsız: EN dilinde
  # placeholder "gg/aa/yyyy" -> "dd/mm/yyyy" değişse de (canlı doğrulandı)
  # maskenin kendisi ve 10 karakterlik sınır AYNI kalıyor.
  Scenario: Birth Date Alanının Maskeli Giriş Kapasitesinin (8 Rakam / gg/aa/yyyy) Sınırını Koruması
    When "Birth Date" alanına geçerli 8 rakamlık bir tarih yazılır
    Then alan "gg/aa/yyyy" formatında, tam 10 karakter uzunluğunda bir değer gösterir
    When aynı alana 9. bir rakam yazılmaya çalışılır
    Then alanın değeri değişmeden kalır, fazla rakamın hiçbir etkisi olmaz
