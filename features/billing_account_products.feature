Feature: Fatura Hesabına Bağlı Ürün Detayları

  # NOT (canlı doğrulandı): "Hesap Ürünleri" paneli, hesap satırının
  # account-row-toggle'ına TIKLANARAK açılan bir şey DEĞİL - hesap
  # oluşturulduğunda VARSAYILAN OLARAK ZATEN AÇIK durumda geliyor
  # (aria-expanded="true"). Bu yüzden aşağıdaki senaryolarda ayrı bir
  # "genişlet" aksiyonuna gerek yok; 013-09 özel olarak tam tersini
  # (kapatma/tekrar açma) test ediyor.
  #
  # KAPSAM DIŞI BIRAKILAN 2 SENARYO (canlı bulgularla netleştirildi):
  #
  # TC-EACRML-013-02 (kampanya kapsamındaki bir ürünün kampanya adı/ID'si
  # ile görüntülenmesi): Satış kataloğundaki 11 teklifin HİÇBİRİ bir
  # kampanyaya bağlı değil (canlı doğrulandı - kampanya seçimi/etiketi
  # içeren tek bir akış yok), bu yüzden UI üzerinden kampanyalı bir ürün
  # OLUŞTURMANIN bir yolu yok. Kampanya alanlarının kendisi GERÇEK ve
  # doğru render ediliyor (bkz. 013-03) - eksik olan, bu alanı DOLU
  # olarak test edecek bir veri kurulum yolu. BA/dev'e iletilmesi
  # gereken bir madde: mock veride kampanyalı bir teklif/ürün olmalı.
  #
  # TC-EACRML-013-05 (kampanya kapsamındaki bir ürünün tek başına
  # silinmeye çalışılması): Bu senaryonun önkoşulu "silmenin mümkün
  # olduğu" varsayımına dayanıyordu. TC-013-04'te canlı olarak KESİN
  # kanıtlandı: Delete ikonu tıklaması HİÇBİR etkisi olmayan, tamamen
  # işlevsiz bir aksiyon (onay penceresi yok, satır sayısı/verisi
  # değişmiyor, reload sonrası da aynı). Kampanyalı olsun ya da olmasın
  # HİÇBİR ürün UI üzerinden silinemediğinden, "kampanya bütünlüğünün
  # korunması" senaryosu şu an anlamsız/test edilemez - TC-011-05'te
  # (durum değiştirme kontrolü, expand/collapse çıktı) yapılan aynı
  # karar: canlı davranışla çelişen senaryo suite'e alınmadı.

  Scenario: TC-EACRML-013-01 - Hesap altındaki ürün satırında View ile Ürün Teklif ID/Adı/Karakteristiklerinin görüntülenmesi
    Given kullanıcı bir fatura hesabı altındaki ürün listesini görüntülemektedir
    When kullanıcı bir ürünün View butonuna tıklar
    Then panel Ürün Teklif ID/Adı/Spec ID ve karakteristiklerini salt okunur şekilde gösterir

  Scenario: TC-EACRML-013-03 - Kampanyasız (tekil) alınan ürünlerde kampanya alanlarının "—" olarak görüntülenmesi
    Given hesap altındaki bir ürün kampanyasız alınmıştır
    When ürün listesi görüntülenir
    Then kampanya alanları "—" olarak görüntülenir

  Scenario: TC-EACRML-013-04 - Ürün detay tablosundaki Delete ikonunun görüntülenmesi ve işlevsiz olması
    Given kullanıcı ürün detay tablosunu görüntülemektedir
    Then her kayıt için bir Delete ikonu görüntülenir
    When kullanıcı bir ürünün Delete ikonuna tıklar
    Then herhangi bir işlem tetiklenmez, ürün verisi değişmeden kalır

  Scenario: TC-EACRML-013-06 - Ürün önizleme panelinin Close (Kapat) butonuyla kapatılabilmesi
    Given ürün önizleme paneli açıktır
    When Close butonuna tıklanır
    Then panel kapanıp ürün listesi görünümüne dönülür

  Scenario: TC-EACRML-013-07 - Bir hesap altında birden fazla ürünün aynı listede görüntülenmesi
    Given bir hesap altında birden fazla ürün vardır
    When ürün listesi görüntülenir
    Then tüm ürünler aynı tabloda ayrı satırlar olarak eksiksiz listelenir

  Scenario: TC-EACRML-013-08 - Fatura hesabına bağlı ürün bulunmadığında ürün detay tablosunun görüntülenmemesi
    Given seçilen fatura hesabına bağlı hiç ürün kaydı yoktur
    When kullanıcı hesap satırını görüntüler
    Then ürün detay tablosu görüntülenmez

  Scenario: TC-EACRML-013-09 - "Collapse" ikonuna tıklandığında ürün detay tablosunun gizlenmesi
    Given fatura hesabı satırı ve ürün detay tablosu görünür durumdadır
    When kullanıcı Collapse ikonuna tıklar
    Then ürün detay tablosu gizlenir
    And kullanıcı Expand ile tabloyu tekrar görüntüleyebilir

  Scenario: TC-EACRML-013-10 - Ürün detay tablosundaki her kayıt için View ikonunun görüntülenmesi
    Given fatura hesabı genişletilmiş ve bağlı ürünler listelenmiştir
    Then tablodaki her kayıt için bir View ikonu görüntülenir
