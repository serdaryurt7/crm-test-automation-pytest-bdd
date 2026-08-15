# Mimari Değerlendirme ve Yol Haritası

**Proje:** CRM Test Automation Framework (Selenium + pytest-bdd)
**İlk değerlendirme:** 2026-08-15
**Son güncelleme:** 2026-08-15 — Faz 1 tamamlandı
**Değerlendiren:** Senior Test Otomasyon Mühendisi
**Kapsam:** Tüm proje yapısı — katman tasarımı, kod tekrarı, konfigürasyon, raporlama, repo hijyeni, CI/CD

> **Bu dosya canlıdır.** Her faz tamamlandığında skorlar ve ölçütler
> güncellenir. Güncel ilerleme için §0'a bakınız.

---

## 0. İlerleme Durumu

**Genel olgunluk: 3.8 → 4.7 / 10**
**Page Object Model: 6 → 9 / 10** ✅ &nbsp;·&nbsp; **Step katmanı: 3 → 5 / 10** ✅

| Faz | Kapsam | Durum |
|---|---|---|
| **Faz 0** | Branch + baseline doğrulama | ✅ Tamam |
| **Faz 1** | `BasePage` + 13 kök sınıf migrasyonu | ✅ Tamam (`ecf6251`) |
| **Faz 2** | `utils/waits.py` + poll döngülerinin taşınması | ✅ Tamam (`96a9a65`, kapsam daraltıldı) |
| **Faz 3** | Page içindeki assert'lerin ayıklanması (11 → 6) | ✅ Tamam (`e7d260c`) |
| Faz 4 | `create_customer_page.py` bölünmesi (735 satır) | ⏳ Ayrı karar |
| **Faz A+B** | `utils/config.py` + `steps/conftest.py::authenticated_driver` | ✅ Tamam (`FAZ_AB_COMMIT`) |
| Faz C | `new_customer` factory fixture (sihirbaz tekrarı, ~210 satır) | ⏳ Sırada |
| Faz D | `utils/test_data.py` (7 ayrı Faker örneği) | ⏳ Bekliyor |
| Faz E | Step'lerdeki ham `By`/`WebDriverWait` (opsiyonel) | ⏳ Risk/getiri zayıf |

### Faz 0 — Yapılanlar

- `refactor/pom-base-page` branch'i açıldı; `main` temiz ve push'lu bırakıldı.
- Bilinen-kırmızı listesi `bugsbunnyupdated.txt`'ten çıkarıldı:
  **6 kasıtlı kırmızı + 4 flaky = 10** (baseline: 204 passed / 10 failed).
- Kanarya koşumu (`billing_account_update`, 5 senaryo) ile listenin bugün
  hâlâ geçerli olduğu doğrulandı: **3 passed / 2 failed**, ikisi de bilinen.

> **Ortam notu:** Bu doğrulama sırasında `bff-service`'in ayakta olmadığı
> tespit edildi. Belirti yanıltıcıydı — frontend (4200) ve Keycloak (8180)
> sağlıklı, gateway (8080) `/actuator/health` → `UP` dönüyordu; ancak
> `POST /bff-service/api/v1/auth/login` bir devre kesici fallback'i
> veriyordu:
> `{"instance":"/fallback/bff-service","service":"bff-service","status":503}`
> Testler değil, hedef sistem eksikti. Servis ayağa kalkınca baseline
> doğrulandı.

### Faz 1 — Yapılanlar

`pages/base_page.py` oluşturuldu ve **13 kök sınıfın tamamı** ona bağlandı
(kalıtım zinciriyle birlikte **18/18 page sınıfı**).

Değişiklik her sınıfta bilinçli olarak minimal tutuldu: sayfaya özel
hazır-olma beklemeleri ve durum alanları `__init__` içinde **aynen
korundu**, yalnızca ortak iki satır `super().__init__(driver)` ile
değiştirildi. İki sayfada (`language_switcher`, `sales_setup`) `__init__`
zaten ortak kısımdan ibaret olduğu için tamamen kaldırıldı.

`poll_frequency` bilerek Selenium varsayılanında (0.5sn) bırakıldı —
bu bir **refactor**'dır: yapı değişir, davranış değişmez. Ölçülmemiş bir
zamanlama değişikliği, olası bir regresyonu ayırt etmeyi zorlaştırırdı.

**Doğrulama:** 214 senaryo üç partide koşuldu.

| Parti | Kapsam | Sonuç |
|---|---|---|
| Parti 1 | `language_switcher`, `login`, `sales_setup` | 34 passed / 2 failed |
| Parti 2 | `offer_selection`, `order_submission`, `product_configuration`, `delete_customer`, `update_customer` | 46 passed / 2 failed |
| Parti 3 | `contact_update`, `address_update`, `billing_account_create`, `create_customer`, `search_customers` (+5 alt sınıf) | 131 passed / 5 failed |

**Benzersiz 8 kırmızı; hepsi bilinen listede.** `BasePage` kaynaklı
regresyon YOK. Baseline'daki 10 kırmızıdan 8'e düşüş, üç flaky testin
(`TC-014-12`, `TC-007-05`, login butonu pasifleşmesi) bu koşumlarda
geçmesinden kaynaklandı.

> **Dürüstlük notu:** `TC-014-12`'nin geçmesi umut verici — bu testin
> bilinen kök nedeni `offer_selection_page`'de eksik olan
> `ignored_exceptions`'tı ve `BasePage` bunu getirdi. Ancak **tek yeşil
> koşum bir flaky'nin düzeldiğini kanıtlamaz.** Kesin yargı için birkaç
> tam süit koşumu gerekiyor.

### Faz 1 — Ölçülen sonuç

| Ölçüt | Önce | Sonra |
|---|---|---|
| Elle `WebDriverWait` kuran sayfa | 11 | **0** |
| `BasePage` alt sınıfı | 0 / 18 | **18 / 18** |
| `ignored_exceptions` korumalı sayfa | 2 / 13 | **13 / 13** |
| Zaman aşımı yönetim noktası | 11 dosya | **1 ortam değişkeni** |
| Ortak yardımcı metot | 0 | **20** |

### Faz 2 — Yapılanlar

`utils/waits.py` oluşturuldu; `utils/` modül sayısı 1 → 2.

| Fonksiyon | Amaç | Durum |
|---|---|---|
| `poll_until()` | "eylem → bekle → kontrol" turunu tekrarlar; asenkron backend işlemleri için | Kullanımda (2 yer) |
| `wait_for_dom_settled()` | MutationObserver ile DOM durulmasını bekler | Yazıldı, **henüz kullanılmıyor** |

`delete_customer_page.py` ve `search_customers_page.py` içindeki elle
yazılmış poll döngüleri `poll_until()`'e taşındı; iki dosyadan ölü
`import time` temizlendi.

`poll_until()` bilerek **exception fırlatmıyor**, `True`/`False` döndürüyor —
çağıran sayfa metotları bu sonucu aynen döndürüp iddiayı step katmanına
bırakıyordu; `TimeoutException` fırlatmak test başarısızlık mesajlarını
değiştirir ve refactor'u davranış değişikliğine dönüştürürdü.

**Doğrulama:** `delete_customer` + `search_customers` → **40 passed / 1 failed**
(7dk 34sn). Tek kırmızı TC-005-03, bilinen kasıtlı kırmızı. Taşınan
metotları kullanan TC-005-05 ve TC-005-06 **geçti**. Sıfır regresyon.

### Faz 2 — Kapsam neden daraltıldı

İlk plan "6 `time.sleep`'i `poll_until`'e taşı" idi. İnceleme bu planın
yanlış bir sayıma dayandığını gösterdi (bkz. §4.2c): gerçek sayı 5'ti,
biri yorum satırıydı ve **3'ü poll döngüsü değildi**.

Kalan 3 sabit bekleme için çözüm (`wait_for_dom_settled`) yazıldı ama
uygulanmadı — ayrıntılı gerekçe §4.2c'de. Özet: en sıcak kod yolunda,
kazanç ancak CI'da görünür, bugün çalışıyorlar.

### Faz 3 — Yapılanlar

