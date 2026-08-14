# UC-EACRML 001–017 — Konsolide Final Test Seti (Gherkin/BDD)

**Rol:** Senior QA review — canlı doğrulama + INVEST'e uygun senaryo tasarımı
**Kapsam:** Repodaki **17 feature dosyasının tamamı** (UC-EACRML 001'den 017'ye — 13 ana UC + demografik alanları tamamlamak için 2 destek dosyası + login/arama)
**Yöntem:** `http://localhost:4200/login`'e gerçek bir Selenium oturumuyla giriş yapılıp (kullanıcı: `demo`/`Password123`), her feature'ın mevcut `.feature` dosyası, ilgili `pages/*.py` / `steps/*.py` implementasyonu ve projenin `project_brain.txt` / `bugsbunny.txt` günlükleri incelendi; hâlâ açık olan sorular (sınır değerler, TC-EACRML-005-03, login kilitlenme sınırı, arama ekranındaki hiç test edilmemiş sıralama/sayaç bileşenleri) canlı bir Selenium oturumuyla bizzat test edildi.

> **Revizyon notu:** İlk teslimatta `login.feature` ve `search_customers.feature` sehven dışarıda bırakılmıştı (yalnızca UC-EACRML-005–017 doküman karşılaştırmasına odaklanılmıştı). Kullanıcının "her feature için yap" talimatı hatırlatılınca bu iki dosya da aynı standartla eklendi — aşağıdaki liste artık **repodaki tüm `.feature` dosyalarını** kapsıyor.

## Neden bu dosyalar "final"?

Bu repo, orijinal 85 senaryo + doküman karşılaştırmasından bu yana çok sayıda oturumda canlı doğrulama ile zaten olgunlaştırılmış durumda (bkz. `project_brain.txt`, 4600+ satır). Bu tur iki şey yaptı:

1. **Konsolidasyon:** 13 UC'nin (005–017) her biri için, mevcut `.feature` dosyasındaki güncel/doğru hâli + doküman karşılaştırmasının hâlâ geçerli olan notlarını **tek bir okunabilir "final" belgede** birleştirdi (her UC kendi `.md` dosyasında).
2. **Boşluk kapama:** Hâlâ ele alınmamış senaryoları tespit edip canlı doğrulayarak ekledi — en kritik ikisi:
   - **TC-EACRML-005-03** (aktif ürünü olan müşteri silinemez) — önceki turda güvenli test kurulumu maliyeti nedeniyle ertelenmişti, bu tur uçtan uca (fatura hesabı + gerçek satış akışı) canlı test edildi.
   - **Sınır değer (boundary value) kontrolleri** — demografik bilgi, adres değerleri, iletişim bilgileri için üç ayrı kategori, kullanıcının bu turda özellikle istediği ekleme.

## Dosya Listesi

