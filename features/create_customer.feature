Feature: Müşteri Oluşturma
  Kullanıcının yeni müşteri kaydı oluşturabilmesi

  Background:
    Given kullanıcı müşteri oluşturma sayfasındadır

  Scenario Outline: Demografik, Adres ve İletişim Bilgileriyle Uçtan Uca Müşteri Yaratma 2
    When kullanıcı zorunlu Demografik Bilgi alanlarını Gender "<gender>" ile rastgele (Faker) değerlerle doldurur
    Then girilen değerler ilgili alanlarda görüntülenir
    When kullanıcı Demografik Bilgi adımında İleri butonuna tıklar
    Then sistem Nationality ID'nin kayıtlı olmadığını doğrular ve "Adres Bilgisi" ekranını açar
    And Adres adımında İleri butonu pasiftir
    When kullanıcı Adres alanlarını rastgele (Faker) değerlerle doldurup Save butonuna tıklar
    Then sistem adresi kart olarak listeler ve İleri butonu aktif hale gelir
    When kullanıcı Adres adımında İleri butonuna tıklar
    Then sistem "İletişim Kanalı" ekranını açar
    When kullanıcı İletişim Kanalı alanlarını rastgele (Faker) değerlerle doldurur
    Then Create butonu aktif hale gelir
    When kullanıcı Create butonuna tıklar
    Then sistem müşteri kaydını oluşturur ve "Customer Info" ekranını açar
    And müşterinin Cinsiyet bilgisi "<gender>" olarak görüntülenir

    Examples:
      | gender |
      | Kadın  |
      | Erkek  |
