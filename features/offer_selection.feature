Feature: Teklif Seçimi

  # KAPSAM DIŞI BIRAKILAN 2 SENARYO (kullanıcının kendi spesifikasyonunda
  # [ASKIDA] olarak işaretlenmişti - dokümanın 8 UC-014 test case'inde bu
  # özelliklerden hiç bahsedilmiyor, PM/BA onayı gelene kadar suite'e
  # ALINMADI):
  #   TC-EACRML-014-06 - Tamamlayıcı ürün gereken teklif seçildiğinde uyarı
  #   TC-EACRML-014-07 - "Birlikte alınması önerilenler" çapraz satış önerisi
  #
  # TC-EACRML-014-08 NOTU: Kullanıcı bunu "DEFEKT ADAYI" (sipariş özetinde
  # teklifin 3 kez tekrarlanıp 899.70 TL çıktığı) olarak işaretlemişti.
  # Canlı olarak 3 AYRI denemede DE yeniden üretilemedi - "Ev İnterneti
  # Fiber 100" TAM 1 KEZ eklenip Sipariş Özeti'ne kadar ilerlendiğinde her
  # seferinde doğru şekilde TEK satır/299.90 TL görüntülendi. Kullanıcı
  # kararıyla senaryo DOĞRU/beklenen davranışı assert edecek şekilde
  # (şu an PASS veren, bug geri gelirse otomatik regresyon yakalayacak bir
  # test olarak) implemente edildi.
  #
  # TC-EACRML-014-13 NOTU: Canlı doğrulandı - sepete mükerrer ekleme ŞU AN
  # HİÇ ENGELLENMİYOR (2. ekleme ayrı bir satır olarak ekleniyor, toplam
  # 2 katına çıkıyor). Kullanıcı kararıyla KASITLI KIRMIZI olarak
  # implemente edildi - TC-014-08'in tarif ettiği "veri bütünlüğü" bug
  # sınıfıyla aynı kök nedene işaret ediyor olabilir.
  #
  # TC-EACRML-014-12 NOTU: "Alan yalnızca sayısal değer kabul eder" ifadesi
  # canlıda INPUT SEVİYESİNDE bir kısıtlama olarak doğrulanamadı (harf
  # yazılabiliyor, type="text"). Kullanıcı kararıyla İŞLEVSEL olarak
  # uyarlandı: harfli bir ID ile arama yapıldığında sonuç bulunamaz -
  # spec'in arkasındaki niyet (ID alanı sayısal eşleştirme içindir) hâlâ
  # doğrulanıyor, gerçek/çalışan davranışla uyumlu.

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
    Given sepette (Basket) en az bir ürün vardır
    When kullanıcı aynı ürünü tekrar "Sepete Ekle" ile eklemeyi dener
    Then sepete mükerrer bir kayıt eklenmez
    And Basket içeriği ve Total Amount değişmeden kalır

  Scenario: TC-EACRML-014-14 - Campaign sekmesinden kampanya seçilerek bağlı tüm ürünlerin sepete eklenmesi
    Given kullanıcı Campaign sekmesindedir
    When bir kampanya seçilip "Sepete Ekle" ile eklenir
    Then kampanya sepete eklenir
    And Total Amount kampanyanın indirimli fiyatını yansıtır
