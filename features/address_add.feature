Feature: Yeni Müşteri Adresinin Eklenmesi

  Scenario: TC-EACRML-007-01 - Adres sekmesinde "Yeni Adres Ekle" ile mevcut müşteriye ek bir adres kaydedilmesi
    Given kullanıcı bir müşterinin Adres sekmesindedir
    When kullanıcı "Yeni Adres Ekle" butonuna tıklayıp formu doldurup Save butonuna tıklar
    Then sistem gerçek bir POST isteğiyle yeni adresi addresses endpoint'ine kaydeder

  Scenario: TC-EACRML-007-02 - Eklenen yeni adresin mevcut adres(ler)i silmeden ayrı bir kart olarak listeye eklenmesi
    Given müşterinin zaten kayıtlı bir adresi vardır
    When kullanıcı yeni bir adres ekler
    Then önceki kart silinmez, yeni adres AYRI bir kart olarak eklenir

  Scenario Outline: TC-EACRML-007-03 - Zorunlu alanlardan biri boşken Save butonunun pasif kalması
    Given kullanıcı yeni adres formundadır
    When "<alan>" alanı boşaltılır
    Then Save butonu pasif kalır

    Examples:
      | alan     |
      | Şehir    |
      | Sokak    |
      | Bina No  |
      | Açıklama |

  Scenario: TC-EACRML-007-04 - Bina/Daire No alanının alfanumerik değer kabul etmesi
    Given kullanıcı yeni adres formundadır
    When Bina No alanına "12 D:4" gibi harf ve rakam karışık bir değer girilir
    Then değer sorunsuz kabul edilir

  Scenario: TC-EACRML-007-05 - Adres ekleme formu iptal edilirse hiçbir adresin kaydedilmemesi
    Given kullanıcı yeni adres formunu doldurmuştur
    When İptal butonuna tıklanır
    Then hiçbir adres kaydedilmez

  Scenario: TC-EACRML-007-06 - Şehir alanının yalnızca tanımlı 81 ilden biriyle seçilebilmesi
    Given kullanıcı yeni adres formundadır
    When Şehir dropdown'ı açılır
    Then yalnızca 81 il listelenir, serbest metin girişine izin verilmez

  Scenario: TC-EACRML-007-07 - Aynı müşteriye art arda 3 veya daha fazla adres eklenebilmesi
    Given müşterinin 2 kayıtlı adresi vardır
    When kullanıcı 3. bir adres daha ekler
    Then herhangi bir üst sınır hatasıyla karşılaşılmadan 3 adres de listelenir

  Scenario: TC-EACRML-007-08 - Yeni eklenen adresin listede "Şehir, Sokak Adı, No" formatında okunabilir şekilde yer alması
    Given kullanıcı yeni bir adres eklemiştir
    When Adres sekmesi görüntülenir
    Then yeni kart "Şehir, Sokak Adı, No" formatında okunabilir şekilde listede yer alır
