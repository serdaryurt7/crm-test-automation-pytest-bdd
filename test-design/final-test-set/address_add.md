# UC-EACRML-007 — Yeni Müşteri Adresinin Eklenmesi — Konsolide Final Test Seti

## Durum Özeti

- Kaynak: `features/address_add.feature`'daki 8 canlı doğrulanmış senaryo. Doküman'ın kendi karşılaştırmasında da belirtildiği gibi bu UC dokümana göre **tam kapsanmış** durumda, ek bir doküman-kaynaklı boşluk yok.
- **Sınır değer kontrolleri kasıtlı olarak buraya DUPLICATE edilmedi:** `pages/address_add_page.py`, `AddressUpdatePage`'den miras alıyor ve kod içi yorumda da doğrulandığı gibi "Yeni Adres Ekle" formu, adres GÜNCELLEME formuyla **aynı DOM/alan setini** kullanıyor. Sokak/Bina No/Açıklama alanlarının maxlength durumu (hiçbiri yok — bkz. `address_update.md` TC-006-05a/b, 006-09, 006-10) bu yüzden aynı bileşen için ikinci kez test edilmiyor; bu DRY kararı INVEST'in "Independent" ilkesiyle çelişmiyor çünkü iki UC farklı bir kod yolunu değil, aynı paylaşılan bileşeni farklı bir giriş noktasından (Add vs Edit) tetikliyor — kapsam tekrarı gerçek bir risk azaltımı sağlamıyor.

## Gherkin — Final Senaryo Seti

```gherkin
Feature: Yeni Müşteri Adresinin Eklenmesi

  Scenario: TC-EACRML-007-01 - Adres sekmesinde "Yeni Adres Ekle" ile mevcut müşteriye ek bir adres kaydedilmesi
    Given kullanıcı bir müşterinin Adres sekmesindedir
    When kullanıcı "Yeni Adres Ekle" butonuna tıklayıp formu doldurup Save'e tıklar
    Then sistem gerçek bir POST isteğiyle (…/addresses) yeni adresi kaydeder

  Scenario: TC-EACRML-007-02 - Eklenen yeni adresin mevcut adres(ler)i silmeden ayrı bir kart olarak listeye eklenmesi
    Given müşterinin zaten kayıtlı bir adresi vardır
    When kullanıcı yeni bir adres ekler
    Then önceki kart silinmez, yeni adres AYRI bir kart olarak eklenir

  Scenario Outline: TC-EACRML-007-03 - Zorunlu alanlardan biri boşken Save butonunun pasif kalması
    Given kullanıcı yeni adres formundadır
    When "<alan>" alanı boşaltılır
    Then Save butonu pasif kalır

    Examples:
      | alan     |
      | Şehir    |
      | Sokak    |
      | Bina No  |
      | Açıklama |

  Scenario: TC-EACRML-007-04 - Bina/Daire No alanının alfanumerik değer kabul etmesi
    Given kullanıcı yeni adres formundadır
    When Bina No alanına "12 D:4" gibi harf+rakam karışık bir değer girilir
    Then değer sorunsuz kabul edilir

  Scenario: TC-EACRML-007-05 - Adres ekleme formu iptal edilirse hiçbir adresin kaydedilmemesi
    Given kullanıcı yeni adres formunu doldurmuştur
    When İptal butonuna tıklanır
    Then hiçbir adres kaydedilmez

  Scenario: TC-EACRML-007-06 - Şehir alanının yalnızca tanımlı 81 ilden biriyle seçilebilmesi
    Given kullanıcı yeni adres formundadır
    When Şehir dropdown'ı açılır
    Then yalnızca 81 il listelenir, serbest metin girişine izin verilmez

  Scenario: TC-EACRML-007-07 - Aynı müşteriye art arda 3 veya daha fazla adres eklenebilmesi
    Given müşterinin 2 kayıtlı adresi vardır
    When kullanıcı 3. bir adres daha ekler
    Then herhangi bir üst sınır hatasıyla karşılaşılmadan 3 adres de listelenir

  Scenario: TC-EACRML-007-08 - Yeni eklenen adresin listede "Şehir, Sokak Adı, No" formatında okunabilir şekilde yer alması
    Given kullanıcı yeni bir adres eklemiştir
    When Adres sekmesi görüntülenir
    Then yeni kart "Şehir, Sokak Adı, No" formatında okunabilir şekilde listede yer alır
```

## Notlar

- `bugsbunny.txt`'de bu UC'ye ait 2 test "triaj gerekiyor" kategorisinde: TC-007-05 (iptal) ve TC-007-08 (format), tam suite koşumlarında ara sıra flake görülmüş ama izole tekrar çalıştırmalarda çoğunlukla PASSED — kalıcı bir regresyon olarak doğrulanmadı, izlenmeye devam edilmeli.
- Adres değerleri için sınır değer kontrolleri → bkz. `address_update.md`.
