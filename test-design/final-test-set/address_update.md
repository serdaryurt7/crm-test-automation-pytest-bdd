# UC-EACRML-006 — Müşteri Adresinin Güncellenmesi — Konsolide Final Test Seti

## Durum Özeti

- Kaynak: `features/address_update.feature`'daki 9 canlı doğrulanmış senaryo (006-05a/b ve 006-06a/b zaten INVEST-Small ilkesine göre ikişer atomik senaryoya bölünmüş durumda — bu turda değiştirilmedi).
- Doküman'ın "006-05 (tek adresli müşteride Primary otomatik/değiştirilemez) eklenmeli" bulgusu zaten 006-07 ile karşılanmış.
- Doküman'ın "006-03 yalnızca Şehir'i test ediyor, diğer alanlar için tekrarlanmalı" bulgusu zaten Sokak/Bina No/Açıklama için Scenario Outline'a genişletilmiş; **Şehir bilerek dışarıda bırakılmış** (aşağıya bkz.).
- **Bu turda YENİ eklenen (canlı doğrulandı — kullanıcının istediği "adres değerleri için sınır değer kontrolleri"):** Sokak ve Bina No alanlarının HTML `maxlength` özniteliği yok; JS ile 500 karakter yazıldığında hiçbir kısıtlama olmadan aynen kabul ediliyor. Açıklama (006-05a/b) ve Hesap Adı (010-09a/b) alanlarında zaten belgelenmiş "metin alanlarında üst karakter sınırı yok" sistemik bulgusunun üçüncü/dördüncü örneği.

## Gherkin — Final Senaryo Seti

```gherkin
Feature: Müşteri Adresinin Güncellenmesi

  Background:
    Given kullanıcı bir müşterinin Adres sekmesinde kayıtlı bir adres kartı görüntülemektedir

  Scenario: TC-EACRML-006-01 - Adres sekmesinde kayıtlı bir adres kartında Edit seçeneğiyle formun mevcut bilgilerle ön-dolu açılması
    When kullanıcı kart menüsünden "düzenle" seçeneğini seçer
    Then form Şehir, Sokak, Bina No, Açıklama alanlarıyla önceden dolu açılır

  Scenario: TC-EACRML-006-02 - Şehir/Sokak/Bina No alanları güncellenip kaydedildiğinde kartın yeni bilgilerle yenilenmesi
    Given kullanıcı adres düzenleme formundadır
    When Sokak/Bina No alanları değiştirilip Kaydet'e tıklanır
    Then kart yeni bilgilerle güncellenir

  Scenario Outline: TC-EACRML-006-03 - Güncelleme formunda zorunlu alan boşaltıldığında Kaydet butonunun pasif kalması
    Given kullanıcı adres düzenleme formundadır
    When "<alan>" alanı boşaltılır
    Then Kaydet butonu pasif kalır

    Examples:
      | alan     |
      | Sokak    |
      | Bina No  |
      | Açıklama |

  Scenario: TC-EACRML-006-04 - Güncelleme formunda İptal edilince adres kartının değişmeden kalması
    Given kullanıcı adres düzenleme formunda değişiklik yapmıştır
    When İptal butonuna tıklanır
    Then kart eski bilgileriyle kalır

  Scenario: TC-EACRML-006-05a - Adres Açıklaması Alanının Herhangi Bir Üst Karakter Sınırı Olmadan Uzun Metni Kabul Etmesi
    Given kullanıcı adres düzenleme formundadır
    When Açıklama alanına 3000 karakterlik bir metin girilir
    Then alan girilen metnin tamamını kabul eder

  Scenario: TC-EACRML-006-05b - Adres Açıklaması Alanının Tanımlı Bir Üst Karakter Sınırını Aşan Girişi Reddetmesi
    Given kullanıcı adres düzenleme formundadır
    When Açıklama alanına 3000 karakterlik bir metin girilir
    Then alan tanımlı karakter sınırını aşan girişi kabul etmez

  Scenario: TC-EACRML-006-06a - Birden Fazla Adresten İkincisi Primary Seçildiğinde Anlık Olarak Yalnızca Onun Primary Kalması
    Given müşterinin birden fazla adresi vardır
    When kullanıcı ikinci adresi Primary olarak işaretler
    Then yalnızca bu adres Primary görüntülenir, öncekinin işareti anlık olarak kalkar

  Scenario: TC-EACRML-006-06b - Primary Adres Değişikliğinin Sayfa Yenilense Dahi Kalıcı Olarak Korunması
    Given müşterinin birden fazla adresi vardır
    When kullanıcı ikinci adresi Primary olarak işaretler
    Then sayfa yenilendiğinde de yalnızca ikinci adres Primary olarak kalır

  Scenario: TC-EACRML-006-07 - Tek Adresli Müşteride Primary Adres Seçeneğinin Otomatik Seçili ve Değiştirilemez Olması
    Then tek adres otomatik olarak Primary işaretlidir
    And değiştirilecek başka bir adres seçeneği bulunmadığından bu işaret değişmez

  Scenario: TC-EACRML-006-08 - Adres Kartı Üzerinde Bilgilerin "Şehir, Sokak, No" Formatında Eksiksiz Görüntülenmesi
    Then kart başlığı "Şehir, Sokak, No" formatında ve açıklama eksiksiz görüntülenir

  Scenario: TC-EACRML-006-09 [YENİ - Sınır Değer] - Sokak Alanının Herhangi Bir Üst Karakter Sınırı Olmadan Uzun Metni Kabul Etmesi
    # Canlı doğrulandı: address-street input'unun HTML maxlength özniteliği
    # yok - 500 karakterlik bir değer (native value-setter ile) tam olarak
    # kabul ediliyor.
    Given kullanıcı adres düzenleme formundadır
    When Sokak alanına 500 karakterlik bir metin girilir
    Then alan girilen metnin tamamını kabul eder

  Scenario: TC-EACRML-006-10 [YENİ - Sınır Değer] - Bina No Alanının Herhangi Bir Üst Karakter Sınırı Olmadan Uzun Metni Kabul Etmesi
    # Canlı doğrulandı: address-building input'unun HTML maxlength özniteliği
    # yok - 500 karakterlik bir değer (native value-setter ile) tam olarak
    # kabul ediliyor. Bina No'nun ayrıca serbest biçimli (alfanümerik + özel
    # karakter) olduğu TC-EACRML-007-04'te zaten doğrulanmış durumda.
    Given kullanıcı adres düzenleme formundadır
    When Bina No alanına 500 karakterlik bir metin girilir
    Then alan girilen metnin tamamını kabul eder
```

## Notlar

- **Şehir bilerek sınır-değer / zorunlu-alan-boşaltma kapsamı dışında tutuldu:** Şehir bir combobox'tır (81 il listesinden seçim, serbest metin girişi yok — bkz. TC-EACRML-007-06); önceden dolu bir seçimi "boşaltmak" veya içine uzun bir metin yazmak yapısal olarak mümkün değil. Bu, `pages/address_update_page.py`'de zaten canlı doğrulanmış ve belgelenmiş bir tasarım kararı, tekrar test edilmesine gerek yok.
- **Sistemik bulgu (konsolide):** Açıklama (006-05b), Hesap Adı (010-09b) ve şimdi Sokak/Bina No (006-09/10) — bu uygulamadaki serbest metin input'larının HİÇBİRİNDE üst karakter sınırı yok. Dört ayrı "defekt" olarak değil, BA/dev'e **tek bir konsolide bulgu** ("metin alanlarında maxlength validasyonu eksik") olarak iletilmesi önerilir.
