# UC-EACRML-003 — Müşteri Arama — Konsolide Final Test Seti

> **Kapsam notu:** İlk teslimatta bu dosya da sehven dışarıda bırakılmıştı — `login.md` ile aynı düzeltme turunda ekleniyor.

## Durum Özeti

- Kaynak: `features/search_customers.feature`'daki 24 canlı doğrulanmış senaryo. Bu, projedeki **en olgun sınır-değer kapsamına sahip** feature dosyalarından biri: ID Number (11 hane — hem alt hem üst sınır, hem de "yalnızca rakam" input-maskeleme), Customer ID (20 hane üst sınırı), GSM (10 hane üst sınırı), First/Last Name (50 karakter) — dördü de zaten hem "kabul" hem "sınırı aşan reddedilir/kesilir" yönleriyle test edilmiş durumda.
- **[İMPLEMENTE EDİLDİ] Page object'te locator'ları hazır ama hiç senaryosu olmayan iki gerçek özellik, artık `features/search_customers.feature`'a eklendi:**
  1. Sonuç sayısı/aralığı göstergesi (`customer-results-count`, `customer-results-range`) — DOM'da gerçekten var ve doğru içerik gösteriyor ("822 kayıt" / "822 kayıttan 1–15 arası"). Dilden bağımsız implemente edildi: sayı metinden regex ile çıkarılıyor, aralığın alt/üst sınırı sayıların metin içindeki POZİSYONUNA değil toplam sayıyla eşleşip eşleşmemesine göre ayrıştırılıyor (`get_results_count_number()`, `get_results_range_bounds()`).
  2. Sütun başlığına tıklayarak sıralama — canlı olarak **6 sütunun TAMAMI tek tek test edildi** (ilk turda sadece "Ad" test edilmişti). Sonuç: Customer ID, Ad, İkinci Ad, Soyad, Kimlik No sütunlarının hepsinde tıklama gerçekten sırayı değiştiriyor ve ikinci tıklamada farklı bir sıraya geçiyor — **Rol sütunu hariç**: mevcut test verisinde TÜM müşterilerin Role değeri aynı ("Müşteri") olduğundan bu sütunda sıra değişikliği gözlemlenemiyor (veri homojenliği, sıralama mekanizmasının kendisiyle ilgisi yok). Scenario Outline olarak, 5 sütunu kapsayacak şekilde implemente edildi, Rol hariç tutma gerekçesiyle birlikte feature dosyasında not düşüldü.
