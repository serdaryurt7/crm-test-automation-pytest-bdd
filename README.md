# CRM Test Automation Framework

Selenium + pytest-bdd ile UI test otomasyon iskeleti.

## Klasör Yapısı

- `features/` — Gherkin `.feature` dosyaları (senaryolar). Örnek: `login.feature`
- `steps/` — step definition modülleri (`@given/@when/@then`) ve `scenarios()` bağlantıları. Örnek: `test_login_steps.py`
- `pages/` — Page Object Model sınıfları. Örnek: `login_page.py`
- `test_data/` — test verileri (JSON/YAML/CSV). Şu an boş; ihtiyaç doğdukça doldurulacak
- `utils/` — yardımcı fonksiyonlar (logger, wait helper, screenshot vb.). Şu an boş; ihtiyaç doğdukça doldurulacak
- `conftest.py` — pytest fixture'ları (`driver`, `base_url`)
- `pytest.ini` — pytest/pytest-bdd konfigürasyonu (`pythonpath = .` sayesinde `pages`/`test_data` gibi paketler `steps/` altından import edilebiliyor)
- `.env` — ortam değişkenleri (`BASE_URL`, `BROWSER`, `HEADLESS`)
- `.vscode/settings.json` — Cucumber (Gherkin) Full Support uzantısı ayarları; `.feature` dosyasındaki step'lerden Ctrl+Click ile `steps/` altındaki tanıma gitmeyi sağlar (parametrik `parsers.parse(...)` step'ler dahil)

## Kurulum

```
pip install -r requirements.txt
```

Not: ChromeDriver'ı Selenium 4.6+ kendi "Selenium Manager"ı ile otomatik indirip yönetiyor, ayrı bir driver-manager paketine gerek yok.

## Çalıştırma

```
pytest -v
```

Örnek senaryo (`features/login.feature`): geçerli kullanıcı adı/şifre ile login olup `/customers` sayfasına yönlendirildiğini doğruluyor. `Scenario Outline` + `Examples` tablosu kullanıyor, yeni bir kullanıcı/şifre kombinasyonunu test etmek için `Examples` tablosuna satır eklemek yeterli.

## Raporlama

Her `pytest` çalıştırmasında (`pytest.ini`'deki `addopts` sayesinde) otomatik olarak:

- `reports/report.html` — tek dosyalık, tarayıcıda direkt açılabilen özet rapor (pytest-html)
- `reports/allure-results/` — Allure için ham sonuç verisi (JSON) + her testten sonra eklenen ekran görüntüsü, sayfa kaynağı ve URL (`conftest.py`'deki `driver` fixture'ı bunları `allure.attach` ile ekliyor)

Ham Allure verisini görüntülenebilir bir HTML rapora çevirmek için [Allure CLI](https://allurereport.org/docs/install/) kurulu olmalı:

```
allure generate reports/allure-results -o reports/allure-report --clean
allure open reports/allure-report
```

veya sonucu tek komutla tarayıcıda açmak için:

```
allure serve reports/allure-results
```

**Not:** `reports/` klasörü `.gitignore`'da — üretilen rapor/ekran görüntüsü dosyaları her çalıştırmada değiştiği için repoya commit edilmiyor. CI'da bunları "artifact" olarak saklamak veya bir Allure sunucusuna publish etmek daha sürdürülebilir bir yaklaşım.

## Not

`core/` ve `fixtures/` klasörleri bilinçli olarak eklenmedi (YAGNI): driver/base class ihtiyacı `utils/`'a, fixture'lar `conftest.py`'ye sığıyor. Gerçek ihtiyaç doğduğunda eklenebilir.
