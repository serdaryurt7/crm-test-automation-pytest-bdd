Feature: Fatura Hesabına Bağlı Ürün Detayları

  Scenario: TC-EACRML-013-01 - Hesap altındaki ürün satırında View ile Ürün Teklif ID/Adı/Karakteristiklerinin görüntülenmesi
    Given kullanıcı bir fatura hesabı altındaki ürün listesini görüntülemektedir
    When kullanıcı bir ürünün View butonuna tıklar
    Then panel Ürün Teklif ID, Adı, Spec ID ve karakteristiklerini salt okunur şekilde gösterir

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
