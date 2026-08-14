# UC-EACRML-013 — Fatura Hesabına Bağlı Ürün Detayları — Konsolide Final Test Seti

## Durum Özeti

- Kaynak: kullanıcının 10 senaryolu spesifikasyonu + `features/billing_account_products.feature`'daki 8 canlı doğrulanmış senaryo. Dokümanın kendisi zaten 013-02/013-04/013-05'i "teyit edilmeli/çelişkili/askıda" olarak işaretlemişti.
- **EN KRİTİK madde (doküman öncelik #1) kapandı:** TC-013-04 — Delete ikonu **kesin olarak işlevsiz**: tıklama hiçbir gözlemlenebilir etki yaratmıyor (onay penceresi yok, satır sayısı/verisi değişmiyor, reload sonrası da aynı). Senin orijinal "ürün silinir" (Positive) senaryon, dokümanın "kasıtlı işlevsiz" bulgusuyla doğrulandı — dokümanın tarafı doğru çıktı. Senaryo işlevsiz-davranışı doğrulayan bir teste dönüştürüldü.
- TC-013-05, TC-013-04'ün önkoşuluyla (silmenin mümkün olduğu) birlikte anlamsızlaştığından suite'e alınmadı (moot).
- **TC-013-02/03 (kampanya alanları) için önemli bir takip notu:** Katalog sekmesindeki 11 teklifin hiçbiri kampanyaya bağlı değil, ama UC-014 keşfinde Kampanya sekmesinde 3 GERÇEK çoklu-ürün kampanya paketi bulundu. Bu, TC-013-02'nin bir kampanya sekmesinden satın alma ile otomasyona alınabileceğini gösteriyor — kapsam dışına kendiliğinden genişletilmedi, ayrı onay gerektiriyor (bkz. Notlar).

## Gherkin — Final Senaryo Seti

```gherkin
Feature: Fatura Hesabına Bağlı Ürün Detayları

  # "Hesap Ürünleri" paneli, hesap oluşturulduğunda VARSAYILAN OLARAK ZATEN
  # AÇIK geliyor (aria-expanded="true") - ayrı bir "genişlet" aksiyonuna
  # gerek yok; 013-09 özel olarak tam tersini (kapatma/tekrar açma) test
  # ediyor.

  Scenario: TC-EACRML-013-01 - Hesap altındaki ürün satırında View ile Ürün Teklif ID/Adı/Karakteristiklerinin görüntülenmesi
    Given kullanıcı bir fatura hesabı altındaki ürün listesini görüntülemektedir
    When kullanıcı bir ürünün View butonuna tıklar
    Then panel Ürün Teklif ID/Adı/Spec ID ve karakteristiklerini salt okunur şekilde gösterir

  Scenario: TC-EACRML-013-03 - Kampanyasız (tekil) alınan ürünlerde kampanya alanlarının "—" olarak görüntülenmesi
    Given hesap altındaki bir ürün kampanyasız alınmıştır
    When ürün listesi görüntülenir
    Then kampanya alanları "—" olarak görüntülenir

  Scenario: TC-EACRML-013-04 [ÇÖZÜLDÜ] - Ürün detay tablosundaki Delete ikonunun görüntülenmesi ve işlevsiz olması
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
```

## Kapsam Dışı / Askıda Kalanlar

| TC ID | Durum | Gerekçe |
|---|---|---|
| TC-EACRML-013-02 (kampanyalı üründe kampanya adı/ID görüntülenmesi) | Kapsam dışı, takip notlu | Katalog sekmesindeki 11 teklifin hiçbiri kampanyaya bağlı değil — UI'dan kampanyalı ürün oluşturmanın yolu yok. **Ancak** UC-014'te Kampanya sekmesinden gerçek kampanya paketleri bulundu; bu senaryonun oradan otomasyona alınabileceği PM/BA'ya iletilmesi önerilen bir bulgu. |
| TC-EACRML-013-05 (kampanyalı ürünün tekil silinmeye çalışılması) | Moot / kapsam dışı | TC-013-04 ile önkoşulu ("silme mümkün") geçersizleşti — hiçbir ürün UI'dan silinemediğinden kampanyalı olsun olmasın fark etmiyor. |

## Notlar

- Sınır değer kontrolleri bu UC'nin kapsamında değil (görüntüleme/silme akışı, alan girişi yok).