| Dosya | UC | Konu | Bu Turdaki Ana Değişiklik |
|---|---|---|---|
| [`login.md`](login.md) | 001 | Login | 4-deneme/kilitlenmeme sınır değeri eklendi (canlı doğrulandı) |
| [`search_customers.md`](search_customers.md) | 002 | Müşteri Arama | Sonuç sayısı/aralığı + sütun sıralama (hiç test edilmemiş) eklendi |
| [`create_customer.md`](create_customer.md) | 003 | Müşteri Oluşturma | Second/Father/Mother Name + Birth Date sınır değerleri eklendi |
| [`update_customer.md`](update_customer.md) | 004 | Müşteri Bilgilerini Güncelleme | Ad/Soyad tam-50 + Nationality ID 10/11/12 hane sınır değerleri eklendi |
| [`delete_customer.md`](delete_customer.md) | 005 | Müşteri Bilgilerini Silme | **TC-005-03 eklendi ve canlı test edildi → kasıtlı kırmızı (gerçek bug)** |
| [`address_update.md`](address_update.md) | 006 | Müşteri Adresinin Güncellenmesi | Sokak/Bina No sınır değer (üst sınır yok) eklendi |
| [`address_add.md`](address_add.md) | 007 | Yeni Müşteri Adresinin Eklenmesi | Değişiklik yok — zaten tam kapsanmış, sınır değer address_update'ten miras |
| [`address_delete.md`](address_delete.md) | 008 | Müşteri Adresinin Silinmesi | TC-008-04 ifadesi kesinleşmiş bulguya göre netleştirildi |
| [`contact_update.md`](contact_update.md) | 009 | Kontakt Bilgilerinin Güncellenmesi | Mobile Phone 9/10/11 hane + Email + Home/Fax sınır değerleri eklendi |
| [`billing_account_create.md`](billing_account_create.md) | 010 | Yeni Fatura Hesabı Oluşturma | Değişiklik yok — zaten tam kapsanmış |
| [`billing_account_update.md`](billing_account_update.md) | 011 | Fatura Hesabı Güncelleme | Değişiklik yok — bilinen adres-kalıcılık defekti (011-02/04) belgeli |
| [`billing_account_delete.md`](billing_account_delete.md) | 012 | Fatura Hesabını Silme | TC-005-03 bulgusuyla çapraz referanslandı (sistemik defekt) |
| [`billing_account_products.md`](billing_account_products.md) | 013 | Fatura Hesabına Bağlı Ürün Detayları | Değişiklik yok — kritik çelişki (Delete ikonu) zaten çözülmüş |
| [`offer_selection.md`](offer_selection.md) | 014 | Teklif Seçimi | Değişiklik yok — zaten canlı doğrulanmış |
| [`product_configuration.md`](product_configuration.md) | 015 | Ürün Konfigürasyonu | Değişiklik yok — zaten canlı doğrulanmış |
| [`order_submission.md`](order_submission.md) | 016 | Siparişin Tamamlanması | Değişiklik yok — zaten canlı doğrulanmış |
| [`language_support.md`](language_support.md) | 017 | Dil Desteği | Değişiklik yok — zaten canlı doğrulanmış |

**Toplam:** 17 dosya, ~155 senaryo (mevcut ~130 + bu turda eklenen ~25 yeni sınır-değer/TC-005-03/sıralama-sayaç senaryosu).

## Bu Turun En Kritik Bulguları

