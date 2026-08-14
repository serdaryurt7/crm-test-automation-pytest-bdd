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

  # KASITLI KIRMIZI (canlı doğrulandı, bkz. bugsbunny.txt madde 17): sistem
  # şu an bu kuralı UYGULAMIYOR - aktif ürünü olan bir müşteri hiçbir
  # engelleme olmadan silinebiliyor (customer 854 ile uçtan uca test
  # edildi: silme başarıyla gerçekleşti, Müşteri Arama ekranına
  # yönlendirildi). Bu senaryo spesifikasyonun DOĞRU davranışını izliyor;
  # bilinen defekt düzelene kadar FAILED kalması beklenen sonuçtur - AYNI
  # kök nedenin fatura-hesabı seviyesindeki (TC-012-03) tezahürüyle
  # tutarlı bir karar (bkz. billing_account_delete.feature).
  #
  # DİLDEN BAĞIMSIZ (tek senaryo, TR/EN'i AYNI anda destekler): Then
  # adımlarının hiçbiri literal TR/EN metin karşılaştırmıyor (yapısal -
  # URL/durum kontrolü). Bunu SADECE teoride değil pratikte de kanıtlamak
  # için akış BİLEREK arayüz dili İngilizce'ye çevrilmiş şekilde
  # çalıştırılıyor - eğer kontrol gizliden Türkçe metne bağımlı olsaydı bu
  # EN çalıştırmada kırılırdı. Aynı mekanizma varsayılan (TR) dilde de
  # değişmeden çalışır - bu yüzden ayrı bir TR örneğine (Outline'a) gerek
  # yok, tek senaryo her iki dili de kapsıyor.
  Scenario: TC-EACRML-005-03 - Aktif ürünü olan müşterinin silinememesi
    Given görüntülenen müşteriye ait, bir fatura hesabına bağlı en az bir aktif ürün kaydı vardır
    And kullanıcı arayüz dilini İngilizce olarak ayarlamıştır
    When kullanıcı Delete ikonuna tıklar
    And kullanıcı "Evet" butonuna tıklar
    Then sistem müşteriyi silmeyi reddeder
    And kullanıcı Müşteri Bilgisi ekranında kalır, müşteri durumu değişmeden kalır
