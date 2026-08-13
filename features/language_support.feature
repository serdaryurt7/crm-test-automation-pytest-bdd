Feature: Dil Desteği

  # TC-EACRML-017-04 ÜZERİNE NOT: Spesifikasyon, oturum kapatılıp tekrar
  # giriş yapıldığında dilin varsayılan TR'ye DÖNMESİNİ bekliyordu -
  # kullanıcının kendi notu bunun "hesaba değil oturuma bağlı" bir tasarım
  # varsayımına dayandığını ve BA/UX ile teyit edilmesi gerektiğini
  # belirtiyordu. Canlı doğrulandı: dil tercihi localStorage'da
  # (`etiya.language`) saklanıyor - bu TAM bir çıkış/giriş döngüsünden
  # BAĞIMSIZ olarak kalıcı, yani EN seçilip çıkış yapılıp tekrar giriş
  # yapıldığında arayüz TR'ye DÖNMÜYOR, EN kalmaya devam ediyor. Kullanıcı
  # kararıyla senaryo GERÇEK/çalışan davranışı doğrulayacak şekilde
  # uyarlandı (aşağıda).

  Scenario: TC-EACRML-017-01 - Dil değiştirici (TR/EN) panelinin açılıp kapatılabilmesi
    Given kullanıcı uygulamada herhangi bir ekrandadır
    When dil değiştirici butonuna tıklanır
    Then TR/EN seçenekleri içeren panel açılır
    When dil değiştirici butonuna tekrar tıklanır
    Then panel kapanır

  Scenario: TC-EACRML-017-02 - "EN" seçildiğinde arayüz metinlerinin İngilizce'ye çevrilmesi
    Given dil değiştirici panel açıktır
    When "EN" seçeneğine tıklanır
    Then menü/buton/başlık gibi arayüz metinleri değişir (İngilizce'ye çevrilir)
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
    Given dil "EN"dir
    When bir doğrulama hatası tetiklenir (Kimlik No formatı)
    Then mesaj Türkçe halinden farklı, İngilizce dilde görüntülenir

  Scenario: TC-EACRML-017-07 - Aktif dilin dil değiştirici buton üzerinde doğru şekilde vurgulanması
    Given aktif dil "TR"dir
    When dil değiştirici panel görüntülenir
    Then panelde aktif dil ("TR") vurgulanmış olarak işaretlenir

  Scenario: TC-EACRML-017-08 - Dil seçeneğinin yalnızca TR ve EN ile sınırlı olması
    Given kullanıcı dil değiştirici paneli açmıştır
    Then yalnızca TR ve EN seçenekleri listelenir, başka dil bulunmaz
