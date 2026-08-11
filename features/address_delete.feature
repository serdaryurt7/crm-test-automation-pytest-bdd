Feature: Müşteri Adresinin Silinmesi

  Scenario: TC-EACRML-008-01 - Adres kartı menüsünden Delete seçeneğiyle kayıtlı bir adresin silinmesi
    Given kullanıcı, birden fazla adresi olan bir müşterinin adres kartını görüntülemektedir
    When kullanıcı kart menüsünden "Sil"i seçer
    Then sistem adresi kalıcı olarak siler (sayfa yenilense dahi adres listede görünmez)

  Scenario: TC-EACRML-008-02 - Silinen adres kartının ekrandaki listeden onay penceresi olmadan anında kaldırılması
    Given kullanıcı "Sil" seçeneğine tıklamıştır
    Then herhangi bir onay penceresi GÖRÜNTÜLENMEZ
    And kart listeden anında kaldırılır

  Scenario: TC-EACRML-008-03 - Müşterinin tek adresi varken Delete seçeneğinin pasif (disabled) görüntülenmesi
    Given müşterinin yalnızca 1 kayıtlı adresi vardır
    When kullanıcı adres kartı menüsünü açar
    Then Delete seçeneği pasif (disabled) olarak görüntülenir
    And tıklansa dahi adres silinemez

  Scenario: TC-EACRML-008-04 - Primary olarak işaretli adres silindiğinde kalan adreslerden birinin otomatik Primary olup olmadığının doğrulanması
    Given müşterinin birden fazla adresi ve Primary işaretli biri vardır
    When Primary adres silinir
    Then kalan adreslerden birinin otomatik Primary olup olmadığı doğrulanır

  Scenario: TC-EACRML-008-06 - Adres silme isteğinin tekrarlanmasının güvenli şekilde reddedilmesi
    Given bir adres silinmiştir
    When kullanıcı aynı adresi (artık silinmiş, stale bir referansla) tekrar silmeyi dener
    Then sistem ikinci denemeyi güvenli şekilde reddeder, uygulama tutarlı durumda kalır

  Scenario: TC-EACRML-008-05 - Fatura hesabının hizmet adresi olarak kullanılan bir adresin silinmeye çalışılması durumunun doğrulanması
    Given bir adres, aktif bir Fatura Hesabının hizmet adresi olarak kullanılmaktadır
    When kullanıcı bu adresi silmeyi dener
    Then sistemin gerçek davranışı doğrulanır: adres herhangi bir engelleme veya uyarı olmadan serbestçe silinir
