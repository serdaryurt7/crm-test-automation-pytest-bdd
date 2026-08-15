# CRM Test Automation Framework

Selenium + pytest-bdd ile UI test otomasyon iskeleti. **214 senaryo**, 17 feature.

## Klasör Yapısı

- `features/` — Gherkin `.feature` dosyaları (senaryolar). Örnek: `login.feature`
- `steps/` — step definition modülleri (`@given/@when/@then`) ve `scenarios()` bağlantıları. Örnek: `test_login_steps.py`
- `steps/conftest.py` — tüm feature'ların paylaştığı fixture'lar (aşağıda)
- `pages/` — Page Object Model sınıfları; hepsi `pages/base_page.py::BasePage`'ten türer
- `utils/` — ortak altyapı: `config.py`, `waits.py`, `test_data.py`, `session.py`
- `test_data/` — dosya tabanlı test verisi (JSON/YAML/CSV) için ayrıldı, şu an boş. Üretilen (Faker) veri `utils/test_data.py`'de
- `conftest.py` — kök fixture'lar (`driver`, `base_url`) ve raporlama hook'ları
- `pytest.ini` — pytest/pytest-bdd konfigürasyonu (`pythonpath = .` sayesinde `pages`/`utils` paketleri `steps/` altından import edilebiliyor)
- `.env` — ortam değişkenleri (repoya dahil DEĞİL, aşağıya bakın)
- `.github/workflows/ci.yml` — statik doğrulama (uygulama gerektirmez) + elle tetiklenen UI koşumu

## Kurulum

```
pip install -r requirements.txt
```

Not: ChromeDriver'ı Selenium 4.6+ kendi "Selenium Manager"ı ile otomatik indirip yönetiyor, ayrı bir driver-manager paketine gerek yok.

## Konfigürasyon

Tüm ortam bağımlı değerler `utils/config.py`'de toplanmıştır ve ortam
değişkeniyle ezilebilir. Kök dizinde bir `.env` dosyası oluşturun:

| Değişken | Varsayılan | Açıklama |
|---|---|---|
| `BASE_URL` | `http://localhost:4200/login` | Login sayfasının tam adresi |
| `APP_ORIGIN` | `BASE_URL`'den türetilir | Uygulama kökü (`http://localhost:4200`) |
| `CRM_USERNAME` | `demo` | Test kullanıcısı |
| `CRM_PASSWORD` | `Password123` | Test kullanıcısının şifresi |
| `BROWSER` | `chrome` | `chrome`, `firefox` veya `edge` |
| `HEADLESS` | `false` | `true` ise tarayıcı görünmez çalışır |
| `DEFAULT_TIMEOUT` | `10` | Sayfa nesnelerinin standart bekleme süresi (sn) |
| `SLOW_TIMEOUT` | `30` | Yavaş işlemler için bekleme süresi (sn) |

> Gerçek bir ortamda (staging/CI) kimlik bilgileri secret olarak
> enjekte edilmeli; `utils/config.py`'deki varsayılanlar yalnızca yerel
> geliştirme kolaylığı içindir.

## Çalıştırma

```
pytest -v                          # tam suite (~55 dk, 214 senaryo)
pytest steps/test_login_steps.py   # tek feature
pytest -m lockout                  # varsayılan koşumdan hariç tutulan testler
```

`lockout` işaretli senaryo `admin-crm` hesabını gerçekten 15 dakika
kilitler; bu yüzden `pytest.ini`'de `-m "not lockout"` ile varsayılan
koşumdan çıkarılmıştır.

**Ön koşul:** testler çalışan bir uygulama gerektirir — frontend
`localhost:4200`, gateway `localhost:8080` (BFF `/bff-service/api/v1/`),
Keycloak `localhost:8180`.

## Paylaşılan Fixture'lar

Yeni bir feature yazarken kurulum kodunu kopyalamayın; `steps/conftest.py`
şunları sunar:

| Fixture | Ne yapar |
|---|---|
| `credentials` | `(kullanıcı adı, şifre)` — `utils/config.py`'den |
| `authenticated_driver` | Giriş yapılmış, müşteri listesine ulaşmış sürücü |
| `new_customer(gender, extra_addresses)` | **Fabrika.** Çağrıldıkça yeni bir tek kullanımlık müşteri oluşturur, demografik bilgilerini döndürür. Aynı test içinde ikinci bir müşteri gerektiğinde tekrar çağrılır (re-login yapmaz) |
| `disposable_customer` | Tek müşteri kısayolu: giriş + bir müşteri oluşturulmuş sürücü |

Tipik kullanım:

```python
@given("kullanıcı bir müşterinin Adres sekmesindedir", target_fixture="address_page")
def user_on_address_tab(disposable_customer):
    return AddressAddPage(disposable_customer)
```

Müşteri **her senaryo için yeniden** oluşturulur (fonksiyon kapsamı).
Mutasyon içeren senaryoların birbirinden bağımsız olması için bu
bilinçli bir tercihtir.

## Raporlama

Her `pytest` çalıştırmasında (`pytest.ini`'deki `addopts` sayesinde) otomatik olarak:

- `reports/report.html` — tek dosyalık, tarayıcıda direkt açılabilen özet rapor (pytest-html)
- `reports/allure-results/` — Allure için ham sonuç verisi (JSON) + başarısız testlerde ekran görüntüsü, sayfa kaynağı ve URL

Ham Allure verisini HTML rapora çevirmek için [Allure CLI](https://allurereport.org/docs/install/) gerekir:

```
allure serve reports/allure-results
```

> **Dikkat:** `addopts` içinde `--clean-alluredir` var. Tam suite koşumundan
> sonra tek bir testi çalıştırmak mevcut raporu SİLER. İzole koşumlarda
> `--alluredir=reports/allure-scratch` ile ayrı bir dizine yönlendirin.

`reports/` klasörü `.gitignore`'da — üretilen dosyalar her çalıştırmada
değiştiği için repoya commit edilmiyor.

## Mimari ve Yol Haritası

- `mimari.md` — katman katman değerlendirme, olgunluk skoru, yapılan refactor fazları
- `bugsbunny.txt` — karşılaşılan test hatalarının kronolojik kaydı (kasıtlı kırmızılar, flaky'ler, kök neden analizleri)
- `kesif_testi.txt` — keşif testi bulguları ve önerilen ek senaryolar
- `project_brain.txt` — projedeki önemli kararların kronolojik kaydı

## Not

`core/` ve `fixtures/` klasörleri bilinçli olarak eklenmedi (YAGNI):
driver/base class ihtiyacı `pages/base_page.py` ve `utils/`'a, fixture'lar
`conftest.py` dosyalarına sığıyor.
