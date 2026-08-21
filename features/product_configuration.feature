Feature: Ürün Konfigürasyonu

  Scenario: TC-EACRML-015-01 - Sepetteki her teklif için ayrı bir konfigürasyon kartının görüntülenmesi
    Given kullanıcı sepete birden fazla teklif ekleyip İleri ile Ürün Konfigürasyonu ekranına geçmiştir
    Then sepetteki her teklif için Ürün Teklif ID, Adı ile ayrı bir konfigürasyon kartı görüntülenir

  Scenario: TC-EACRML-015-02 - Zorunlu konfigürasyon alanları boşken "İleri" butonunun pasif kalması
    Given kullanıcı Ürün Konfigürasyonu ekranındadır
    When zorunlu konfigürasyon alanları boş bırakılır
    Then İleri butonu pasif kalır

  Scenario: TC-EACRML-015-03 - Konfigürasyon ekranında hizmet adresi olarak müşterinin kayıtlı adreslerinden birinin seçilmesi
    Given kullanıcının birden fazla kayıtlı adresi olduğu Ürün Konfigürasyonu ekranındadır
    When müşterinin kayıtlı adreslerinden biri hizmet adresi olarak seçilir
    Then seçim işaretli olarak görüntülenir

  Scenario: TC-EACRML-015-04 - "Yeni Adres Ekle" ile konfigürasyon sırasında yeni bir hizmet adresinin eklenip seçilebilmesi
    Given kullanıcı Ürün Konfigürasyonu ekranındadır
    When "Yeni Adres Ekle" ile yeni bir hizmet adresi eklenir
    Then yeni adres seçili olarak listeye eklenir

  Scenario: TC-EACRML-015-05 - "Geri" butonuyla Teklif Seçimi ekranına dönüldüğünde sepetin ve girilen değerlerin korunması
    Given kullanıcı Ürün Konfigürasyonu ekranında konfigürasyon alanlarını doldurmuştur
    When "Geri" butonuna tıklanır
    Then Teklif Seçimi ekranına dönülür ve sepet korunur
    When kullanıcı tekrar İleri butonuna tıklar
    Then daha önce girilmiş teknik konfigürasyon değerleri korunmuş olarak görüntülenir

  Scenario: TC-EACRML-015-09 - Tüm zorunlu alanlar doldurulduğunda "İleri" butonunun aktif hale gelip Sipariş Özetine geçilmesi
    Given tüm zorunlu konfigürasyon alanları doldurulmuştur
    When İleri butonuna tıklanır
    Then Sipariş Özeti ekranına geçilir