Page object içindeki 11 assert kategorize edildi; yalnızca **gerçek POM
ihlali olan 5 tanesi** step katmanına taşındı (ayrıntılı kategorizasyon
ve kalan 6'nın gerekçesi için §4.2b).

Etkilenen: `search_customers_page.py` + `test_search_customers_steps.py`.
Üç `verify_*` metodu, durum döndüren `get_*` metotlarına dönüştürüldü;
beklemeler page katmanında bırakıldı.

**Doğrulama:** `search_customers` → **34 passed / 0 failed** (5dk 40sn).
Bu feature'da bilinen kırmızı yok, dolayısıyla tam yeşil beklenen sonuçtu.
Sıfır regresyon.

**Sonuç: page içinde assert 11 → 6.** Kalan 6 POM ihlali değil:
3'ü ayrıştırma guard'ı, 3'ü beklemenin kapsamadığı ikinci bir doğrulama.

### Faz A+B — Yapılanlar (step katmanı, 1. dalga)

Skor gerekçesindeki üç şikâyetten ikisi kapatıldı: *sabit kodlanmış veri*
ve *sıfır paylaşılan fixture*. Üçüncüsü (*ağır tekrar*) kısmen — sihirbaz
tekrarı Faz C'ye kaldı.

**Yeni dosyalar**

| Dosya | Satır | İçerik |
|---|---|---|
| `utils/config.py` | 40 | `USERNAME`, `PASSWORD`, `APP_ORIGIN`, `url()` |
| `steps/conftest.py` | 34 | `credentials`, `authenticated_driver` fixture'ları |

`steps/conftest.py`'nin varlığı başlı başına bir dönüm noktası: pytest-bdd
step tanımlarını ve fixture'ları normal pytest kurallarıyla çözer, yani bu
mekanizma en baştan mevcuttu ama proje hiç kullanmamıştı.

**Ölçülen sonuç**

| Ölçüt | Önce | Sonra |
|---|---|---|
| `steps/` satır sayısı | 3879 | **3756** (−123) |
| Kopyalanmış login bloğu | 16 dosya | **0** |
| `urlparse` ile origin hesabı | 14 dosya | **0** |
| Sabit kodlanmış `demo`/`Password123` | 17 satır | **0** |
| Ölü import | — | 28 silindi |
| Paylaşılan fixture kullanan dosya | 0 | **16** |

**Doğrulama:** `--collect-only` → **214 test** (temel çizgiyle birebir,
senaryo kaybı yok). Kanarya 4/4 (50sn). Tam suite → **203 passed /
11 failed** (58dk 02sn).

11 başarısızlığın dağılımı: **7 bilinen kasıtlı kırmızı + 2 bilinen flaky
+ 2 YENİ flaky**. Yeni ikisi izole koşumda PASSED verdi ve
`bugsbunny.txt` madde 18-19 olarak kayda geçti. **Regresyon tespit
edilmedi.**

> **Dürüstlük payı:** yeni flaky'lerden biri (`update_customer` TC-004-07
> [Soyad]) yığın izinde `steps/conftest.py:28`'i, yani bu fazda eklenen
> fixture'ı gösteriyor. Hata, login formunun 10sn içinde görünmemesi —
> fixture, eskiden 16 dosyada tekrarlanan **aynı çağrıyı aynı zaman
> aşımıyla** yapıyor; refactor çağrının yerini değiştirdi, içeriğini
> değil. Aynı senaryonun `[Ad]` parametreli kardeşi aynı koşumda geçti ve
> izole koşumda ikisi de geçiyor. Yine de, "fixture'la ilgisi yok" demek
> yerine bunu açıkça izleme listesine aldım: tekrarlarsa ilk müdahale
> `DEFAULT_TIMEOUT`'u yükseltmek olmalı (Faz 1 sayesinde tek ortam
> değişkeni).

**Bilinçli davranış değişikliği:** uygulama origin'i artık canlı
`driver.current_url` yerine yapılandırmadan deterministik olarak
türetiliyor. Eski davranış bir tasarım tercihi değildi — `.env`'deki
`BASE_URL`'in login yolunu da içermesinin (`…:4200/login`) yan etkisiydi
ve 14 dosyayı `urlparse` yapmaya zorluyordu. `utils/config.py` içinde
gerekçesiyle belgelendi.

**Bilinçli olarak DOKUNULMAYANLAR**

- `test_login_steps.py` — giriş akışının **kendisini** test ediyor,
  adımların açık kalması gerekir.
- `language_support`'taki logout → yeniden giriş adımı — senaryonun konusu
  bu; yalnızca kimlik bilgileri `config`'e bağlandı.
- `lockout` senaryosundaki `admin-crm` / `Password123` literalleri —
  bunlar paylaşılan yapılandırma değil, **`demo` hesabı kilitlenmesin diye
  kasten seçilmiş ayrı bir hesabın** test verisi.

### Faz 1 — Bilinçli olarak YAPILMAYAN

`BasePage`'in 20 yardımcı metodu (`find`, `click`, `type`, `text_of`,
`wait_until_gone` …) şu an **hiçbir sayfa tarafından kullanılmıyor**;
sayfalar hâlâ kendi `self.driver.find_element(...)` çağrılarını yapıyor.
Bu, Faz 1'in "davranış değişmez" sözleşmesinin gereğiydi. Yardımcıları
benimsetmek ayrı ve daha riskli bir iştir; ayrı bir faz olarak ele
alınmalıdır. Şu anki değerleri, **yeni yazılacak sayfaların bu mantığı
yeniden üretmek zorunda kalmaması**.

---

## 1. Yönetici Özeti

Bu framework **çalışan ve gerçek değer üreten** bir yapı. 17 feature dosyası, 187 senaryo,
18 page object ve 17 step modülü ile ciddi bir kapsam oluşturulmuş. Page Object Model doğru
anlaşılmış, `data-testid` tabanlı locator stratejisi disiplinli uygulanmış, dil bağımsızlığı
bilinçli bir tasarım kararı olarak ele alınmış ve dinamik bekleme (WebDriverWait) kuralı
büyük ölçüde korunmuş. Bunlar önemsiz başarılar değil.

Ancak framework şu anda **"çalışıyor" olgunluğunda, "ölçeklenebilir" olgunluğunda değil.**
Temel sorun tek bir cümleyle özetlenebilir:

> **Ortak davranışlar için bir soyutlama katmanı yok; bu yüzden her yeni feature,
> mevcut kodun kopyalanmasıyla ekleniyor.**

Bunun ölçülebilir kanıtı:

| Tekrar eden davranış | Kaç dosyada tekrarlanıyor |
|---|---|
| Login akışı (`LoginPage` + `login("demo","Password123")`) | **17 / 17 step dosyası** |
| Sabit kodlanmış şifre `Password123` | **18 kez** |
| Tek kullanımlık (disposable) müşteri oluşturma bloğu | **14 step dosyası** |
| `urlparse` ile origin yeniden kurma | **14 step dosyası (27 kez)** |
| `WebDriverWait(driver, 10)` step katmanında çıplak kullanım | **~48 kez** |
| `WebDriverWait(driver, 10)` her page sınıfının kendi `__init__`'inde | **11 kez** |

`utils/` klasörü tek bir 40 satırlık dosya içeriyor. `test_data/` tamamen boş.
Yani framework'ün "ortak altyapı" katmanı fiilen **mevcut değil** — ve yukarıdaki tekrarların
tek sebebi bu.

### Olgunluk Skoru

| Boyut | İlk | Güncel | Değerlendirme |
|---|---|---|---|
| Senaryo kapsamı | 8 | 🟢 **8**/10 | 187 senaryo, iyi Gherkin disiplini, INVEST'e uyum |
| Page Object Model | 6 | 🟢 **9**/10 | ✅ Faz 1: BasePage, 18/18 sınıf bağlı. ✅ Faz 3: assert 11 → 6 (kalanlar gerekçeli). Kalan tek eksik: 735 satırlık god class |
| Step katmanı | 3 | 🟡 **5**/10 | ✅ Faz A+B: login tekrarı 16 → 0, sabit kimlik bilgisi 17 → 0, ilk paylaşılan fixture. Kalan: 14 dosyadaki sihirbaz tekrarı (Faz C), ham `By` kullanımı |
| Ortak altyapı (`utils/`) | 1 | 🔴 **3**/10 | ✅ Faz 2: `waits.py`. ✅ Faz A: `config.py` (3 modül). Hedef 8; `text`, `test_data`, `logger`, `api_client` hâlâ yok |
| Test verisi yönetimi | 1 | 🔴 **1**/10 | `test_data/` boş, veri koda gömülü |
| Konfigürasyon | 5 | 🟡 **6**/10 | ✅ Faz A: tek kaynak `utils/config.py`, origin semantiği düzeltildi. Kalan: `requirements.txt`'te sürüm sabitleme yok (K3) |
| Raporlama | 7 | 🟢 **7**/10 | Allure + pytest-html iyi kurulmuş, ekran görüntüsü ekleniyor |
| Repo hijyeni | 2 | 🔴 **2**/10 | README'de çözülmemiş merge conflict, 321KB dosya, 25 artık klasör |
| CI/CD | 0 | 🔴 **0**/10 | Hiç yok |
| Kararlılık (flaky yönetimi) | 5 | 🟡 **6**/10 | ✅ Faz 1: `ignored_exceptions` kapsamı 2/13 → 13/13. Hâlâ retry/paralel/izolasyon mekanizması yok |

**Genel: 3.8 → 4.7 / 10**

> **Neden genel skor yavaş artıyor?** Skor 10 boyutun ortalamasıdır; POM
> 3, step katmanı 2 puan yükseldi ama bu ortalamaya yalnızca 0.5 olarak
> yansıyor. Bu yanıltıcı değil, **gerçekçi**: framework'ün olgunluğu tek
> bir katmanın düzelmesiyle sıçramaz. Kalan üç sıfıra yakın boyut
> (CI/CD 0, test verisi 1, repo hijyeni 2) tek başına ortalamayı 0.3
> aşağı çekiyor — ve üçü de **düşük riskli**, çünkü hiçbiri mevcut test
> mantığına dokunmuyor. Faz C+D step katmanını 7'ye, `utils/`'i 4'e
> taşır (≈ **5.1**); asıl sıçrama CI + test verisi ile gelir.

---

## 2. Şu An İyi Olan Şeyler (Bozmayın)

Bunları korumak, düzeltmeler kadar önemli:

1. **`data-testid` tabanlı locator stratejisi.** XPath/CSS zinciri yerine kararlı test
   kimlikleri kullanılmış. Bu, framework'ün en güçlü yanı.

2. **Dil bağımsızlığı bilinçli bir tasarım kararı.** Doğrulamalar literal TR/EN metne değil;
   eleman görünürlüğü, değer uzunluğu, URL ve değişmez belirteçlere (rakam, `+90`, `—`)
   dayanıyor. Örneğin `search_customers_page.py` içindeki `_turkish_fold()` yardımcısı,
   Türkçe alfabe katlaması sorununu doğru çözüyor.

