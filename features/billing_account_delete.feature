Feature: Fatura Hesabını Silme

  Scenario: TC-EACRML-012-01 - Hesap satırındaki Delete seçeneğiyle fatura hesabının silinmesi
    Given kullanıcı, aktif ürünü olmayan bir hesap satırı görüntülemektedir
    When Delete butonuna tıklanır ve onay penceresinde onaylanırsa
    Then hesap aktif hesap listesinden kalıcı olarak kaldırılır

  Scenario: TC-EACRML-012-02 - Silme onay penceresinde "Hayır" butonuna tıklandığında işlemin iptal edilmesi
    Given silme onay penceresi görüntülenmektedir
    When kullanıcı "Hayır" butonuna tıklar
    Then herhangi bir değişiklik yapılmaz, onay penceresi kapanır
    And kullanıcı Müşteri Hesabı ekranında kalır

  Scenario: TC-EACRML-012-03 - Aktif ürün/aboneliği bulunan bir fatura hesabının silinmeye çalışılması durumunda sistemin uyarı vermesi
    Given hesaba bağlı en az bir aktif ürün vardır
    When kullanıcı hesabı silmeyi dener
    Then hesap listeden kaldırılmaz
    And sistem doğrudan silmek yerine bir uyarı, engelleme mesajı gösterir

  Scenario: TC-EACRML-012-04 - Silinen hesabın aktif hesap listesinden kaldırılması
    Given bir fatura hesabı silinmiştir
    When Müşteri Hesabı sekmesindeki hesap listesi görüntülenir
    Then silinen hesap artık bu listede görüntülenmez

  Scenario: TC-EACRML-012-05 - Müşterinin tek fatura hesabı silindiğinde "Hesap bulunmuyor" boş durumuna dönülmesi
    Given müşterinin yalnızca 1 hesabı vardır
    When bu hesap silinir
    Then "Hesap bulunmuyor" boş durumuna dönülür

  Scenario: TC-EACRML-012-06 - Silme isteğinin tekrarlanmasının güvenli şekilde reddedilmesi
    Given bir hesap silinmiştir
    When kullanıcı aynı hesabı artık silinmiş, stale bir referansla tekrar silmeyi dener
    Then sistem ikinci denemeyi güvenli şekilde reddeder, uygulama tutarlı durumda kalır
