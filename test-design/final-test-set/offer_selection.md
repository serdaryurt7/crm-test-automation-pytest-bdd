# UC-EACRML-014 — Teklif Seçimi — Konsolide Final Test Seti

## Durum Özeti

- Kaynak: `features/offer_selection.feature`'daki 12 canlı doğrulanmış senaryo.
- **014-08 [DEFEKT ADAYI] netleşti:** kullanıcının işaretlediği "teklif 3 kez tekrarlanıp 899.70 TL çıkıyor" iddiası, 3 ayrı canlı denemede DE yeniden üretilemedi — teklif her seferinde doğru şekilde tek satır/299.90 TL. Senaryo, doğru/beklenen davranışı assert edecek şekilde (şu an PASS veren bir regresyon-guard'ı olarak) yazıldı.
- **014-13 canlı KESİN olarak doğrulanan gerçek bir bug:** sepete mükerrer ekleme şu an hiç engellenmiyor (aynı teklif 2. kez eklenince ayrı satır oluşuyor, toplam 2 katına çıkıyor). Kasıtlı kırmızı test — 014-08'in tarif ettiği "veri bütünlüğü" bug sınıfının farklı bir tezahürü olabilir.
- **014-12 uyarlandı:** "Teklif ID yalnızca sayısal kabul eder" iddiası input-seviyesinde YANLIŞ (alan `type="text"`, harf yazılabiliyor) — ama harfli bir ID hiçbir teklifle eşleşmediğinden her zaman "sonuç bulunamadı" dönüyor. İşlevsel/yapısal olarak uyarlandı, input-seviyesi kısıtlama iddia edilmiyor.
- **014-14 zaten `features/offer_selection.feature`'da mevcut** (bu turda BEN eklemedim — önceki bir oturumda, orijinal analiz dokümanında hiç geçmediği için canlı keşifle eklenmişti). Kampanya sekmesinde 3 gerçek çoklu-ürün kampanya paketi bulundu; kampanya sepete eklendiğinde ürün başına ayrı satırlar değil, kampanyayı temsil eden TEK bir indirimli sepet satırı oluşuyor.
- **014-06/014-07 (tamamlayıcı ürün önerisi / çapraz satış) kapsam dışı bırakıldı** — dokümanın 8 UC-014 test case'inde bu özelliklerden hiç bahsedilmiyor, PM/BA onayı bekleniyor.

## Gherkin — Final Senaryo Seti

```gherkin
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

  Scenario: TC-EACRML-014-08 [DEFEKT ADAYI - yeniden üretilemedi] - Sepete yalnızca bir kez eklenen teklifin sipariş özetinde de tam bir kez görüntülenmesi
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

  Scenario: TC-EACRML-014-12 [UYARLANDI] - Teklif ID filtresine harf girilip arandığında sonuç bulunamaması
    Given kullanıcı Teklif Seçimi ekranındadır
    When Teklif ID filtresine harf girilip Ara'ya tıklanır
    Then sonuç bulunamadı durumu görüntülenir

  Scenario: TC-EACRML-014-13 [DEFEKT - kasıtlı kırmızı] - Sepette zaten bulunan bir ürünün tekrar eklenmeye çalışılmasının engellenmesi
    Given sepette (Basket) en az bir ürün vardır
    When kullanıcı aynı ürünü tekrar "Sepete Ekle" ile eklemeyi dener
    Then sepete mükerrer bir kayıt eklenmez
    And Basket içeriği ve Total Amount değişmeden kalır

  Scenario: TC-EACRML-014-14 - Campaign sekmesinden kampanya seçilerek bağlı tüm ürünlerin sepete eklenmesi
    Given kullanıcı Campaign sekmesindedir
    When bir kampanya seçilip "Sepete Ekle" ile eklenir
    Then kampanya sepete eklenir
    And Total Amount kampanyanın indirimli fiyatını yansıtır
```

## Kapsam Dışı / Askıda Kalanlar

| TC ID | Durum | Gerekçe |
|---|---|---|
| TC-EACRML-014-06 (tamamlayıcı ürün önerisi uyarısı) | Askıda — PM/BA onayı bekliyor | Dokümanın 8 test case'inde hiç geçmiyor, var olmayan bir özelliği test etmeye çalışmak false-fail üretir. |
| TC-EACRML-014-07 ("Birlikte alınması önerilenler" çapraz satış) | Askıda — PM/BA onayı bekliyor | Aynı gerekçe. |

## Notlar

- Sınır değer kontrolleri bu UC'nin kapsamında değil (teklif/sepet akışı, serbest metin alanı yok — Teklif ID/Adı filtreleri arama amaçlı, format değil boundary testi 014-12'de zaten kapsanıyor).
