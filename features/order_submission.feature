Feature: Siparişin Tamamlanması

  # KAPSAM DIŞI BIRAKILAN SENARYO:
  #
  # TC-EACRML-016-07 [ASKIDA]: "Tamamlayıcı ürün" (complementary product)
  # kavramı UC-EACRML 014'te (TC-014-06/07) zaten [ASKIDA] olarak
  # işaretlenmiş ve kullanıcı kararıyla suite dışı bırakılmıştı - dokümanda
  # hiç geçmeyen, PM/BA onayı bekleyen bir özellik. Bu senaryo AYNI
  # onaylanmamış önkoşula bağımlı olduğundan suite'e alınmadı.
  #
  # TC-EACRML-016-02 ve TC-EACRML-016-05 ÜZERİNE NOTLAR:
  #
  # TC-EACRML-016-02 [DEFEKT ADAYI]: Kullanıcının işaret ettiği "aynı kök
  # neden UC-014-08" iddiası - "Sipariş Gönder" ekranı, TC-014-08'in test
  # ettiği ekranla AYNI ekran (sales-summary-line/sales-summary-total).
  # Canlı olarak 5 AYRI denemede DE (3'ü UC-014 keşfinde, 2'si bu UC'de)
  # yeniden üretilemedi - teklif her seferinde TAM 1 kez, doğru toplamla
  # görüntülendi. TC-014-08'deki AYNI kullanıcı kararına göre (spesifikasyonu
  # olduğu gibi/doğru davranış olarak implemente et) burada da UYGULANDI -
  # şu an PASS veren, ortam davranışı tekrar bozulursa otomatik regresyon
  # yakalayacak bir test. UC-014-08 ile YAPISAL OLARAK aynı kontrolü
  # tekrarlıyor olması BİLİNÇLİ bir tercih: her UC'nin kendi feature
  # dosyasında bağımsız/eksiksiz doğrulanabilir olması (INVEST -
  # Independent) her iki dokümanın da kendi başına ayrı bir kanıt
  # sunmasını sağlıyor.
  #
  # TC-EACRML-016-05: Dokümanın kendisi "Adım 8'den sonra ne olduğu
  # belirtilmemiş" diyerek bu davranışı teyit edemiyordu. Canlı keşifle
  # KESİN olarak netleşti: sipariş başarıyla gönderildiğinde kullanıcı
  # Müşteri Hesabı'na OTOMATİK yönlendirilmiyor - "Sipariş oluşturuldu!"
  # başlıklı AYRI bir başarı ekranında kalıyor, orada bir Sipariş ID'si
  # ve "Müşteri Aramaya Dön" bağlantısı gösteriliyor. Artık kesin bir Then
  # ifadesiyle otomasyona alınabilir hale geldi.

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
    When "Gönder" isteği sırasında bir sunucu/ağ hatası simüle edilir
    Then kullanıcıya anlamlı bir hata mesajı gösterilir
    And yanlış bir başarı yönlendirmesi yapılmaz

  Scenario: TC-EACRML-016-08 - Submit Order ekranında benzersiz Order ID üretilmesi
    Given "Product Configuration" tamamlanmış ve "Submit Order" ekranı açılmıştır
    When art arda birden fazla sipariş oluşturulur
    Then her siparişin Order ID'si birbirinden farklıdır
