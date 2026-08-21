Feature: Siparişin Tamamlanması

  Scenario: TC-EACRML-016-01 - Sipariş Gönder ekranında seçilen tekliflerin, hizmet adresinin ve toplam tutarın özet olarak görüntülenmesi
    Given kullanıcı Ürün Konfigürasyonu adımını tamamlamıştır
    When Sipariş Gönder ekranına geçilir
    Then seçilen teklifler, hizmet adresi ve toplam tutar özet olarak görüntülenir

  Scenario: TC-EACRML-016-02 - Sepete tek kez eklenen bir teklifin sipariş özetinde de tam bir kez görüntülenmesi
    Given kullanıcı sepete yalnızca bir kez bir teklif eklemiştir
    Then özet listesinde bu teklif TAM 1 KEZ, doğru toplam tutarla görüntülenmelidir

  Scenario: TC-EACRML-016-03 - "Gönder" butonuna tıklandığında siparişin oluşturulup ilgili ürünlerin fatura hesabına eklenmesi
    Given kullanıcı Sipariş Gönder ekranındadır
    When "Gönder" butonuna tıklanır
    Then sipariş oluşturulur, ürünler ilgili fatura hesabına eklenir

  Scenario: TC-EACRML-016-04 - "Geri" butonuyla Ürün Konfigürasyonu ekranına dönülüp bilgilerin korunması
    Given kullanıcı Sipariş Gönder ekranındadır
    When "Geri" butonuna tıklanır
    Then Ürün Konfigürasyonu ekranına dönülür ve girilen bilgiler korunur

  Scenario: TC-EACRML-016-05 - Sipariş başarıyla tamamlandıktan sonra ayrı bir başarı ekranının ve Sipariş ID'sinin gösterilmesi
    Given kullanıcı siparişi başarıyla göndermiştir
    Then "Sipariş oluşturuldu!" başlıklı bir başarı ekranı görüntülenir
    And bir Sipariş ID'si gösterilir

  Scenario: TC-EACRML-016-06 - Sipariş gönderimi sırasında bir iletişim/sunucu hatası oluşması durumunda kullanıcıya anlamlı bir hata mesajı gösterilmesi
    Given kullanıcı Sipariş Gönder ekranındadır
    When "Gönder" isteği sırasında bir sunucu, ağ hatası simüle edilir
    Then kullanıcıya anlamlı bir hata mesajı gösterilir
    And yanlış bir başarı yönlendirmesi yapılmaz

  Scenario: TC-EACRML-016-08 - Submit Order ekranında benzersiz Order ID üretilmesi
    Given "Product Configuration" tamamlanmış ve "Submit Order" ekranı açılmıştır
    When art arda birden fazla sipariş oluşturulur
    Then her siparişin Order ID'si birbirinden farklıdır
