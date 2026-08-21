Feature: Teklif Seçimi

  Scenario: TC-EACRML-014-01 - "Yeni Satış Başlat" ile Teklif Seçimi ekranına geçiş ve varsayılan katalog listesinin görüntülenmesi
    Given kullanıcı bir fatura hesabının Müşteri Hesabı ekranındadır
    When kullanıcı "Yeni Satış Başlat" butonuna tıklar
    Then sistem "Teklif Seçimi" başlıklı ekrana yönlendirir ve varsayılan katalog listesini gösterir

  Scenario: TC-EACRML-014-02 - Katalog dropdown'ından filtreleme yapıldığında sonuçların daralması
    Given kullanıcı Teklif Seçimi ekranındadır
    When kullanıcı katalog dropdown'ından "Mobil" seçeneğini seçer
    Then yalnızca Mobil kategorisindeki teklifler listelenir

  Scenario: TC-EACRML-014-03 - Teklif ID veya Teklif Adı filtreleriyle arama yapılıp "Ara" butonuna tıklanması
    Given kullanıcı Teklif Seçimi ekranındadır
    When Teklif Adı filtresine bir değer girilip Ara'ya tıklanır
    Then yalnızca eşleşen teklifler listelenir

  Scenario: TC-EACRML-014-04 - Var olmayan bir Teklif ID/Adı ile arandığında sonuç bulunamadı durumunun gösterilmesi
    Given kullanıcı Teklif Seçimi ekranındadır
    When var olmayan bir Teklif Adı ile arama yapılır
    Then sonuç bulunamadı durumu görüntülenir

  Scenario: TC-EACRML-014-05 - Bir teklifin seçilip "Sepete Ekle" ile sepete eklenmesi ve toplam tutarın güncellenmesi
    Given kullanıcı bir teklif satırı seçmiştir
    When "Sepete Ekle" butonuna tıklanır
    Then teklif sepette listelenir
    And toplam tutar teklifin fiyatı kadar artar

  Scenario: TC-EACRML-014-08 - Sepete yalnızca bir kez eklenen teklifin sipariş özetinde de tam bir kez görüntülenmesi
    Given kullanıcı sepete "Ev İnterneti Fiber 100" teklifini YALNIZCA BİR KEZ eklemiştir
    When kullanıcı İleri ile Ürün Konfigürasyonu ve Sipariş Özeti ekranlarına ilerler
    Then sipariş özetinde bu teklif TAM 1 KEZ görüntülenmeli, toplam tutar 299.90 TL olmalıdır

  Scenario: TC-EACRML-014-09 - "Temizle" butonuyla sepetteki tüm ürünlerin kaldırılıp toplam tutarın 0.00 TL'ye dönmesi
    Given sepette en az bir teklif vardır
    When "Temizle" butonuna tıklanır
    Then sepet boşalır, toplam "0.00 TL" olur

  Scenario: TC-EACRML-014-10 - Sepet boşken "İleri" butonunun pasif kalması
    Given sepet boştur
    Then "İleri" butonu pasif durumdadır

  Scenario: TC-EACRML-014-11 - "Kampanya" sekmesine geçildiğinde kampanya bazlı tekliflerin katalogdan ayrı listelenmesi
    Given kullanıcı Teklif Seçimi ekranındadır
    When "Kampanya" sekmesine geçilir
    Then kampanya bazlı teklifler katalogdan ayrı bir liste olarak görüntülenir

  Scenario: TC-EACRML-014-12 - Teklif ID filtresine harf girilip arandığında sonuç bulunamaması
    Given kullanıcı Teklif Seçimi ekranındadır
    When Teklif ID filtresine harf girilip Ara'ya tıklanır
    Then sonuç bulunamadı durumu görüntülenir

  Scenario: TC-EACRML-014-13 - Sepette zaten bulunan bir ürünün tekrar eklenmeye çalışılmasının engellenmesi
    Given sepette en az bir ürün vardır
    When kullanıcı aynı ürünü tekrar "Sepete Ekle" ile eklemeyi dener
    Then sepete mükerrer bir kayıt eklenmez
    And Basket içeriği ve Total Amount değişmeden kalır

  Scenario: TC-EACRML-014-14 - Campaign sekmesinden kampanya seçilerek bağlı tüm ürünlerin sepete eklenmesi
    Given kullanıcı Campaign sekmesindedir
    When bir kampanya seçilip "Sepete Ekle" ile eklenir
    Then kampanya sepete eklenir
    And Total Amount kampanyanın indirimli fiyatını yansıtır
