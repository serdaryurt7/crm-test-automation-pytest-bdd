Feature: Dil Desteği

  Scenario: TC-EACRML-017-01 - Dil değiştirici (TR/EN) panelinin açılıp kapatılabilmesi
    Given kullanıcı uygulamada herhangi bir ekrandadır
    When dil değiştirici butonuna tıklanır
    Then TR, EN seçenekleri içeren panel açılır
    When dil değiştirici butonuna tekrar tıklanır
    Then panel kapanır

  Scenario: TC-EACRML-017-02 - "EN" seçildiğinde arayüz metinlerinin İngilizce'ye çevrilmesi
    Given dil değiştirici panel açıktır
    When "EN" seçeneğine tıklanır
    Then menü, buton, başlık gibi arayüz metinleri İngilizce'ye çevrilir
    And bu tercih kullanıcı farklı ekranlara geçse dahi oturum boyunca korunur

  Scenario: TC-EACRML-017-03 - Dil değişikliğinin sayfa yenilense dahi korunması
    Given kullanıcı dili "EN" yapmıştır
    When sayfa yenilenir
    Then arayüz İngilizce kalmaya devam eder

  Scenario: TC-EACRML-017-04 - EN dili seçiliyken oturum kapatılıp tekrar giriş yapıldığında dil tercihinin korunması
    Given kullanıcı arayüz dilini EN olarak ayarlamıştır
    When kullanıcı oturumu kapatıp tekrar giriş yapar
    Then arayüz EN olarak kalmaya devam eder, TR'ye dönmez

  Scenario: TC-EACRML-017-05 - Dil değişikliğinin, yapısal (data-testid bazlı) kontrollerin etkilenmeden, yalnızca görünen metni değiştirmesi
    Given otomasyon testleri data-testid tabanlı locator kullanmaktadır
    When dil "EN" olarak değiştirilir
    Then tüm data-testid değerleri dilden bağımsız aynı kalır, yalnızca görünen metin değişir

  Scenario: TC-EACRML-017-06 - İngilizce dilde iken doğrulama mesajlarının Türkçe'den farklı (İngilizce) dilde görüntülenmesi
    Given dil "EN" dir
    When Kimlik No formatı için bir doğrulama hatası tetiklenir
    Then mesaj Türkçe halinden farklı, İngilizce dilde görüntülenir

  Scenario: TC-EACRML-017-07 - Aktif dilin dil değiştirici buton üzerinde doğru şekilde vurgulanması
    Given aktif dil "TR" dir
    When dil değiştirici panel görüntülenir
    Then panelde aktif dil "TR" vurgulanmış olarak işaretlenir

  Scenario: TC-EACRML-017-08 - Dil seçeneğinin yalnızca TR ve EN ile sınırlı olması
    Given kullanıcı dil değiştirici paneli açmıştır
    Then yalnızca TR ve EN seçenekleri listelenir, başka dil bulunmaz