| # | Bulgu | Kanıt | Etki |
|---|---|---|---|
| 1 | 🔴 **Aktif ürünü/aboneliği olan bir müşteri, hiçbir engelleme olmadan silinebiliyor.** Fresh bir disposable müşteriye fatura hesabı + gerçek bir sipariş açılıp Delete + "Evet" denendi → engellenmeden silindi. | Bu turda canlı olarak `customers/854` üzerinde uçtan uca doğrulandı (bkz. `delete_customer.md`, TC-005-03). | Aynı kök nedenin fatura-hesabı seviyesindeki (TC-012-03, `bugsbunny.txt`) zaten bilinen tutarsızlığıyla birleşince, bu artık **tek seferlik bir flake değil, sistemik bir iş kuralı eksikliği** olarak okunmalı — BA/dev'e birlikte raporlanması önerilir. |
| 2 | 🟡 **Serbest metin alanlarında sistemik üst-karakter-sınırı eksikliği.** Açıklama, Hesap Adı (zaten biliniyordu) + bu turda **Sokak, Bina No, Email** de aynı kategoriye eklendi — hiçbirinde HTML `maxlength` yok. | Canlı DOM incelemesiyle doğrulandı (`address-street`, `address-building`, `new-contact-email` → `maxlength=None`). | 3 ayrı "defekt" yerine BA/dev'e **tek bir konsolide bulgu** olarak iletilmesi önerilir. |
| 3 | 🟢 **Gerçekten uygulanan sınır değerler netleşti.** Ad/Soyad=50, Second/Father/Mother Name=100, Identity Number=11, Birth Date mask=8 rakam, Mobile/Home/Fax Phone=10 — hepsi canlı DOM'dan okunarak doğrulandı, artık tahmine dayalı değil. | `pages/*.py` + bu turdaki canlı `maxlength` taraması. | Sınır-değer senaryoları artık gerçek uygulanan değerlere göre yazıldı (49/50/51 değil, gerçek sınırın kendisi + ±1). |
| 4 | 🟡 **Müşteri Arama ekranında geliştirilmiş ama hiç test edilmemiş 2 özellik bulundu:** sonuç sayısı/aralığı göstergesi ve tıklanabilir sütun sıralaması (5 sütun). İkisi de gerçek/çalışır durumda ama sıralama tıklaması `aria-sort` özniteliğini hiç güncellemiyor (a11y boşluğu). | Canlı doğrulandı: `customer-results-count`→"822 kayıt", sütun tıklaması sıra ve yönü gerçekten değiştiriyor. | `search_customers.md`'ye 2 yeni senaryo + a11y bulgusu eklendi. |
| 5 | 🟢 **Login'in 5-deneme kilitlenme kuralı erken tetiklenmiyor.** Tam 4 başarısız denemeden sonra doğru bilgilerle giriş güvenle başarılı oluyor. | Canlı doğrulandı, gerçek 15 dk'lık kilitlenmeyi TETİKLEMEDEN (yalnızca 4 deneme). | `login.md`'ye sınır-değer senaryosu olarak eklendi, varsayılan suite'e (lockout marker'sız) güvenle dahil edilebilir. |

## INVEST Uygulaması

- **Independent:** Her UC kendi `.md` dosyasında, kendi Background/Given'larıyla bağımsız çalışabilir durumda; paylaşılan bileşenler (adres formu, hesap adı alanı) için sınır değer testleri **tek bir yerde** tutulup diğer dosyalarda "Notlar" ile çapraz referanslandı (kör kopyalama yerine bilinçli DRY — INVEST'in "Independent"ı test edilebilirlik bağımsızlığı ister, kod-yolu tekrarı değil).
- **Negotiable:** Askıda/kapsam dışı bırakılan senaryolar (014-06/07, 015-06/07/08, 016-07, 013-02/05) her dosyada gerekçesiyle birlikte ayrı bir tabloda tutuldu — implementasyon detayına kilitlenmeden PM/BA onayına açık.
- **Valuable:** Yeni eklenen her senaryo ya bilinen bir riski (sınır değer, sistemik boşluk) ya da dokümanın kendi işaretlediği kritik bir iş kuralını (005-03) kapatıyor — "olsun diye" eklenen senaryo yok.
- **Estimable / Small:** Sınır değer senaryoları, projenin kendi kurduğu "a/b" ve Scenario Outline + Examples kalıbı korunarak tek-assertion'a yakın küçük parçalara bölündü (ör. 004-09/10/11/12 — dört ayrı, bağımsız çalıştırılabilir senaryo, tek bir dev "sınır değer" senaryosu değil).
- **Testable:** Tüm yeni senaryolar, projenin zaten kurduğu dil-bağımsız/yapısal doğrulama konvansiyonuna (literal metin yerine `maxlength`/hata-elementi görünürlüğü kontrolü) uygun yazıldı — mevcut page object'lerdeki yöntemlerle (`get_attribute("maxlength")`, `is_*_error_displayed()`) doğrudan otomatize edilebilir.

## Sonraki Adım (opsiyonel)

Bu dosyalar bir **test tasarım/dokümantasyon** teslimatıdır — `features/*.feature` dosyalarına veya `pages/`/`steps/`'e henüz dokunulmadı. İstenirse bir sonraki adımda:

1. Yeni sınır-değer senaryoları ilgili `.feature` dosyalarına eklenip `pages/`/`steps/` implementasyonları yazılabilir (çoğu, mevcut page object'lere `get_attribute("maxlength")` tabanlı 1-2 yeni metotla eklenebilir — DOM sınırları zaten bu turda keşfedildi).
2. TC-EACRML-005-03, bu turdaki keşif script'inde kullanılan aynı page object zincirinden (`CreateCustomerPage` → `BillingAccountProductsPage` → `SalesSetupPage` → `DeleteCustomerPage`) yararlanılarak doğrudan `test_delete_customer_steps.py`'ye taşınabilir.
