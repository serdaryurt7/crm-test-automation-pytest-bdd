# UC-EACRML-005 — Müşteri Bilgilerini Silme — Konsolide Final Test Seti

## Durum Özeti

- Kaynak: kullanıcının orijinal senaryoları + doküman karşılaştırması (UC-005 analizi) + `features/delete_customer.feature`'daki mevcut, canlı doğrulanmış 6 senaryo + bu turda eklenen 1 yeni senaryo.
- Soft-delete/hard-delete belirsizliği daha önceki oturumda çözüldü: senaryolar artık implementasyon detayına (HTTP metodu, 204 vb.) değil, **gözlemlenebilir davranışa** (arama sonuçlarında görünmeme, eski URL'e gidildiğinde "bulunamadı" durumu) referans veriyor — bu yüzden hem soft-delete hem hard-delete ile uyumlu, kırılgan olmayan bir ifade tarzı.
- **[İMPLEMENTE EDİLDİ] TC-EACRML-005-03** — dokümanın "kritik eksik iş kuralı" olarak işaretlediği "aktif ürünü olan müşteri silinemez" senaryosu, `features/delete_customer.feature`'a eklendi. Kurulum, `billing_account_delete_page.py`'deki TC-012-03 için zaten kanıtlanmış minimal satın alma desenini (fatura hesabı → "Yeni Satış Başlat" → `SalesSetupPage.purchase_simple_offer()`) Background'ın oluşturduğu müşterinin ÜZERİNE inşa ederek yeniden kullanıyor (ekstra müşteri oluşturmadan, INVEST/Estimable).
- **CANLI BULGU (kritik, doğrulandı):** İzole pytest çalıştırmasında **AssertionError ile FAILED** — sistem müşteriyi silmeyi ENGELLEMEDİ, Müşteri Arama ekranına yönlendirdi. Bu, `bugsbunny.txt`'de zaten belgelenmiş TC-EACRML-012-03 (Fatura Hesabı seviyesinde aynı kural) ile aynı kök nedene işaret ediyor. Senaryo, TC-011-02/04, TC-012-03, TC-014-13 ile aynı proje kararıyla spesifikasyonun doğru/beklenen davranışını assert ediyor — **kasıtlı kırmızı**, kural düzeltilirse otomatik PASS'e dönüp regresyonu izleyecek.
- **Kendi kendini düzelten bir uygulama hatası (izleme değeri var):** İlk implementasyon denemesi "silme reddedildi mi" kontrolünü `current_url hâlâ aynı mı` şeklinde DOĞRUDAN bir `wait.until` ile yapıyordu — bu, silme isteği asenkron işlenirken yönlendirme henüz BAŞLAMADAN önceki ilk polling anında yanlışlıkla "değişmedi" görüp **sahte-PASS** üretti (ilk izole çalıştırmada test PASSED çıktı — yanıltıcıydı). Kök neden fark edilip zaten kanıtlanmış `wait_for_redirect_to_search()` (tam 10sn) metoduna devredilerek düzeltildi: yönlendirme GERÇEKTEN olursa bilinçli bir `AssertionError`'a çevriliyor. Düzeltme sonrası doğru/beklenen FAILED sonucu elde edildi — bkz. `bugsbunny.txt` madde 17.
- **[GÜNCELLEME] Tek senaryo, TR/EN'i AYNI ANDA destekleyecek şekilde güçlendirildi:** Akış artık kasıtlı olarak arayüz dilini İngilizce'ye çevirip (`LanguageSwitcherPage`) öyle devam ediyor - bu, Then adımlarının GERÇEKTEN literal Türkçe metne bağımlı olmadığının pratik kanıtı (bağımlı olsaydı bu çalıştırma kırılırdı). "Müşteri durumu değişmeden kalır" kontrolü de aynı gerekçeyle `"Aktif"` gibi hardcoded bir değerle değil, silme denemesinden HEMEN ÖNCE (o an aktif dilde) alınan bir anlık görüntüyle karşılaştırılıyor (`capture_status_snapshot` / `is_still_on_customer_info_with_status_unchanged`). Yeniden doğrulama: **İngilizce arayüzde de AYNI `AssertionError` ile FAILED** — kural eksikliğinin TR'ye özgü bir tuhaflık olmadığını, dilden bağımsız olarak var olduğunu ek olarak kanıtlıyor.

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

  # KASITLI KIRMIZI (canlı doğrulandı, bkz. Durum Özeti / bugsbunny.txt
  # madde 17): sistem şu an bu kuralı UYGULAMIYOR. Spesifikasyonun doğru
  # davranışını izliyor; bilinen defekt düzelene kadar FAILED kalması
  # beklenen sonuçtur.
  #
  # DİLDEN BAĞIMSIZ (tek senaryo, TR/EN'i AYNI anda destekler): Then
  # adımlarının hiçbiri literal metin karşılaştırmıyor (yapısal - URL/durum
  # kontrolü). Bunu pratikte kanıtlamak için akış BİLEREK arayüz dili
  # İngilizce'ye çevrilmiş şekilde çalıştırılıyor - kontrol gizliden
  # Türkçe metne bağımlı olsaydı bu EN çalıştırmada kırılırdı. Aynı
  # mekanizma varsayılan (TR) dilde de değişmeden çalışır.
  Scenario: TC-EACRML-005-03 - Aktif ürünü olan müşterinin silinememesi
    Given görüntülenen müşteriye ait, bir fatura hesabına bağlı en az bir aktif ürün kaydı vardır
    And kullanıcı arayüz dilini İngilizce olarak ayarlamıştır
    When kullanıcı Delete ikonuna tıklar
    And kullanıcı "Evet" butonuna tıklar
    Then sistem müşteriyi silmeyi reddeder
    And kullanıcı Müşteri Bilgisi ekranında kalır, müşteri durumu değişmeden kalır
```

## Notlar

- Demografik alan bazlı sınır değer (boundary value) senaryoları bu UC'nin kapsamında değil — bkz. `update_customer.md` (Ad/Soyad/Kimlik No) ve `create_customer.md` (Second/Father/Mother Name, Birth Date).
- TC-EACRML-005-03, fatura hesabı + tam satış akışı (Yeni Satış Başlat → Teklif Seçimi → Ürün Konfigürasyonu → Sipariş Gönder) gerektirdiğinden diğer senaryolardan daha ağır/yavaş çalışıyor (~35-45sn, izole ölçüldü) — isteğe bağlı olarak ayrı bir `@slow` marker ile işaretlenmesi değerlendirilebilir.
- **Bu test kasıtlı olarak KIRMIZI kalacak şekilde tasarlandı** — tam suite koşumlarında bu FAILED'i "gerçek bir regresyon" sanıp gereksiz yere araştırmayın; `bugsbunny.txt` madde 17'de zaten belgelendi. Kural düzeltildiğinde otomatik olarak PASS'e dönecektir.
