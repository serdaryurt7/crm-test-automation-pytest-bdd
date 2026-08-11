Feature: Müşteri Bilgilerini Silme

  Background:
    Given kullanıcı silinecek müşterinin Müşteri Bilgisi ekranındadır

  Scenario: TC-EACRML-005-01 - Müşteri Bilgisi ekranında Delete butonuna tıklandığında onay penceresinin görüntülenmesi
    When kullanıcı Delete ikonuna tıklar
    Then onay penceresi, silme mesajı ve Evet, Hayır butonlarıyla birlikte görüntülenir

  Scenario: TC-EACRML-005-04 - Onay penceresinde "Hayır" seçilince işlemin iptal edilip müşteri kaydının değişmeden kalması
    Given onay penceresi görüntülenmektedir
    When kullanıcı "Hayır" butonuna tıklar
    Then pencere kapanır
    And müşteri kaydı hiçbir şekilde değiştirilmeden ekranda kalmaya devam eder

  Scenario: TC-EACRML-005-07 - Onay penceresi açıkken ekranın diğer alanlarıyla etkileşimin engellenmesi (modal davranışı)
    Given onay penceresi görüntülenmektedir
    When kullanıcı arka plandaki herhangi bir alanla etkileşime girmeyi dener
    Then pencere modal davranışı gösterip arka planı engeller

  Scenario: TC-EACRML-005-02 - Onay Penceresinde "Evet" Seçilince Müşterinin Müşteri Arama Ekranına Yönlendirilmesi
    Given onay penceresi görüntülenmektedir
    When kullanıcı "Evet" butonuna tıklar
    Then kullanıcı Müşteri Arama ekranına yönlendirilir

  Scenario: TC-EACRML-005-05 - Silinen Müşterinin Arama Sonuçlarında Artık Görüntülenmemesi
    Given onay penceresi görüntülenmektedir
    When kullanıcı "Evet" butonuna tıklar
    Then silinen müşteri arama sonuçlarında artık görüntülenmez

  Scenario: TC-EACRML-005-06 - Silinen Müşterinin Detay Ekranına Doğrudan Erişilmeye Çalışılması
    Given onay penceresi görüntülenmektedir
    When kullanıcı "Evet" butonuna tıklar
    Then silinen müşterinin eski detay ekranına doğrudan gidildiğinde bir "bulunamadı" durumu görüntülenir