3. **Kalıtım zincirleri anlamlı kurulmuş.**
   `AddressUpdatePage → AddressAddPage → AddressDeletePage` ve
   `BillingAccountCreatePage → BillingAccountDeletePage → BillingAccountProductsPage`
   gerçek "is-a" ilişkileri; `BillingAccountUpdatePage` içindeki yorum bu kararı
   gerekçelendirmiş. Bu doğru mühendislik.

4. **`implicitly_wait` bilinçli olarak kaldırılmış** ve `conftest.py`'de nedeni yorumla
   belgelenmiş (implicit + explicit wait anti-pattern'i). Bu seviyede bir farkındalık nadir.

5. **`lockout` marker'ı** ile yıkıcı testin varsayılan koşumdan çıkarılması doğru bir refleks.

6. **Kusur takibi disiplini.** `bugsbunny.txt` / `bugsbunnyupdated.txt` ile "kasıtlı kırmızı"
   testlerin gerçek hatalardan ayrılması, olgun bir QA pratiği.

7. **Başarısızlıkta ekran görüntüsü + sayfa kaynağı + URL** Allure'a ekleniyor. Doğru.

---

## 3. Kritik Bulgular — Hemen Müdahale Gerektiren

### 🔴 K1 — README.md içinde çözülmemiş merge conflict, repoya commit edilmiş

```
<<<<<<< HEAD
# CRM Test Automation Framework
...
=======
# crm-test-automation-pytest-bdd
>>>>>>> 6b40b8db2e65bc794f312e3ae3c04e7a666178b1
```

Projenin ilk görünen yüzü bozuk. Bir işe alım mülakatında veya kod incelemesinde
bu **ilk fark edilen şey** olur.

**Yapılacak:** Conflict'i çöz, iki README'yi birleştir. 5 dakikalık iş, etkisi büyük.

---

### 🔴 K2 — `test-design/final-test-set/` altındaki 17 dosya silindi ve **commit edildi**

İlk tespitte bu dosyalar çalışma ağacında silinmiş ama commit edilmemişti.
Sonraki kontrolde silmenin `87a7bae` ile **commit edilip push edildiği**
görüldü — 17 dosya artık `HEAD`'de yok.

Hâlâ git geçmişinde duruyorlar, yani **kurtarılabilirler**:

```bash
git restore --source=58b416b test-design/
```

Silme kasıtlıysa bir işlem gerekmiyor; değilse yukarıdaki komut yeterli.
Bu dosyalar `kesif_testi.txt` ile birlikte projenin test tasarımı
belleğini oluşturuyordu, kaybı geri döndürülemez olmasa da maliyetlidir.

---

### 🔴 K3 — `requirements.txt`'te hiçbir sürüm sabitlenmemiş

```
selenium
pytest
pytest-bdd
python-dotenv
pytest-html
allure-pytest-bdd
allure-python-commons
Faker
```

Bugün çalışan test paketi, yarın `pip install -r requirements.txt` çalıştıran bir
meslektaşınızda veya CI'da **sessizce farklı sürümlerle** kurulur. `pytest-bdd` major
sürüm değişikliklerinde davranış değiştirir; Selenium 4.x içinde bile API farkları vardır.
Bu, tekrarlanamayan test koşumlarının en yaygın sebebidir.

**Yapılacak:**
```bash
pip freeze > requirements.lock.txt
```
ve `requirements.txt`'i minimum sürümlerle sabitle:
```
selenium>=4.20,<5.0
pytest>=8.0,<9.0
pytest-bdd>=7.0,<8.0
...
```

---

### ✅ K4 — Kimlik bilgileri 17 step dosyasına gömülü — **ÇÖZÜLDÜ (Faz A)**

```python
login_page.login("demo", "Password123")   # 17 satırda tekrarlanıyordu
```

İki ayrı problem vardı:
1. **Güvenlik:** Şifre versiyon kontrolünde düz metin. Bugün demo ortamı, yarın staging.
2. **Bakım:** Şifre değişirse 17 dosyaya dokunmak gerekiyordu.

**Yapıldı:** `utils/config.py` `CRM_USERNAME`/`CRM_PASSWORD` ortam
değişkenlerinden okuyor, `steps/conftest.py::credentials` fixture'ı ile
sunuluyor. Step dosyalarında **0** sabit kimlik bilgisi kaldı.

> Varsayılan değerler (`demo` / `Password123`) hâlâ `config.py` içinde
> düz metin duruyor — bu **bilinçli**: yerel geliştirmede `.env` olmadan
> çalışabilmek için. Gerçek bir ortama (staging/CI) geçerken bunlar
> secret olarak enjekte edilmeli, varsayılanlar da kaldırılmalı. Şu anki
> hâli tek dosyada olduğu için bu artık **tek satırlık** bir iş.
>
> `test_login_steps.py`'deki `admin-crm` / `Password123` literalleri
> bilerek bırakıldı: bunlar paylaşılan yapılandırma değil, `demo` hesabı
> kilitlenmesin diye ayrı seçilmiş bir hesabın senaryo verisidir.

---

### 🟠 K5 — `reports/` altında 22 adet artık `allure-results-*` klasörü, toplam 14 MB

```
allure-results-005-06-fix-verify        allure-results-search-fix-verify
allure-results-005-06-fix-verify2       allure-results-search-fix-verify2
allure-results-delete-customer-...5     allure-results-triage-login-button
... (22 adet)
```

Bunlar geçmiş hata ayıklama koşumlarından kalma. `.gitignore`'da `reports/` olduğu için
repoya girmemişler (iyi), ama diskte birikiyorlar ve `allure serve` çağrılarında hangisinin
güncel olduğu karışıyor.

**Yapılacak:** Temizle ve isimlendirme yerine tek bir `reports/allure-results` + arşiv
klasörü kullan (§6.7).

---

### 🟠 K6 — `project_brain.txt` (321 KB) repoda izleniyor

Tek başına repo boyutunun büyük kısmını oluşturuyor. İçeriği geliştirme notu ise
`docs/` altına taşınmalı veya `.gitignore`'a alınmalı.

---

## 4. Katman Katman Analiz

### 4.1 `conftest.py` — Fixture Katmanı

**Mevcut durum:** 96 satır. `driver` ve `base_url` olmak üzere **yalnızca 2 fixture** var.
Ayrıca pytest-bdd step loglama hook'u ve pytest-html entegrasyonu bulunuyor.

**Sorunlar:**

| # | Sorun | Etki |
|---|---|---|
| 1 | `base_url` aslında **login URL'i** döndürüyor (`.env`: `BASE_URL=http://localhost:4200/login`) | Step'ler `/customers/new`'e gitmek için `urlparse(driver.current_url)` ile origin'i yeniden kurmak zorunda kalıyor — **14 dosyada 27 kez** |
| 2 | Varsayılan değer `https://example.com` | `.env` yoksa testler anlamsız bir siteye gider, hata mesajı kafa karıştırıcı olur |
| 3 | `driver` fixture'ı `function` scope'ta — her senaryo yeni tarayıcı | Doğru izolasyon ama **yavaş**; 187 senaryo × ~3sn tarayıcı açılışı ≈ 9 dakika sadece başlatma |
| 4 | Login fixture'ı yok | Her step dosyası kendi login'ini yazıyor |
| 5 | Disposable müşteri fixture'ı yok | 14 dosyada aynı 12 satırlık blok |
| 6 | Başarısızlıkta sadece Allure'a ek yapılıyor, **konsola/log dosyasına hiçbir şey yazılmıyor** | CI'da hata ayıklama zor |

**Öneri:** `base_url` semantiğini düzelt (§6.1), fixture katmanını genişlet.

---

### 4.2 `pages/` — Page Object Model

**Mevcut durum:** 18 dosya, 3.688 satır. En büyüğü `create_customer_page.py` (735 satır).

**Sorunlar:**

#### a) ~~`BasePage` yok — en önemli yapısal eksik~~ ✅ ÇÖZÜLDÜ (Faz 1, `ecf6251`)

**Tespit edilen durum:** 11 ayrı sınıf kendi `__init__`'inde aynı satırı yazıyordu:

```python
def __init__(self, driver):
    self.driver = driver
    self.wait = WebDriverWait(driver, 10)   # 11 kez tekrarlanıyordu
```

Sonuçları:
- Timeout tek yerden değiştirilemiyordu. Yavaş bir CI ortamında 10sn yetmezse
  11 dosya düzenlenecekti.
- `ignored_exceptions=(StaleElementReferenceException,)` yalnızca 2 sayfada
  vardı — **kanıtlanmış flaky kaynağı** (`offer_selection_page.py` /
  TC-014-12 bu yüzden sorun çıkarıyordu).
- Her sayfa kendi `click`, `type`, `get_text` mantığını yeniden yazıyordu.

**Yapılan:** `pages/base_page.py` oluşturuldu; 18/18 sınıf bağlandı.
Timeout artık `DEFAULT_TIMEOUT` ortam değişkeniyle tek yerden yönetiliyor,
stale koruması her sayfada. Ayrıntı ve doğrulama sonuçları için §0'a bakınız.

**Kalan iş:** 20 ortak yardımcı metot henüz benimsenmedi — sayfalar hâlâ
kendi `self.driver.find_element(...)` çağrılarını yapıyor. Bu, ayrı bir
faz olarak ele alınmalıdır.

#### b) Page object içinde `assert` — 11 → 6 ✅ ÇÖZÜLDÜ (Faz 3, `e7d260c`)

POM sözleşmesi: **page object durumu döndürür, step katmanı iddia eder.**
Assert'ler page içine girdiğinde aynı metot ters bir senaryoda yeniden
kullanılamaz hale gelir.

İlk tespitte 11 assert sayılmıştı. Detaylı inceleme bunların **üç farklı
şey** yaptığını gösterdi — hepsi taşınmamalıydı:

**Kategori A — gerçek POM ihlali (5 assert / 3 metot) → TAŞINDI**

Üçü de yalnızca iddia etmek için vardı (`verify_*` isimli, anlamlı bir şey
döndürmüyor, her biri tek bir step'ten çağrılıyor):

| Eski (page iddia ediyordu) | Yeni (page durum döndürüyor) |
|---|---|
| `verify_next_page_records_are_new()` | `get_next_page_record_comparison()` |
| `verify_navigated_to_customer_detail_same_tab()` | `get_customer_detail_navigation_state()` |
| `verify_all_search_fields_empty()` | `get_all_search_field_values()` |

**Beklemeler page'de bırakıldı** — bekleme page katmanının işidir; yalnızca
iddia step'e taşındı. Yan kazanç: hata mesajları iyileşti. Örneğin alan
temizliği kontrolü artık ilk hatada durmak yerine temizlenmeyen alanların
**tamamını** raporluyor.

**Kategori B — ayrıştırma/veri sağlığı guard'ı (3 assert) → PAGE'DE KALDI**

`is_customer_id_column_sorted_ascending()`, `get_results_count_number()`,
`get_results_range_bounds()`

Bunlar iş kuralı doğrulamıyor; **dönüş değerinin anlamlı olduğunu** garanti
ediyor. Boş listede "sıralı" yanlış-pozitifini ve regex eşleşmemesini
engelliyorlar. Step'e taşınırlarsa page metodu sessizce anlamsız değer
döndürür — bu daha kötüdür.

**Kategori C — beklemeden sonra ek doğrulama (3 assert) → PAGE'DE KALDI**

`wait_for_no_results_state()`, `wait_for_no_mobile_phone_error_and_save_enabled()`,
`wait_for_save_enabled_with_no_identity_number_error()`

Bunlar ilk bakışta "beklemeyle çakışan ölü kod" sanılabilir — **değiller.**
Wait bir şeyi bekliyor, assert **başka** bir şeyi kontrol ediyor:

| Metot | Wait ne bekliyor | Assert ne kontrol ediyor |
|---|---|---|
| `wait_for_no_results_state` | EMPTY_STATE görünür olsun | satır sayısı 0 mı |
| Diğer ikisi | Kaydet butonu aktifleşsin | hata mesajı görünmüyor mu |

Kodda gerekçesi yazılı: yarış durumundan kaçınmak için önce nihai durum
bekleniyor, sonra hata elemanı okunuyor. Assert kaldırılırsa **doğrulama
tamamen kaybolur.** Taşınabilirler ama kazanç marjinal, üç ayrı dosyaya
dokunmak gerekir.

**Sonuç: 11 → 6.** Kalan 6, POM ihlali değil; yukarıda gerekçelendirilmiş
bilinçli kararlardır.

#### c) `time.sleep` — kısmen çözüldü (Faz 2)

> **İlk sayımda hata vardı — düzeltildi.** İlk taramada 6 kullanım
> raporlanmıştı; `address_update_page.py`'deki geçişin bir **yorum satırı**
> olduğu sonradan görüldü. Gerçek sayı **5**'ti ve hepsi aynı problem
> değildi:

| Konum | Tür | Durum |
|---|---|---|
| `delete_customer_page.py` × 1 | Gerçek poll döngüsü | ✅ `poll_until`'e taşındı |
| `search_customers_page.py` × 1 | Gerçek poll döngüsü | ✅ `poll_until`'e taşındı |
| `create_customer_page.py` × 3 | Sabit 0.3sn bekleme | ⏸️ Bilinçli olarak bırakıldı |
| `address_update_page.py` | Yorum satırı | — (bulgu geçersiz) |

**Taşınan ikisi**, asenkron silme gecikmesini tolere etmek için
"eylem → bekle → kontrol" turunu tekrarlayan gerçek yoklama döngüleriydi.
Artık `utils/waits.py::poll_until()` ile adı konmuş durumda.

**Kalan üçü** farklı bir problem: bir adımın son alanına değer girilip
odak kaydırıldıktan sonra Angular'ın form geçerliliğini yeniden
hesaplaması bekleniyor. Tek bir `WebDriverWait` koşulu yazılamıyor çünkü
*ne* bekleneceği senaryoya göre değişiyor — pozitif senaryoda buton
aktifleşmeli, negatifte **pasif kalmalı**.

Bunlar için `utils/waits.py::wait_for_dom_settled()` yazıldı
(MutationObserver ile DOM durulmasını bekler; hızlı makinede ~150ms →
bugünkünden hızlı, yavaş CI'da 1.5sn'ye kadar → bugünkünden sağlam).
Ancak **uygulanmadı**: bu üç bekleme, 14 step dosyasının disposable
müşteri oluşturmak için kullandığı en sıcak kod yolunda. Bugün çalışıyor
olmaları ve kazancın ancak CI'ya geçildiğinde görünür olması nedeniyle
değişiklik ertelendi.

> **Yapılacak (CI'ya geçişten önce):** `create_customer_page.py`'deki üç
> `time.sleep(0.3)` çağrısını `wait_for_dom_settled()` ile değiştir ve
> `create_customer` + ona bağlı feature'ları koş (~35 dk). Sabit 300ms
> varsayımı, CI'da kırılacak ilk şeylerden biridir.

#### d) `create_customer_page.py` 735 satır — tek sorumluluk ihlali

Bu dosya üç ekranın (Demografik / Adres / İletişim) sorumluluğunu birlikte taşıyor.
Sihirbaz adımı başına ayrı sınıflara bölünmeli.

---

### 4.3 `steps/` — En Zayıf Katman *(Faz A+B ile kısmen düzeltildi)*

**Faz A+B öncesi:** 17 dosya, 3.879 satır. **Sıfır `@pytest.fixture` tanımı.**
**Faz A+B sonrası:** 3.756 satır + `steps/conftest.py` (2 fixture).

Tüm kurulum, `@given(..., target_fixture="...")` içinde yapılıyordu. Bu pytest-bdd'de geçerli
bir desendir; ancak burada kurulum kodu **paylaşılmadığı için** her dosyaya kopyalanmıştı.

Tipik bir step dosyasının açılışı **(Faz A+B ÖNCESİ)**:

```python
@given("kullanıcı ... görüntülemektedir", target_fixture="address_page")
def user_on_customer_address_tab(driver, base_url):
    login_page = LoginPage(driver)
    login_page.open(base_url)
    login_page.login("demo", "Password123")          # ← sabit kodlanmış
    WebDriverWait(driver, 10).until(lambda d: "/customers" in d.current_url)  # ← çıplak wait

    origin = urlparse(driver.current_url)             # ← origin yeniden kuruluyor
    driver.get(f"{origin.scheme}://{origin.netloc}/customers/new")
    create_page = CreateCustomerPage(driver)
    create_page.fill_demographic_step_with_faker(gender="Erkek")
    create_page.click_demographic_next()
    create_page.wait_for_address_step()
    create_page.add_address_with_faker()              # ← bu 12 satır
    create_page.wait_for_address_saved()              #    14 dosyada
    create_page.click_address_next()                  #    neredeyse birebir
    create_page.wait_for_contact_step()               #    aynı
    create_page.fill_contact_step_with_faker()
    create_page.click_submit()
    create_page.wait_for_navigated_to_customer_info()

    return AddressUpdatePage(driver)
```

**Faz A+B SONRASI aynı fonksiyon** — ilk 6 satır (login + origin) tamamen
gitti, `authenticated_driver` fixture'ı devraldı:

```python
@given("kullanıcı ... görüntülemektedir", target_fixture="address_page")
def user_on_customer_address_tab(authenticated_driver):
    authenticated_driver.get(config.url("/customers/new"))
    create_page = CreateCustomerPage(authenticated_driver)
    ...                                               # ← 12 satırlık sihirbaz
    return AddressUpdatePage(authenticated_driver)    #    HÂLÂ 14 dosyada
```

**Kalan bir numaralı sorun:** o 12 satırlık sihirbaz bloğu hâlâ **14
dosyada**. Müşteri oluşturma akışına bir alan eklenirse 14 dosya
düzenlenecek. Faz C'nin (`new_customer` factory fixture) hedefi tam olarak
bu.

**Ayrıca:** Step katmanında **56 çıplak `WebDriverWait`** ve 7 dosyada
**24 ham `By.*` locator'ı** var. Bekleme ve locator mantığı page
katmanına ait; step'te olması katman ihlali (Faz E).

---

### 4.4 `utils/` — Fiilen Yok (En Kritik Eksik)

Başlangıç durumu:

```
utils/
├── .gitkeep
└── session.py    (40 satır — JWT exp claim'ini geçmişe çekiyor)
```

Güncel durum (Faz 2 + Faz A):

```
utils/
├── .gitkeep
├── session.py    (40 satır  — JWT exp claim'ini geçmişe çekiyor)
├── waits.py      (100 satır — poll_until, wait_for_dom_settled)   ✅ Faz 2
└── config.py     (40 satır  — kimlik bilgileri, origin, url())    ✅ Faz A
```

`session.py` iyi yazılmış, amacı net ve yorumlanmış. Artık tek başına
değil, ama hedef 8 modüle göre hâlâ **3/8**: `text`, `test_data`,
`logger`, `driver_factory`, `api_client` eksik.

Ne eklenmesi gerektiği **§6**'da kodla birlikte.

---

### 4.5 `test_data/` — Tamamen Boş

Sadece `.gitkeep` var. Tüm test verisi ya koda gömülü ya Faker ile üretiliyor.

**Sorun:** Faker rastgele veri üretir; bu **pozitif** akışlar için mükemmeldir ama
**sınır değer** testleri için uygun değildir. `kesif_testi.txt`'te tasarlanan 16 SDA
senaryosu (10 hane / 9 hane / 11 hane, 50 karakter / 51 karakter) deterministik veri
gerektiriyor. Bu değerler şu an Gherkin `Examples` tablolarına gömülü — kabul edilebilir,
ama alan sınırları (`maxlength`) merkezi bir yerde tanımlı olmalı ki tek noktadan
güncellenebilsin.

---

### 4.6 `features/` — İyi Durumda

17 dosya, 187 senaryo. Gherkin disiplini yüksek: `Scenario Outline` yerinde kullanılmış,
senaryo isimleri açıklayıcı, `Background` doğru kullanılmış.

**Küçük öneriler:**
- **Tag stratejisi yok.** Şu an yalnızca `@lockout` var. `@smoke`, `@regression`,
  `@destructive`, `@known-bug` etiketleri eklenirse alt küme koşumu mümkün olur.
- Feature dosyalarında `Feature:` altında **kullanıcı hikâyesi** (As a… I want… So that…)
  çoğunlukla yok. INVEST'in "Valuable" boyutu için faydalı olur.

---

### 4.7 Konfigürasyon

**`pytest.ini`:**
```ini
addopts = --html=reports/report.html --self-contained-html
          --alluredir=reports/allure-results --clean-alluredir -m "not lockout"
```

**Eksikler:**

| Eksik | Neden gerekli |
|---|---|
| `--strict-markers` | Yazım hatası olan bir marker sessizce yok sayılıyor (`@smoek` gibi) |
| `-ra` | Koşum sonunda atlanan/başarısız testlerin özeti görünmüyor |
| `--tb=short` | Varsayılan traceback CI loglarında çok uzun |
| `log_cli` ayarları | Canlı koşumda ilerleme görünmüyor |
| `filterwarnings` | Deprecation uyarıları gürültü yapıyor |
| Ek marker'lar | `smoke`, `regression`, `destructive`, `known_bug` |

**`.env`:** `.gitignore`'da (doğru), ama **`.env.example` yok.** Projeyi yeni klonlayan
biri hangi değişkenleri tanımlaması gerektiğini bilemez.

---

### 4.8 Raporlama — İyi Kurulmuş

Allure + pytest-html + başarısızlıkta ekran görüntüsü/sayfa kaynağı/URL. Bu katman sağlam.

**Geliştirme alanları:**
- Allure `severity`, `epic`, `feature`, `story` etiketleri kullanılmıyor →
  rapor gruplanamıyor
- Başarısız testin **video** veya **DOM anlık görüntüsü zaman serisi** yok
- Tarayıcı konsol logları (`driver.get_log("browser")`) toplanmıyor —
  JS hatalarını yakalamanın en ucuz yolu

---

### 4.9 CI/CD — Hiç Yok

`.github/workflows/` mevcut değil. Bu, framework'ün **tek kullanıcılı** kaldığı anlamına
geliyor: testler yalnızca sizin makinenizde, sizin elinizle çalışıyor.

Bir test otomasyon framework'ünün asıl değeri, **her commit'te otomatik çalışmasıdır.**
CI olmadan framework bir "test yazma aracı"dır, "kalite güvencesi mekanizması" değildir.

---

## 5. Kararlılık (Flaky) Yönetimi

**Mevcut:** Flaky testler manuel triyaj edilmiş ve belgelenmiş — bu iyi.
**Eksik:** Sistematik mekanizma yok.

| Eksik mekanizma | Faydası |
|---|---|
| `pytest-rerunfailures` | Gerçek flaky'yi gerçek hatadan ayırır (`--reruns 2 --reruns-delay 1`) |
| `pytest-xdist` | 187 senaryo paralel koşarsa süre ~4 kat düşer |
| Test izolasyonu | Şu an sepet gibi **sunucu tarafı durum** testler arası sızıyor (bkz. `kesif_testi.txt` KESIF-OFFER-04) |
| Deterministik sıralama | `pytest-randomly` ile gizli sıra bağımlılıkları yakalanır |

> ⚠️ **Paralelleştirme uyarısı:** `pytest-xdist` eklemeden önce test izolasyonu çözülmeli.
> Şu an testler aynı `demo` kullanıcısını ve aynı sunucu tarafı sepeti paylaşıyor;
> paralel koşum bunları birbirine karıştırır.

---

## 6. `utils/` Altına Eklenmesi Gerekenler — Somut Kod

Bu bölüm **doğrudan uygulanabilir** olacak şekilde yazıldı. Öncelik sırasına göre.

### 6.1 `utils/config.py` — Merkezî Konfigürasyon ⭐ ÖNCELİK 1

Sabit kodlanmış kimlik bilgilerini ve `base_url` semantik hatasını tek seferde çözer.

```python
"""Tüm ortam konfigürasyonunun TEK kaynağı.

base_url artık ORIGIN döndürüyor (login URL'i değil) - böylece step'ler
urlparse ile origin'i yeniden kurmak zorunda kalmıyor.
"""
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _int_env(key: str, default: int) -> int:
    try:
        return int(os.getenv(key, default))
    except (TypeError, ValueError):
        return default


@dataclass(frozen=True)
class Config:
    # --- ortam ---
    base_url: str = os.getenv("BASE_URL", "http://localhost:4200").rstrip("/")
    browser: str = os.getenv("BROWSER", "chrome").lower()
    headless: bool = os.getenv("HEADLESS", "false").lower() == "true"

    # --- kimlik bilgileri (ARTIK KODDA DEĞİL) ---
    username: str = os.getenv("CRM_USERNAME", "demo")
    password: str = os.getenv("CRM_PASSWORD", "")

    # --- zaman aşımları (tek yerden ayarlanabilir) ---
    default_timeout: int = _int_env("DEFAULT_TIMEOUT", 10)
    slow_timeout: int = _int_env("SLOW_TIMEOUT", 30)
    poll_frequency: float = 0.3

    # --- pencere ---
    window_width: int = _int_env("WINDOW_WIDTH", 1920)
    window_height: int = _int_env("WINDOW_HEIGHT", 1080)

    # --- türetilmiş adresler ---
    @property
    def login_url(self) -> str:
        return f"{self.base_url}/login"

    @property
    def customers_url(self) -> str:
        return f"{self.base_url}/customers"

    def customer_url(self, customer_id) -> str:
        return f"{self.base_url}/customers/{customer_id}"

    @property
    def new_customer_url(self) -> str:
        return f"{self.base_url}/customers/new"


config = Config()
```

Buna eşlik eden **`.env.example`** (repoya commit edilir, `.env` edilmez):

```bash
BASE_URL=http://localhost:4200
BROWSER=chrome
HEADLESS=false

CRM_USERNAME=demo
CRM_PASSWORD=degistir-beni

DEFAULT_TIMEOUT=10
SLOW_TIMEOUT=30
```

---

### 6.2 `pages/base_page.py` — Ortak Sayfa Davranışı ⭐ ÖNCELİK 1

11 sınıftaki tekrarı ortadan kaldırır ve stale-element korumasını **her sayfaya** getirir.

```python
"""Tüm page object'lerin ortak atası.

Buradaki tek kritik karar: WebDriverWait'in ignored_exceptions ile
kurulması. StaleElementReferenceException, Angular gibi DOM'u sürekli
yeniden çizen framework'lerde en yaygın flaky kaynağıdır ve tek tek
sayfalarda ele alınırsa MUTLAKA unutulan bir sayfa kalır.
"""
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
)
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.config import config

_TRANSIENT = (StaleElementReferenceException, ElementClickInterceptedException)


class BasePage:
    def __init__(self, driver, timeout: int | None = None):
        self.driver = driver
        self.wait = WebDriverWait(
            driver,
            timeout or config.default_timeout,
            poll_frequency=config.poll_frequency,
            ignored_exceptions=_TRANSIENT,
        )
        self.slow_wait = WebDriverWait(
            driver,
            config.slow_timeout,
            poll_frequency=config.poll_frequency,
            ignored_exceptions=_TRANSIENT,
        )

    # ---------- temel etkileşimler ----------
    def find(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def find_visible(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def find_all(self, locator):
        return self.driver.find_elements(*locator)

    def click(self, locator):
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def js_click(self, locator):
        """Selenium'un tıklama noktası hesabı bir kaplama (overlay) nedeniyle
        şaştığında kullanılır - login-password-toggle'da kanıtlanmış ihtiyaç."""
        self.driver.execute_script("arguments[0].click();", self.find(locator))

    def type(self, locator, text, clear=True):
        field = self.find_visible(locator)
        if clear:
            field.clear()
        field.send_keys(text)
        return field

    def text_of(self, locator) -> str:
        """find + .text'i TEK bir retry'lanan lambda içinde yapar.
        Ayrı ayrı yapılırsa aradaki DOM yenilenmesi stale hatası üretir."""
        return self.wait.until(
            lambda d: d.find_element(*locator).text
        )

    def value_of(self, locator) -> str:
        return self.find(locator).get_attribute("value") or ""

    def is_displayed(self, locator) -> bool:
        elements = self.find_all(locator)
        return bool(elements) and elements[0].is_displayed()

    def is_enabled(self, locator) -> bool:
        return self.find(locator).is_enabled()

    # ---------- beklemeler ----------
    def wait_until_gone(self, locator):
        self.wait.until(EC.invisibility_of_element_located(locator))

    def wait_for_url_contains(self, fragment):
        self.wait.until(lambda d: fragment in d.current_url)

    def wait_for_count(self, locator, expected):
        self.wait.until(lambda d: len(d.find_elements(*locator)) == expected)

    # ---------- tarayıcı ----------
    def open(self, url):
        self.driver.get(url)
        return self

    def refresh(self):
        self.driver.refresh()
        return self

    def browser_logs(self):
        """JS hatalarını yakalamanın en ucuz yolu."""
        try:
            return self.driver.get_log("browser")
        except Exception:
            return []
```

**Uygulama:** Tüm kök page sınıflarını `class XPage(BasePage):` yap ve
kendi `__init__`'lerini sil.

---

### 6.3 `utils/waits.py` — Adı Konmuş Bekleme Desenleri ⭐ ÖNCELİK 2

`time.sleep` kullanımlarının niyetini kodda görünür kılar.

```python
"""Standart WebDriverWait'in karşılamadığı bekleme desenleri.

Buradaki fonksiyonlar 'time.sleep' değildir - hepsi bir KOŞUL yokluyor.
Fark şu: bazı koşullar tek bir DOM sorgusuyla değil, sayfa yenileme veya
yeniden arama gerektirir (asenkron backend işlemleri).
"""
import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait

from utils.config import config


def poll_until(action, condition, attempts=6, interval=2.0, description=""):
    """Her denemede action() çalıştırır, sonra condition() kontrol eder.

    Asenkron backend işlemleri için: silme isteği kabul edilir ama işlem
    saniyeler sonra tamamlanır - tek bir DOM beklemesi bunu yakalayamaz,
    işlemin (sayfa yenileme/yeniden arama) TEKRARLANMASI gerekir.
    """
    last = None
    for attempt in range(1, attempts + 1):
        last = action()
        if condition(last):
            return last
        if attempt < attempts:
            time.sleep(interval)
    raise TimeoutException(
        f"{description or 'Koşul'} {attempts} denemede sağlanamadı "
        f"(aralık={interval}sn, son değer={last!r})"
    )


def wait_for_attribute_change(driver, element, attribute, timeout=None):
    """Polling aralığından DAHA KISA süren durum geçişlerini yakalar.

    MutationObserver kullanır çünkü dışarıdan periyodik yoklama, ne kadar
    sık olursa olsun, ~100ms'lik bir pencereyi ŞANSA BAĞLI kaçırır.
    (login butonunun submit sırasında pasifleşmesi: ~60ms'de başlıyor,
    ~200ms'de bitiyor - canlı ölçüldü.)
    """
    driver.execute_script(
        """
        const [el, attr] = arguments;
        window.__attrChanged = false;
        new MutationObserver(() => { window.__attrChanged = true; })
            .observe(el, {attributes: true, attributeFilter: [attr]});
        """,
        element, attribute,
    )
    return lambda: bool(driver.execute_script("return window.__attrChanged;"))


def wait_for_stable_count(driver, locator, timeout=None, stable_for=0.6):
    """Eleman sayısı belirli bir süre DEĞİŞMEDİĞİNDE döner.

    Kademeli yüklenen listeler için: 'en az 1 satır var' yetersizdir,
    çünkü 3. satır 200ms sonra gelebilir.
    """
    end = time.time() + (timeout or config.default_timeout)
    last_count, stable_since = -1, None
    while time.time() < end:
        count = len(driver.find_elements(*locator))
        if count == last_count:
            if stable_since and (time.time() - stable_since) >= stable_for:
                return count
        else:
            last_count, stable_since = count, time.time()
        time.sleep(0.15)
    raise TimeoutException(f"Eleman sayısı {timeout}sn içinde kararlı hale gelmedi")
```

---

### 6.4 `utils/text.py` — Dil Bağımsız Metin Yardımcıları ⭐ ÖNCELİK 2

`search_customers_page.py` içine gömülü olan Türkçe katlama mantığını dışarı çıkarır ve
**tüm projede** kullanılabilir hale getirir.

```python
"""Dil bağımsız metin karşılaştırma ve ayrıştırma.

Bu modül framework'ün 'TR/EN bağımsızlık' sözleşmesinin teknik karşılığıdır.
"""
import re

# Türkçe'nin İ/I/ı/i sorunu: 'FIBER'.lower() Türkçe yerel ayarında 'fıber'
# üretir ve 'fiber' ile EŞLEŞMEZ. Uygulamanın kendi arama filtresinde bu
# hatanın canlı örneği bulundu (bkz. kesif_testi.txt KESIF-OFFER-01).
_TURKISH_FOLD = str.maketrans({
    "ı": "i", "İ": "i", "I": "i", "i": "i",
    "ğ": "g", "Ğ": "g", "ş": "s", "Ş": "s",
    "ç": "c", "Ç": "c", "ö": "o", "Ö": "o",
    "ü": "u", "Ü": "u",
})


def fold(text: str) -> str:
    """Aksan/Türkçe-duyarsız karşılaştırma için normalize eder."""
    return (text or "").translate(_TURKISH_FOLD).lower().strip()


def matches(actual: str, expected: str) -> bool:
    return fold(actual) == fold(expected)


def starts_with(actual: str, prefix: str) -> bool:
    return fold(actual).startswith(fold(prefix))


def first_number(text: str) -> int | None:
    """'1106 kayıt' / '1106 records' → 1106. Dile bakmaz."""
    match = re.search(r"\d+", text or "")
    return int(match.group()) if match else None


def all_numbers(text: str) -> list[int]:
    """'1106 kayıttan 1096–1106 arası' → [1106, 1096, 1106]"""
    return [int(n) for n in re.findall(r"\d+", text or "")]


def money(text: str) -> float | None:
    """'1,149.70 TL' → 1149.70. Para birimi etiketini okumaz."""
    cleaned = re.sub(r"[^\d.,]", "", text or "").replace(",", "")
    try:
        return float(cleaned)
    except ValueError:
        return None


def contains_number(text: str, number: int) -> bool:
    """Dil bağımsız doğrulamanın temel taşı: mesajın İÇİNDEKİ RAKAMI arar.

    'TC Kimlik No 11 haneli olmalıdır' ve 'Identity number must be 11 digits'
    metinlerinin ikisi de contains_number(msg, 11) ile doğrulanır.
    """
    return number in all_numbers(text)
```

---

### 6.5 `utils/test_data.py` — Veri Fabrikası ⭐ ÖNCELİK 3

Faker'ı sarmalar ve **sınır değerleri merkezîleştirir.**

```python
"""Test verisi üretimi ve alan sınırlarının TEK kaynağı.

Alan sınırları burada tanımlı olduğu için, uygulama bir sınırı değiştirdiğinde
tek satır güncellenir - Gherkin Examples tablolarındaki sayılar da buradan
türetilebilir.
"""
import random
from dataclasses import dataclass

from faker import Faker

fake = Faker("tr_TR")


# --- CANLI DOĞRULANMIŞ ALAN SINIRLARI ---
FIELD_LIMITS = {
    "first_name": 50,
    "last_name": 50,
    "second_name": 100,
    "father_name": 100,
    "mother_name": 100,
    "identity_number": 11,
    "birth_date": 10,          # gg/aa/yyyy
    "customer_id": 20,
    "account_number": 10,
    "order_number": 8,
    "gsm": 10,
    # Aşağıdakilerde uygulamada maxlength YOK - bilinen eksiklik
    "address_street": None,
    "address_building": None,
    "address_description": None,
    "billing_account_name": None,
    "billing_account_description": None,
}


def at_limit(field: str) -> str:
    """Tam sınır değerinde geçerli girdi (SDA: eşiğin kendisi)."""
    limit = FIELD_LIMITS[field]
    return "A" * limit if limit else "A" * 100


def under_limit(field: str, by: int = 1) -> str:
    """Sınırın bir altı (SDA: eşiğin altı)."""
    limit = FIELD_LIMITS[field]
    return "A" * (limit - by) if limit else "A" * 99


def over_limit(field: str, by: int = 1) -> str:
    """Sınırın bir üstü (SDA: eşiğin üstü) - kırpılması beklenir."""
    limit = FIELD_LIMITS[field]
    return "A" * (limit + by) if limit else "A" * 300


def unique_identity_number() -> str:
    """11 haneli, çakışmayan kimlik numarası.

    Zaman damgası tabanlı çünkü uygulama benzersizlik doğruluyor ve
    tamamen rastgele üretim paralel koşumda çakışabilir.
    """
    import time
    return str(int(time.time() * 1000))[-11:].rjust(11, "9")


@dataclass
class CustomerData:
    first_name: str
    last_name: str
    identity_number: str
    birth_date: str
    gender: str
    email: str
    mobile_phone: str

    @classmethod
    def random(cls, gender: str = "Erkek"):
        return cls(
            first_name=fake.first_name_male() if gender == "Erkek" else fake.first_name_female(),
            last_name=fake.last_name(),
            identity_number=unique_identity_number(),
            birth_date=fake.date_of_birth(minimum_age=18, maximum_age=80).strftime("%d%m%Y"),
            gender=gender,
            email=f"kesif{random.randint(100000, 999999)}@example.com",
            mobile_phone=f"5{random.randint(300000000, 599999999)}",
        )


@dataclass
class AddressData:
    city: str
    street: str
    building_no: str
    description: str

    @classmethod
    def random(cls):
        return cls(
            city=random.choice(["Ankara", "İstanbul", "İzmir", "Bursa", "Antalya"]),
            street=fake.street_name(),
            building_no=str(random.randint(1, 200)),
            description=fake.word(),
        )
```

---

### 6.6 `utils/logger.py` — Yapılandırılmış Loglama ⭐ ÖNCELİK 3

CI'da hata ayıklamanın olmazsa olmazı.

```python
"""Konsol + dosya loglaması.

CI'da bir test başarısız olduğunda elinizde yalnızca traceback olur;
o ana kadar hangi adımların geçtiğini görmek hata ayıklama süresini
dramatik biçimde kısaltır.
"""
import logging
import sys
from pathlib import Path

LOG_DIR = Path("reports/logs")


def get_logger(name: str = "crm-tests") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )

    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(fmt)
    logger.addHandler(console)

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(LOG_DIR / "test-run.log", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    return logger


log = get_logger()
```

---

### 6.7 `utils/driver_factory.py` — Sürücü Kurulumu ⭐ ÖNCELİK 4

`conftest.py`'yi inceltir, tarayıcı yeteneklerini merkezîleştirir.

```python
"""WebDriver oluşturma - tarayıcıya özel tüm ayarlar TEK yerde."""
from selenium import webdriver

from utils.config import config


def _chrome_options():
    opts = webdriver.ChromeOptions()
    if config.headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-gpu")
    # Otomasyon bandını gizle - bazı uygulamalar davranış değiştirir
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    # Tarayıcı konsol loglarını topla (JS hatalarını yakalamak için)
    opts.set_capability("goog:loggingPrefs", {"browser": "ALL"})
    return opts


def create_driver():
    browser = config.browser
    if browser == "firefox":
        opts = webdriver.FirefoxOptions()
        if config.headless:
            opts.add_argument("--headless")
        driver = webdriver.Firefox(options=opts)
    elif browser == "edge":
        opts = webdriver.EdgeOptions()
        if config.headless:
            opts.add_argument("--headless=new")
        driver = webdriver.Edge(options=opts)
    else:
        driver = webdriver.Chrome(options=_chrome_options())

    driver.set_window_size(config.window_width, config.window_height)
    # implicitly_wait BİLEREK ayarlanmıyor - explicit wait ile birlikte
    # kullanımı resmî Selenium dokümantasyonunda uyarılan anti-pattern.
    return driver
```

---

### 6.8 `utils/api_client.py` — Test Kurulumunu Hızlandırma ⭐ ÖNCELİK 5 (Stratejik)

**Bu, framework'ün süresini en çok kısaltacak tek değişikliktir.**

Şu an her adres/iletişim/fatura testi, UI üzerinden sıfırdan müşteri oluşturuyor:
sihirbazın 3 adımı, ~15 saniye. 14 step dosyası bunu yapıyor.

**Arka uç topolojisi (Faz 0 sırasında CANLI DOĞRULANDI):**

| Adres | Rol | Durum |
|---|---|---|
| `localhost:4200` | Angular frontend | ✅ |
| `localhost:8080` | **API Gateway** (Spring Cloud Gateway) | ✅ |
| `localhost:8080/bff-service/api/v1/...` | BFF servisi (gateway arkasında) | ✅ |
| `localhost:8180/realms/etiya-crm` | Keycloak | ✅ |
| `localhost:8081/8082/8084/8085/8090` | Diğer mikroservisler | ✅ |

Doğrulanmış login uç noktası:

```
POST http://localhost:8080/bff-service/api/v1/auth/login
Content-Type: application/json
{"username":"demo","password":"..."}
→ 200 {"accessToken":"eyJhbGciOiJSUzI1NiIs..."}
```

> ⚠️ **Gateway'de rate limiting var.** Yanıt başlıklarında görüldü:
> `X-RateLimit-Burst-Capacity: 20`, `X-RateLimit-Replenish-Rate: 1`,
> `X-RateLimit-Requested-Tokens: 4`.
> Yani saniyede 1 token dolan, 20 kapasiteli bir kova ve her istek 4 token
> tüketiyor → **sürdürülebilir hız ≈ 15 istek/dakika**. API ile toplu
> kurulum yaparken veya `pytest-xdist` ile paralel koşarken bu sınır
> aşılırsa 429 alınır. `ApiClient` bir geri-çekilme (backoff) mekanizması
> içermelidir.

Kurulum API ile yapılıp doğrulama UI ile yapılmalıdır:

```python
"""Test ÖN KOŞULLARINI API ile kurar - UI yalnızca DOĞRULAMA için kullanılır.

Test piramidi ilkesi: UI üzerinden kurulum yapmak, testin asıl amacı olmayan
bir akışı her seferinde yeniden çalıştırmak demektir. Adres güncelleme testi,
müşteri oluşturma akışının çalışmasına bağımlı olmamalıdır.
"""
import requests

from utils.config import config


class ApiClient:
    # Gateway rate limit'i: ~15 istek/dk sürdürülebilir. Toplu kurulumda
    # 429 alınırsa üstel geri çekilme (backoff) uygulanmalı.
    BASE_PATH = "/bff-service/api/v1"

    def __init__(self, token: str | None = None):
        self.base = config.base_url.replace(":4200", ":8080") + self.BASE_PATH
        self.session = requests.Session()
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"

    @classmethod
    def from_browser(cls, driver):
        """Tarayıcı oturumundaki token'ı devralır - ayrı login gerekmez."""
        token = driver.execute_script(
            "return sessionStorage.getItem('etiya.refreshToken');"
        )
        return cls(token)

    def create_customer(self, payload: dict) -> dict:
        r = self.session.post(f"{self.base}/api/customers", json=payload, timeout=15)
        r.raise_for_status()
        return r.json()

    def delete_customer(self, customer_id) -> None:
        self.session.delete(f"{self.base}/api/customers/{customer_id}", timeout=15)

    def clear_cart(self, account_id) -> None:
        """KESIF-OFFER-04: sepet sunucu tarafında kalıcı ve testler arası
        sızıyor. Test izolasyonu için her satış testinden ÖNCE temizlenmeli."""
        self.session.delete(f"{self.base}/api/cart/{account_id}", timeout=15)
```

> **Not:** Uç nokta adresleri doğrulanmalıdır — yukarıdakiler örnektir.
> `requirements.txt`'te `requests` zaten yok, eklenmeli.
> Projenin GitHub açıklamasında "Requests" geçiyor, yani bu niyet zaten varmış.

---

### 6.9 Özet: `utils/` Hedef Yapısı

```
utils/
├── __init__.py
├── config.py            ⭐1  Merkezî konfigürasyon + kimlik bilgileri
├── waits.py             ⭐2  poll_until, MutationObserver, kararlı sayım
├── text.py              ⭐2  Türkçe katlama, sayı/para ayrıştırma
├── test_data.py         ⭐3  Veri fabrikası + ALAN SINIRLARI
├── logger.py            ⭐3  Konsol + dosya loglaması
├── driver_factory.py    ⭐4  Tarayıcı kurulumu
├── api_client.py        ⭐5  API ile hızlı kurulum (stratejik)
├── assertions.py        ⭐5  Alan bazlı özel assert'ler
└── session.py           ✅   (mevcut, korunacak)
```

Ve yeni bir dosya:

```
pages/base_page.py       ⭐1  Tüm page object'lerin ortak atası
```

---

## 7. `conftest.py` Nasıl Görünmeli

Yukarıdaki modüller eklendikten sonra `conftest.py` **tekrarı ortadan kaldıran**
fixture'lar sunmalı:

```python
import allure
import pytest

from pages.login_page import LoginPage
from pages.create_customer_page import CreateCustomerPage
from utils.config import config
from utils.driver_factory import create_driver
from utils.logger import log
from utils.test_data import CustomerData


@pytest.fixture
def driver(request):
    driver = create_driver()
    yield driver
    if getattr(getattr(request.node, "rep_call", None), "failed", False):
        _attach_failure_evidence(driver)
    driver.quit()


def _attach_failure_evidence(driver):
    allure.attach(driver.get_screenshot_as_png(), "Ekran Görüntüsü",
                  allure.attachment_type.PNG)
    allure.attach(driver.page_source, "Sayfa Kaynağı",
                  allure.attachment_type.HTML)
    allure.attach(driver.current_url, "URL", allure.attachment_type.TEXT)
    # JS hataları - en ucuz teşhis kaynağı
    try:
        logs = driver.get_log("browser")
        if logs:
            allure.attach("\n".join(str(entry) for entry in logs),
                          "Tarayıcı Konsolu", allure.attachment_type.TEXT)
    except Exception:
        pass


@pytest.fixture
def logged_in(driver):
    """17 step dosyasındaki login tekrarını TEK yerde toplar."""
    page = LoginPage(driver)
    page.open(config.login_url)
    page.login(config.username, config.password)
    page.wait_for_url_contains("/customers")
    log.info("Giriş yapıldı: %s", config.username)
    return driver


@pytest.fixture
def disposable_customer(logged_in):
    """14 step dosyasındaki müşteri oluşturma bloğunu TEK yerde toplar.

    Geri dönüşü zor mutasyonlar (Primary değişikliği, silme) barındıran
    testler için her senaryoda taze, tek kullanımlık müşteri sağlar.
    """
    driver = logged_in
    driver.get(config.new_customer_url)
    page = CreateCustomerPage(driver)
    data = CustomerData.random()
    page.create_full_customer(data)      # akışı tek metoda sarmalayın
    log.info("Disposable müşteri oluşturuldu: %s %s", data.first_name, data.last_name)
    return data
```

Bundan sonra bir step dosyası şuna iner:

```python
@given("kullanıcı bir müşterinin Adres sekmesinde kayıtlı bir adres kartı görüntülemektedir",
       target_fixture="address_page")
def user_on_address_tab(driver, disposable_customer):
    return AddressUpdatePage(driver).open_address_tab()
```

**20 satır → 2 satır. 14 dosyada.**

---

## 8. Yol Haritası

### Sprint 1 — Hijyen ve Temel (½ gün, düşük risk)

| # | İş | Süre |
|---|---|---|
| 1 | `README.md` merge conflict'ini çöz | 10 dk |
| 2 | `git restore test-design/` (silme kasıtlı değilse) | 2 dk |
| 3 | `requirements.txt` sürümlerini sabitle + `requirements.lock.txt` | 20 dk |
| 4 | `.env.example` oluştur | 10 dk |
| 5 | `reports/allure-results-*` artık klasörlerini temizle | 5 dk |
| 6 | `project_brain.txt`'i `docs/`'a taşı veya `.gitignore`'a al | 5 dk |
| 7 | `pytest.ini`'ye `--strict-markers -ra --tb=short` + yeni marker'lar ekle | 20 dk |

### Sprint 2 — Ortak Altyapı (2 gün, orta risk)

| # | İş | Etki | Durum |
|---|---|---|---|
| 8 | `utils/config.py` + `.env` kimlik bilgileri | 18 sabit kodlanmış şifre yok olur | ⏳ |
| 9 | `pages/base_page.py` + 13 sınıfı ona bağla | Timeout tek yerden; stale koruması her yerde | ✅ `ecf6251` |
| 10 | `utils/text.py` (Türkçe katlama dışarı çıkar) | Dil bağımsızlığı tüm projede kullanılabilir | ⏳ |
| 11 | `utils/logger.py` | CI'da hata ayıklama mümkün olur | ⏳ |
| 12 | `conftest.py`'ye `logged_in` fixture'ı | 17 dosyadaki login tekrarı biter | ⏳ |

### Sprint 3 — Tekrarın Ortadan Kaldırılması (2 gün, orta risk)

| # | İş | Etki | Durum |
|---|---|---|---|
| 13 | `conftest.py`'ye `disposable_customer` fixture'ı | 14 dosyada 20 satır → 2 satır | ⏳ |
| 14 | `utils/test_data.py` + `FIELD_LIMITS` | SDA senaryoları tek kaynaktan beslenir | ⏳ |
| 15 | `utils/waits.py`; poll döngülerini `poll_until`'e taşı | Niyet kodda görünür olur | ✅ Faz 2 |
| 15b | `create_customer`'daki 3 sabit beklemeyi `wait_for_dom_settled`'a taşı | CI'da 300ms varsayımı kırılmaz | ⏳ CI öncesi |
| 16 | Step'lerdeki ~48 çıplak `WebDriverWait`'i page metotlarına taşı | Katman ihlali biter | ⏳ |
| 17 | `create_customer_page.py`'yi 3 sınıfa böl | 735 satırlık dosya biter | ⏳ |

### Sprint 4 — CI/CD ve Ölçek (2 gün, yüksek değer)

| # | İş | Etki |
|---|---|---|
| 18 | `.github/workflows/tests.yml` — her PR'da smoke, gecelik full | Framework gerçek bir kalite kapısı olur |
| 19 | `pytest-rerunfailures` ekle (`--reruns 2`) | Flaky ile gerçek hata ayrışır |
| 20 | Allure'a `@allure.severity`, `epic`, `story` etiketleri | Rapor gruplanabilir hale gelir |
| 21 | `utils/api_client.py` ile kurulumu API'ye taşı | Koşum süresi **~%60 azalır** |
| 22 | Test izolasyonu (sepet temizleme) → sonra `pytest-xdist` | Paralel koşum güvenli hale gelir |

### Sprint 5 — Kapsam

| # | İş |
|---|---|
| 23 | `kesif_testi.txt`'teki 106 senaryoyu implemente et (o dosyadaki öncelik sırasıyla) |

---

## 9. Örnek CI İş Akışı

`.github/workflows/tests.yml`:

```yaml
name: UI Tests

on:
  pull_request:
  schedule:
    - cron: "0 2 * * *"       # her gece 02:00 - tam regresyon
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 45
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip

      - name: Bağımlılıkları kur
        run: pip install -r requirements.txt

      - name: Testleri çalıştır
        env:
          BASE_URL: ${{ secrets.BASE_URL }}
          CRM_USERNAME: ${{ secrets.CRM_USERNAME }}
          CRM_PASSWORD: ${{ secrets.CRM_PASSWORD }}
          HEADLESS: "true"
        run: |
          # PR'da yalnızca smoke, gecelik koşumda tam regresyon
          MARKS=$([ "${{ github.event_name }}" = "pull_request" ] && echo "smoke" || echo "not lockout")
          pytest -m "$MARKS" --reruns 2 --reruns-delay 1 -ra

      - name: Allure sonuçlarını sakla
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: allure-results
          path: reports/allure-results

      - name: Başarısızlık kanıtlarını sakla
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: failure-evidence
          path: |
            reports/report.html
            reports/logs/
```

---

## 10. Ölçülebilir Hedefler

Bu yol haritası tamamlandığında beklenen durum:

| Ölçüt | İlk | **Güncel** | Hedef |
|---|---|---|---|
| Elle `WebDriverWait` kuran page sınıfı | 11 | ✅ **0** | 0 |
| `BasePage` alt sınıfı | 0 / 18 | ✅ **18 / 18** | 18 / 18 |
| `ignored_exceptions` korumalı sayfa | 2 / 13 | ✅ **13 / 13** | 13 / 13 |
| Zaman aşımı yönetim noktası | 11 dosya | ✅ **1 env** | 1 |
| Page içinde elle yazılmış poll döngüsü | 2 | ✅ **0** | 0 |
| Page içinde sabit `time.sleep` | 3 | 3 | **0** (CI öncesi) |
| `utils/` modül sayısı (ayrıca aşağıda) | 1 | ✅ **2** | 8 |
| Page içinde `assert` | 11 | ✅ **6** | 6 (3 guard + 3 tanısal) |
| En büyük page dosyası (satır) | 735 | 735 | **~250** (Faz 4) |
| Sabit kodlanmış şifre sayısı | 18 | 18 | **0** |
| Login kodunun tekrarlandığı dosya | 17 | 17 | **1** (conftest) |
| Disposable müşteri bloğunun tekrarı | 14 | 14 | **1** (fixture) |
| Step katmanında çıplak `WebDriverWait` | ~48 | ~48 | **0** |
| `test_data/` içerik | boş | boş | Alan sınırları + veri fabrikası |
| Sürümü sabitlenmiş bağımlılık | 0 / 8 | 0 / 8 | **8 / 8** |
| CI koşumu | yok | yok | Her PR + gecelik |
| Tam regresyon süresi | ~50 dk | ~53 dk | **~20 dk** (API kurulum + paralel) |
| Bilinen kırmızı test | 10 | **8** | 6 (yalnızca kasıtlı) |

> Tam regresyon süresi Faz 1'de düşmedi — düşmesi de beklenmiyordu.
> `BasePage` bir **yapı** iyileştirmesidir; süre kazancı API tabanlı
> kurulum ve paralelleştirmeden (Sprint 4) gelecek.

---

## 11. Kapanış Değerlendirmesi

Bu framework'ün **temel mühendislik kararları doğru.** POM anlaşılmış, locator stratejisi
sağlam, dil bağımsızlığı bilinçli, dinamik bekleme disiplini var, kusur triyajı olgun.
Bunlar öğretilmesi zor şeylerdir ve zaten mevcut.

Eksik olan şey **soyutlama katmanı** — ve bu, öğretilmesi kolay ama fark edilmesi zor bir
boşluktur, çünkü framework onsuz da çalışır. Sadece her yeni feature'da biraz daha yavaş,
biraz daha kırılgan çalışır.

Eğer bu listeden **yalnızca üç şey** yapılacaksa:

1. ~~**`pages/base_page.py`** — 11 kez tekrarlanan wait kurulumunu bitirir.~~
   ✅ **Faz 1'de yapıldı** (`ecf6251`). POM 6 → 8, kararlılık 5 → 6.
2. **`utils/config.py` + `conftest.py`'ye `logged_in` ve `disposable_customer`
   fixture'ları** — 18 sabit kodlanmış şifreyi, 17 dosyadaki login tekrarını ve
   14 dosyadaki müşteri oluşturma bloğunu tek yerde toplar. (~1.5 gün)
3. **CI iş akışı** — framework'ü kişisel bir araçtan takım kalite kapısına
   dönüştürür. (~yarım gün)

Kalan iki madde, toplam iki günlük iş karşılığında olgunluğu
**4.1/10'dan yaklaşık 7/10'a** taşır.

### Faz 1'den çıkan ders

Refactor'un başarısı tek bir karara dayandı: **önce baseline'ı doğrulamak.**
`bugsbunnyupdated.txt`'teki bilinen-kırmızı listesi olmasaydı, koşumlardaki
8 kırmızının "zaten kırmızıydı" mı yoksa "ben mi kırdım" mı olduğunu ayırt
etmek imkansız olurdu ve refactor ya geri alınır ya da körlemesine kabul
edilirdi.

Aynı şekilde, `poll_frequency`'yi "biraz daha iyi olur" diye değiştirmemek
de bilinçli bir karardı. Bir refactor'da **aynı anda hem yapıyı hem
davranışı değiştirmek**, bir sorun çıktığında hangisinin sebep olduğunu
bulmayı imkansız hale getirir.

Bu iki alışkanlık — baseline'ı önce sabitlemek ve tek seferde tek tür
değişiklik yapmak — sonraki fazlarda da korunmalıdır.