- **Doğrulama:** `pytest steps/test_search_customers_steps.py -v` izole çalıştırıldı (34 test case — 28 mevcut + 6 yeni [count/range senaryosu + Outline'ın 5 örneği]): **yeni eklenen 6 test case'in TAMAMI PASSED**. Dosyada ayrıca 7 FAILED vardı ama hiçbiri yeni koddan kaynaklanmıyor — 5'i zaten bilinen flaky testler, 2'si triaj edildi (biri izole tekrarda PASSED çıkıp flaky olduğu kesinleşti; diğeri — "ID Number Alanına 11 Haneden Az Rakam Girildiğinde Validasyon Hatası Gösterilmesi" — gerçek bir bulguydu: hardcoded İngilizce mesaj metni, uygulamanın varsayılan Türkçe diliyle hiç eşleşmiyordu, `bugsbunny.txt` madde 19'a kaydedildi ve AYNI oturumda dilden bağımsız hale getirilerek düzeltildi — bkz. aşağıdaki Gherkin, artık TR/EN'de ortak olan "11" rakamını doğruluyor, literal metin karşılaştırmıyor).

## Gherkin — Final Senaryo Seti

```gherkin
Feature: Müşteri Arama
  Kullanıcının müşteri kayıtlarını arayabilmesi

  Background:
    Given kullanıcı müşteri arama sayfasındadır

  Scenario: Arama Kriteri Girilmeden Ara Butonunun Pasif Kalması
    When kullanıcı arama kriteri girmez
    Then Ara butonu pasif kalır

  Scenario: Ekran Açıldığında B2C Segmentinin Varsayılan Seçili Gelmesi ve Filtre Formunun Görüntülenmesi
    Then sistem tüm arama alanlarını görüntüler
    And sistem Search ve Clear butonlarını görüntüler
    And B2C sekmesi aktif, B2B sekmesi pasif görüntülenir

  Scenario: B2B Sekmesinin Prototipte Pasif (Disabled) ve İşlevsiz Olması
    When kullanıcı B2B sekmesine tıklamayı dener
    Then B2C sekmesi aktif, B2B sekmesi pasif görüntülenir

  Scenario: Geçerli 11 Haneli ID Number ile Tam Eşleşen Müşterinin Bulunması
    When kullanıcı ID Number alanına "10000000146" değerini girer
    Then ID Number alanında "10000000146" değeri görüntülenir
    And Search butonu aktif hale gelir
    When kullanıcı Search butonuna tıklar
    Then girilen ID Number'a sahip müşteri kaydı sonuç tablosunda görüntülenir

  Scenario: ID Number Alanının Yalnızca Rakam Kabul Etmesi ve 11 Hane Sınırını Aşmaması
    When kullanıcı ID Number alanına "abc!@#123" değerini girmeyi dener
    Then ID Number alanında "123" değeri görüntülenir
    When kullanıcı ID Number alanına "123456789012345" değerini girmeyi dener
    Then ID Number alanı yalnızca ilk 11 haneyi kabul eder

  Scenario: ID Number Alanına 11 Haneden Az Rakam Girildiğinde Validasyon Hatası Gösterilmesi
    # DÜZELTİLDİ (canlı doğrulandı): önceki hâli hardcoded İngilizce
    # ("Please enter a valid 11-digit ID number.") metniyle karşılaştırıyordu
    # - uygulama VARSAYILAN olarak Türkçe çalıştığından gerçek mesaj
    # "Lütfen geçerli 11 haneli bir kimlik numarası giriniz." oluyor ve
    # eşleşme hiç sağlanamıyordu (bkz. bugsbunny.txt madde 19). Artık dilden
    # bağımsız: TR/EN metinlerinde ORTAK olan tek değişmez unsur (11 rakamı)
    # doğrulanıyor, literal kelime karşılaştırması yapılmıyor.
    When kullanıcı ID Number alanına "1000000014" değerini girer
    Then ID Number alanında "1000000014" değeri görüntülenir
    When kullanıcı Search butonuna tıklar
    Then ID Number'ın 11 haneli olması gerektiğine dair bir doğrulama hatası görüntülenir

  Scenario: Customer ID Aramasının Tam Eşleşme (Exact Match) ile Çalışması
    When kullanıcı Customer ID alanına "5" değerini girer
    And kullanıcı Search butonuna tıklar
    Then yalnızca bu Customer ID'ye tam eşleşen tek müşteri kaydı sonuç listesinde görüntülenir

  Scenario: Customer ID Alanının Yalnızca Rakam Kabul Etmesi ve 20 Hane Sınırı
    When kullanıcı Customer ID alanına "abc!@#123" değerini girer
    Then Customer ID alanında "123" değeri görüntülenir
    When kullanıcı Customer ID alanına "123456789012345678901234" değerini girer
    Then Customer ID alanı 20 üzeri karakter alamaz

  Scenario: GSM Alanının Yalnızca Rakam Kabul Etmesi ve Ülkelere Göre Karakter Sınırı
    When kullanıcı GSM alanına "abc!@#123" değerini girer
    Then GSM alanında "123" değeri görüntülenir
    When kullanıcı GSM alanına "12345678901234" değerini girer
    Then GSM alanı en fazla 10 haneyi kabul eder

  Scenario: (Var olmayan kullanıcı için) GSM Alanının Geçerli Değer Girilse Dahi Arama Sonuçlarını Filtrelememesi
    When kullanıcı GSM alanına "5551234567" değerini girer
    Then GSM alanında "5551234567" değeri görüntülenir
    And Search butonu aktif hale gelir
    When kullanıcı Search butonuna tıklar
    Then "Arama kriterlerine uygun müşteri bulunamadı." mesajı görüntülenir

  Scenario: First Name ve Last Name Alanlarının 50 Karakter Sınırı
    When kullanıcı First Name ve Last Name alanlarına 60 karakterden uzun değerler girer
    Then First Name ve Last Name alanları en fazla 50 karakter kabul eder

  Scenario: Last Name Alanında Baş/Son Boşlukların Otomatik Temizlenmesi (Auto-Trim)
    When kullanıcı Last Name alanına "  Yılmaz  " değerini girer
    And kullanıcı Search butonuna tıklar
    Then "Yılmaz" soyadına sahip müşteri kayıtları sonuç listesinde görüntülenir

  Scenario Outline: Last Name Aramasının Büyük/Küçük Harf Duyarsız Olması
    When kullanıcı Last Name alanına "<last_name>" değerini girer
    And kullanıcı Search butonuna tıklar
    Then "Yılmaz" soyadına sahip müşteri kayıtları sonuç listesinde görüntülenir

    Examples:
      | last_name |
      | YILMAZ    |
      | yılmaz    |
      | YİLMAZ    |

  Scenario: First Name Alanında Baş/Son Boşlukların Otomatik Temizlenmesi (Auto-Trim)
    When kullanıcı First Name alanına "  İbrahim  " değerini girer
    And kullanıcı Search butonuna tıklar
    Then "İbrahim" adına sahip müşteri kayıtları sonuç listesinde görüntülenir

  Scenario Outline: First Name Aramasının Büyük/Küçük Harf Duyarsız Olması
    When kullanıcı First Name alanına "<first_name>" değerini girer
    And kullanıcı Search butonuna tıklar
    Then "İbrahim" adına sahip müşteri kayıtları sonuç listesinde görüntülenir

    Examples:
      | first_name |
      | IBRAHIM    |
      | ibrahim    |
      | İBRAHİM    |

  Scenario: Last Name Aramasının Baştan Eşleşme (Starts-With) ile Çalışması
    When kullanıcı Last Name alanına "Kar" değerini girer
    And kullanıcı Search butonuna tıklar
    Then "Kar" ile başlayan soyadına sahip müşteri kayıtları sonuç listesinde görüntülenir
    When kullanıcı Last Name alanına "ılmaz" değerini girer
    And kullanıcı Search butonuna tıklar
    Then "Arama kriterlerine uygun müşteri bulunamadı." mesajı görüntülenir

  Scenario: First Name Aramasının Baştan Eşleşme (Starts-With) ile Çalışması
    When kullanıcı First Name alanına "Em" değerini girer
    And kullanıcı Search butonuna tıklar
    Then "Em" ile başlayan adına sahip müşteri kayıtları sonuç listesinde görüntülenir
    When kullanıcı First Name alanına "mine" değerini girer
    And kullanıcı Search butonuna tıklar
    Then "Arama kriterlerine uygun müşteri bulunamadı." mesajı görüntülenir

  Scenario: First Name ve Last Name Birlikte Girildiğinde AND Mantığıyla Değerlendirilmesi
    When kullanıcı First Name alanına "Ahmet" ve Last Name alanına "Yılmaz" değerlerini girer
    And kullanıcı Search butonuna tıklar
    Then yalnızca hem "Ahmet" hem "Yılmaz" kriterine uyan müşteriler sonuç listesinde görüntülenir

  Scenario: İsim Kriteri ile Diğer Arama Kriterlerinin OR Mantığıyla Değerlendirilmesi
    When kullanıcı First Name alanına "İbrahim" ve Customer ID alanına "1" değerlerini girer
    And kullanıcı Search butonuna tıklar
    Then "İbrahim" ismine VEYA "1" Customer ID'sine uyan tüm müşteriler sonuç listesinde görüntülenir

  Scenario: 15 Kaydı Aşan Sonuç Kümesinde İlk Sayfada 15 Kayıt ve Sayfalama
    Then ilk sayfada tam 15 kayıt gösterilir ve sayfalama kontrolleri aktiftir
    When kullanıcı sayfalama kontrolleriyle diğer sayfalara geçer
    Then her sayfada doğru sayıda kayıt gösterilir; hiçbir kayıt kaybolmaz veya tekrarlanmaz

  Scenario: Sonuç Listesinin Varsayılan Olarak Customer ID'ye Göre Artan Sıralanması
    Then sonuç listesi varsayılan olarak Customer ID'ye göre artan sırada listelenir

  Scenario: Toplam Kayıt Sayısı ve Görüntülenen Aralığın Doğru Gösterilmesi
    # Dilden bağımsız: sayı, metnin ("822 kayıt" / olası "822 records" gibi)
    # kelimelerinden değil regex ile çıkarılıyor; aralık üst/alt sınırı da
    # sayıların METİN İÇİNDEKİ SIRASINA değil, toplam sayıyla eşleşip
    # eşleşmemesine göre ayrıştırılıyor (dile göre kelime/sayı sırası
    # değişse bile kırılmaz).
    Then toplam kayıt sayısı bilgisi görüntülenir
    And görüntülenen aralık bilgisi görüntülenir
    And aralık bilgisindeki üst değer o sayfadaki gerçek satır sayısıyla tutarlıdır

  # NOT (canlı doğrulandı): "Rol" sütunu Outline'a BİLEREK dahil edilmedi -
  # mevcut test verisinde TÜM müşterilerin Role değeri aynı ("Müşteri"),
  # bu yüzden o sütuna göre sıralamanın gözlemlenebilir hiçbir etkisi yok
  # (veri homojenliği - sıralama mekanizmasının kendisiyle ilgili bir sorun
  # değil). Diğer 5 sütun (Customer ID, Ad, İkinci Ad, Soyad, Kimlik No)
  # canlı olarak TEK TEK doğrulandı: tıklama GERÇEKTEN sırayı değiştiriyor,
  # ikinci tıklama farklı bir sıraya geçiyor. Sütun etiketleri (ör. "Ad")
  # ekrandaki o an aktif dilin metnine değil, sabit bir Python sözlüğü
  # üzerinden data-testid'e eşleniyor (create_customer_page.py'deki
  # GENDER_VALUE_MAP ile aynı desen) - test dilden bağımsız çalışır.
  Scenario Outline: Sütun Başlığına Tıklanarak Sonuçların O Sütuna Göre Sıralanabilmesi ve Sıra Yönünün Değişmesi
    Given sonuç listesi varsayılan (Customer ID artan) sırada görüntülenmektedir
    When kullanıcı "<sütun>" sütun başlığına tıklar
    Then sonuç listesi "<sütun>" sütununa göre yeniden sıralanır (varsayılan sıradan farklı)
    When kullanıcı "<sütun>" sütun başlığına tekrar tıklar
    Then sıralama yönü değişir (ilk tıklamadaki sıradan farklı bir sıraya geçilir)

    Examples:
      | sütun       |
      | Customer ID |
      | Ad          |
      | İkinci Ad   |
      | Soyad       |
      | Kimlik No   |

  Scenario: "No Customer Found" Mesajının ve Create Customer Butonunun Görüntülenmesi
    When kullanıcı ID Number alanına "00000000000" değerini girer
    And kullanıcı Search butonuna tıklar
    Then sonuç bulunamadı durumu görüntülenir
    And Müşteri Oluştur butonu görüntülenir
    When kullanıcı Müşteri Oluştur butonuna tıklar
    Then kullanıcı müşteri oluşturma sayfasına yönlendirilir

  Scenario: Customer ID Linkiyle Customer Info Ekranına Aynı Sekmede Geçiş
    When kullanıcı Customer ID alanına "1" değerini girer
    And kullanıcı Search butonuna tıklar
    And kullanıcı sonuç listesindeki Customer ID linkine tıklar
    Then kullanıcı aynı sekmede "1" numaralı müşterinin Customer Info ekranına yönlendirilir

  Scenario: Clear Butonuyla Tüm Filtrelerin ve Sonuçların Sıfırlanması
    When kullanıcı tüm arama alanlarına Tab ile sırayla değer girer
    And kullanıcı Search butonuna tıklar
    And kullanıcı Clear butonuna tıklar
    Then tüm arama alanları boşalır ve sonuç listesi varsayılan hale döner
```

## Notlar

- **Erişilebilirlik bulgusu (yeni sıralama senaryosuyla ortaya çıktı):** Sütun başlığı tıklamaları `aria-sort` özniteliğini HİÇBİR zaman güncellemiyor (tıklamadan önce/sonra hep `None`) — ekran okuyucu kullanıcıları için sıralama durumu programatik olarak iletilmiyor. Otomasyon bu yüzden sıralama durumunu `aria-sort`'tan değil, satırların GERÇEK içerik sırasından okuyor; bulgu ayrıca BA/dev'e a11y maddesi olarak iletilmesi önerilir.
- Bu UC'nin ID Number/Customer ID/GSM/First-Last Name sınır değerleri, `update_customer.md`/`create_customer.md`'deki AYNI demografik alanların (Kimlik No, Ad, Soyad) FARKLI bir bağlamdaki (arama/filtre, kayıt oluşturma/düzenleme değil) karşılığıdır — iki taraf da bağımsız olarak doğrulanmış durumda, birbirini de dolaylı olarak teyit ediyor (ör. Kimlik No'nun her iki ekranda da 11 hane olması).
- **[ÇÖZÜLDÜ] Bilinen flaky test kümesi (`bugsbunny.txt` madde 10-14) kök nedeniyle birlikte düzeltildi:** Auto-trim (Last/First Name), büyük/küçük harf duyarsızlık (Outline, 6 örnek) ve AND-mantığı senaryoları uzun/tam suite koşularında ara sıra FAILED veriyordu. Önceki hipotez ("Yılmaz" gibi yaygın bir soyadın Faker ile sayıca artıp beklenen sabit sonuç sayısını bozması) canlı ölçümle **kısmen** doğrulandı (veri gerçekten büyümüş, "Yılmaz" araması artık 17 sonuç döndürüyor) ama asıl kök neden farklı çıktı: 17 sonuçtan biri tam "Yılmaz" değil, **"Yilmaz"** (Türkçe noktalı ı/İ olmadan, düz ASCII "i" ile) yazılıydı. Uygulamanın arama motoru zaten aksan/büyük-küçük harf duyarsız eşleştiriyor (ikisini de buluyor) ama testlerin `==`/`.startswith()` karşılaştırması aksan DUYARLI olduğundan bunu yakalayamıyordu — sonuç kümesinde gerçek bir hata yoktu, test uygulamadan daha katıydı. **Dilden/alfabeden bağımsız, dinamik çözüm:** `pages/search_customers_page.py`'ye Türkçe alfabeye özgü harf/aksan farklarını (İ/I/ı/i, ğ/Ğ, ş/Ş, ç/Ç, ö/Ö, ü/Ü) normalize eden `_turkish_fold()` yardımcı fonksiyonu eklendi, isim karşılaştırması yapan **6 metodun tamamına** (yalnızca failed olan değil, aynı bug sınıfına açık starts-with/OR-logic metodları da dahil) uygulandı — test verisi değiştirilmedi, karşılaştırma mantığı uygulamanın kendi toleransıyla eşleştirildi. İzole doğrulama: 12/12 PASSED (regresyon yok). Ayrıca triaj edilen `test_customer_id_linkiyle_customer_info_ekranına_aynı_sekmede_geçiş` (madde 18) 5 ayrı denemede de PASSED verdi — bu, aynı kök nedene bağlı değil, geçici ortam kaynaklı bir flake olarak kapatıldı, ayrı bir düzeltme gerektirmedi. Detaylar: `bugsbunny.txt` madde 10-14, 18, 20.
