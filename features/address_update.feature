Feature: Müşteri Adresinin Güncellenmesi

  Background:
    Given kullanıcı bir müşterinin Adres sekmesinde kayıtlı bir adres kartı görüntülemektedir

  Scenario: TC-EACRML-006-01 - Adres sekmesinde kayıtlı bir adres kartında Edit seçeneğiyle formun mevcut bilgilerle ön-dolu açılması
    When kullanıcı kart menüsünden "düzenle" seçeneğini seçer
    Then form Şehir, Sokak, Bina No, Açıklama alanlarıyla önceden dolu açılır

  Scenario: TC-EACRML-006-02 - Şehir/Sokak/Bina No alanları güncellenip kaydedildiğinde kartın yeni bilgilerle yenilenmesi
    Given kullanıcı adres düzenleme formundadır
    When Sokak, Bina No alanları değiştirilip Kaydet'e tıklanır
    Then kart yeni bilgilerle güncellenir

  Scenario Outline: TC-EACRML-006-03 - Güncelleme formunda zorunlu alan boşaltıldığında Kaydet butonunun pasif kalması
    Given kullanıcı adres düzenleme formundadır
    When "<alan>" alanı boşaltılır
    Then Kaydet butonu pasif kalır

    Examples:
      | alan     |
      | Sokak    |
      | Bina No  |
      | Açıklama |

  Scenario: TC-EACRML-006-04 - Güncelleme formunda İptal edilince adres kartının değişmeden kalması
    Given kullanıcı adres düzenleme formunda değişiklik yapmıştır
    When İptal butonuna tıklanır
    Then kart eski bilgileriyle kalır

  Scenario: TC-EACRML-006-05a - Adres Açıklaması Alanının Herhangi Bir Üst Karakter Sınırı Olmadan Uzun Metni Kabul Etmesi
    Given kullanıcı adres düzenleme formundadır
    When Açıklama alanına 3000 karakterlik bir metin girilir
    Then alan girilen metnin tamamını kabul eder

  Scenario: TC-EACRML-006-05b - Adres Açıklaması Alanının Tanımlı Bir Üst Karakter Sınırını Aşan Girişi Reddetmesi
    Given kullanıcı adres düzenleme formundadır
    When Açıklama alanına 3000 karakterlik bir metin girilir
    Then alan tanımlı karakter sınırını aşan girişi kabul etmez

  Scenario Outline: TC-EACRML-006-09/006-10 - Sokak/Bina No Alanlarının Herhangi Bir Üst Karakter Sınırı Olmadan Uzun Metni Kabul Etmesi
    Given kullanıcı adres düzenleme formundadır
    When "<alan>" alanına 500 karakterlik bir metin girilir
    Then alan girilen 500 karakterlik değerin tamamını kabul eder

    Examples:
      | alan    |
      | Sokak   |
      | Bina No |

  Scenario: TC-EACRML-006-06a - Birden Fazla Adresten İkincisi Primary Seçildiğinde Anlık Olarak Yalnızca Onun Primary Kalması
    Given müşterinin birden fazla adresi vardır
    When kullanıcı ikinci adresi Primary olarak işaretler
    Then yalnızca bu adres Primary görüntülenir, öncekinin işareti anlık olarak kalkar

  Scenario: TC-EACRML-006-06b - Primary Adres Değişikliğinin Sayfa Yenilense Dahi Kalıcı Olarak Korunması
    Given müşterinin birden fazla adresi vardır
    When kullanıcı ikinci adresi Primary olarak işaretler
    Then sayfa yenilendiğinde de yalnızca ikinci adres Primary olarak kalır

  Scenario: TC-EACRML-006-07 - Tek Adresli Müşteride Primary Adres Seçeneğinin Otomatik Seçili ve Değiştirilemez Olması
    Then tek adres otomatik olarak Primary işaretlidir
    And değiştirilecek başka bir adres seçeneği bulunmadığından bu işaret değişmez

  Scenario: TC-EACRML-006-08 - Adres Kartı Üzerinde Bilgilerin "Şehir, Sokak, No" Formatında Eksiksiz Görüntülenmesi
    Then kart başlığı "Şehir, Sokak, No" formatında ve açıklama eksiksiz görüntülenir
