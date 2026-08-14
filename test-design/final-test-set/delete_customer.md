# UC-EACRML-005 — Müşteri Bilgilerini Silme — Konsolide Final Test Seti

## Durum Özeti

- Kaynak: kullanıcının orijinal senaryoları + doküman karşılaştırması (UC-005 analizi) + `features/delete_customer.feature`'daki mevcut, canlı doğrulanmış 6 senaryo + bu turda eklenen 1 yeni senaryo.
- Soft-delete/hard-delete belirsizliği daha önceki oturumda çözüldü: senaryolar artık implementasyon detayına (HTTP metodu, 204 vb.) değil, **gözlemlenebilir davranışa** (arama sonuçlarında görünmeme, eski URL'e gidildiğinde "bulunamadı" durumu) referans veriyor — bu yüzden hem soft-delete hem hard-delete ile uyumlu, kırılgan olmayan bir ifade tarzı.
- **Bu turda YENİ eklenen (canlı doğrulandı):** TC-EACRML-005-03 — dokümanın "kritik eksik iş kuralı" olarak işaretlediği "aktif ürünü olan müşteri silinemez" senaryosu, önceki oturumda güvenli test müşterisi hazırlamanın maliyeti nedeniyle ertelenmişti (bkz. `project_brain.txt`). Bu turda gerekli tüm page object'ler (fatura hesabı, Teklif Seçimi, Ürün Konfigürasyonu, Sipariş Gönder) artık mevcut olduğundan uçtan uca canlı olarak test edildi.
- **CANLI BULGU (kritik):** Fresh bir disposable müşteriye (ID 854) fatura hesabı açılıp gerçek bir sipariş akışıyla ("Mobil 20GB Paket") aktif ürün kazandırıldıktan sonra Delete + "Evet" denendi → **sistem silmeyi ENGELLEMEDİ**, müşteri normal şekilde silindi (arama ekranına yönlendirildi, eski URL artık açılmıyor). Bu, `bugsbunny.txt`'de zaten belgelenmiş olan TC-EACRML-012-03 (Fatura Hesabı seviyesinde aynı kural, "ortam/zaman kaynaklı tutarsızlık") ile aynı kök nedene işaret ediyor olabilir. Senaryo, TC-011-02/04, TC-012-03, TC-014-13 ile aynı proje kararıyla **spesifikasyonun doğru/beklenen davranışını assert edecek şekilde** yazıldı — şu an **kasıtlı kırmızı** (FAILED bekleniyor), kural düzeltilirse otomatik PASS'e dönüp regresyonu izleyecek bir test olarak suite'e alınmalı.

## Gherkin — Final Senaryo Seti

```gherkin
Feature: Müşteri Bilgilerini Silme

  Background:
    Given kullanıcı silinecek müşterinin Müşteri Bilgisi ekranındadır

  Scenario: TC-EACRML-005-01 - Müşteri Bilgisi ekranında Delete butonuna tıklandığında onay penceresinin görüntülenmesi
    When kullanıcı Delete ikonuna tıklar
    Then onay penceresi, silme mesajı ve Evet, Hayır butonlarıyla birlikte görüntülenir

  Scenario: TC-EACRML-005-04 - Onay penceresinde "Hayır" seçilince işlemin iptal edilip müşteri kaydının değişmeden kalması
    Given onay penceresi görüntülenmektedir
    When kullanıcı "Hayır" butonuna tıklar
    Then pencere kapanır
    And müşteri kaydı hiçbir şekilde değiştirilmeden ekranda kalmaya devam eder

  Scenario: TC-EACRML-005-07 - Onay penceresi açıkken ekranın diğer alanlarıyla etkileşimin engellenmesi (modal davranışı)
    Given onay penceresi görüntülenmektedir
    When kullanıcı arka plandaki herhangi bir alanla etkileşime girmeyi dener
    Then pencere modal davranışı gösterip arka planı engeller

  Scenario: TC-EACRML-005-02 - Onay Penceresinde "Evet" Seçilince Müşterinin Müşteri Arama Ekranına Yönlendirilmesi
    Given onay penceresi görüntülenmektedir
    When kullanıcı "Evet" butonuna tıklar
    Then kullanıcı Müşteri Arama ekranına yönlendirilir

  Scenario: TC-EACRML-005-05 - Silinen Müşterinin Arama Sonuçlarında Artık Görüntülenmemesi
    Given onay penceresi görüntülenmektedir
    When kullanıcı "Evet" butonuna tıklar
    Then silinen müşteri arama sonuçlarında artık görüntülenmez

  Scenario: TC-EACRML-005-06 - Silinen Müşterinin Detay Ekranına Doğrudan Erişilmeye Çalışılması
    Given onay penceresi görüntülenmektedir
    When kullanıcı "Evet" butonuna tıklar
    Then silinen müşterinin eski detay ekranına doğrudan gidildiğinde bir "bulunamadı" durumu görüntülenir

  Scenario: TC-EACRML-005-03 [YENİ] - Aktif ürünü olan müşterinin silinememesi
    # KASITLI KIRMIZI (canlı doğrulandı, bkz. Durum Özeti): sistem şu an bu
    # kuralı UYGULAMIYOR. Spesifikasyonun doğru davranışını izliyor;
    # bilinen defekt düzelene kadar FAILED kalması beklenen sonuçtur.
    Given görüntülenen müşteriye ait, bir fatura hesabına bağlı en az bir aktif ürün kaydı vardır
    When kullanıcı Delete ikonuna tıklayıp onay penceresinde "Evet"e basar
    Then sistem müşteriyi silmeyi reddedip ilgili uyarı/engelleme mesajını gösterir
    And kullanıcı Müşteri Bilgisi ekranında kalır, müşteri durumu "Aktif" olarak görüntülenmeye devam eder
```

## Notlar

- Demografik alan bazlı sınır değer (boundary value) senaryoları bu UC'nin kapsamında değil — bkz. `update_customer.md` (Ad/Soyad/Kimlik No) ve `create_customer.md` (Second/Father/Mother Name, Birth Date).
- TC-EACRML-005-03'ün otomasyona kalıcı olarak eklenmesi, fatura hesabı + tam satış akışı (Yeni Satış Başlat → Teklif Seçimi → Ürün Konfigürasyonu → Sipariş Gönder) gerektirdiğinden diğer senaryolardan daha ağır/yavaş çalışacaktır — isteğe bağlı olarak ayrı bir `@slow` marker ile işaretlenmesi değerlendirilebilir.
