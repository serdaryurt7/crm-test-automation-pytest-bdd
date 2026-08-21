Feature: Fatura Hesabı Güncelleme

  Scenario: TC-EACRML-011-01 - Hesap satırındaki Edit seçeneğiyle "Fatura Hesabını Düzenle" formunun mevcut bilgilerle açılması
    Given kullanıcı Müşteri Hesabı sekmesinde bir hesap satırı görüntülemektedir
    When kullanıcı Edit butonuna tıklar
    Then "Fatura Hesabını Düzenle" formu mevcut Hesap Adı, Açıklaması, Adres bilgileriyle önceden dolu açılır

  Scenario: TC-EACRML-011-02 - Hesap Adı ve Adres güncellenip kaydedildiğinde listedeki satırın yeni bilgilerle yenilenmesi
    Given kullanıcı hesap düzenleme formundadır
    When Hesap Adı ve Adres alanları geçerli değerlerle güncellenip Kaydet'e tıklanır
    Then satır listede yeni bilgiyle yenilenir

  Scenario: TC-EACRML-011-03 - Güncelleme formunda Hesap Adı boşaltıldığında güncellemenin engellenmesi
    Given kullanıcı hesap düzenleme formundadır
    When Hesap Adı alanı boşaltılır
    Then ilgili alan hatalı olarak işaretlenir
    And güncelleme gerçekleştirilmez, kullanıcı düzenleme ekranında kalır

  Scenario: TC-EACRML-011-04 - Hesabın bağlı olduğu hizmet adresinin güncelleme formunda değiştirilebilmesi
    Given kullanıcı hesap düzenleme formundadır
    When hizmet adresi müşterinin başka bir kayıtlı adresiyle değiştirilir
    Then kaydedildiğinde hesap yeni adresle ilişkilendirilir

  Scenario: TC-EACRML-011-06 - Güncelleme formunda İptal edilince hesap bilgilerinin değişmeden kalması
    Given kullanıcı formda değişiklik yapmıştır
    When İptal butonuna tıklanır
    Then hesap bilgileri değişmeden kalır
