Feature: Kontakt Bilgilerinin Güncellenmesi

  Scenario: TC-EACRML-009-01 - İletişim Kanalı sekmesinde Edit ile Email/Telefon bilgilerinin güncellenip kaydedilmesi
    Given kullanıcı bir müşterinin İletişim Kanalı sekmesindedir
    When Edit ile Email/Mobile Phone alanları güncellenip Kaydet'e tıklanır
    Then güncelleme kaydedilir ve görüntüleme modunda yeni bilgiler yansır

  Scenario: TC-EACRML-009-02 - Geçersiz formatta email girildiğinde uyarı gösterilmesi
    Given kullanıcı düzenleme formundadır
    When Email alanına geçersiz formatta bir değer girilir
    Then geçersiz format hatası gösterilir ve güncelleme gerçekleştirilmez

  Scenario Outline: TC-EACRML-009-03 - Email veya Mobile Phone zorunlu alanı boş bırakıldığında güncellemenin engellenmesi
    Given kullanıcı düzenleme formundadır
    When "<alan>" alanı boşaltılır
    Then ilgili alan hatalı olarak işaretlenir
    And güncelleme gerçekleştirilmez

    Examples:
      | alan          |
      | Email         |
      | Mobile Phone  |

  Scenario: TC-EACRML-009-04 - Mobile Phone alanına tam 8 haneli geçersiz değer girildiğinde doğrulamanın çalışması
    Given kullanıcı düzenleme formundadır
    When Mobile Phone alanına "05551234" (8 haneli) girilir
    Then hata gösterilir ve Kaydet butonu pasif kalır

  Scenario: TC-EACRML-009-05 - Contact Medium sekmesinin açılması ve iletişim bilgilerinin salt okunur görüntülenmesi
    Given müşterinin kayıtlı iletişim bilgileri mevcuttur
    When kullanıcı İletişim Kanalı sekmesini açar
    Then iletişim bilgileri salt okunur (read-only) görüntülenir
    And başlığın yanında Edit ikonu bulunur

  Scenario: TC-EACRML-009-06 - Edit ikonuyla iletişim bilgileri düzenleme formunun açılması
    Given "İletişim Kanalı" sekmesi açıktır ve Edit ikonu görünmektedir
    When kullanıcı Edit ikonuna tıklar
    Then sistem iletişim bilgilerini düzenlemek için formu açar

  Scenario: TC-EACRML-009-07 - Home Phone ve Fax alanlarının opsiyonel olması ve boş bırakılabilmesi
    Given kullanıcı düzenleme formundadır
    When Home Phone ve Fax alanları boş bırakılıp yalnızca zorunlu alanlar doldurulur
    Then güncelleme başarıyla tamamlanır

  Scenario: TC-EACRML-009-08 - Edit formunda İptal edilince girilen değişikliklerin kaydedilmeden atılması
    Given kullanıcı formda değişiklik yapmıştır
    When İptal butonuna tıklanır
    Then değişiklikler kaydedilmez, önceki bilgiler korunur

  Scenario: TC-EACRML-009-09 - Aynı email adresinin başka bir müşteride zaten kayıtlı olması durumunda güncellemenin reddedilmesi
    Given müşterinin dışında (başka bir müşteride) zaten kayıtlı bir email vardır
    When kullanıcı bu emaili Email alanına girer
    Then sistem güncellemeyi reddeder, ilgili alan hatalı olarak işaretlenir

  Scenario: TC-EACRML-009-10 - Ülke kodu (+90) sabit alanının telefon numarasından bağımsız olarak değişmemesi
    Given kullanıcı düzenleme formundadır
    When telefon numarası değiştirilir
    Then Mobile/Home Phone/Fax alanlarının önünde sabit "+90" ülke kodu değişmeden görüntülenmeye devam eder

  Scenario: TC-EACRML-009-11 - Mobile Phone Alanına 9 Haneli (Bir Eksik) Değer Girildiğinde Doğrulama Hatasının Gösterilmesi
    Given kullanıcı düzenleme formundadır
    When Mobile Phone alanına 9 haneli geçerli formatta bir değer girilir
    Then hata gösterilir ve Kaydet butonu pasif kalır

  Scenario: TC-EACRML-009-12 - Mobile Phone Alanına Tam 10 Haneli Değer Girildiğinde Doğrulamanın Başarıyla Geçmesi
    Given kullanıcı düzenleme formundadır
    When Mobile Phone alanına tam 10 haneli geçerli bir değer girilir
    Then herhangi bir doğrulama hatası gösterilmez ve Kaydet butonu aktif hale gelir

  # DİNAMİK + DİLDEN BAĞIMSIZ: 3 farklı telefon alanı (Mobile Phone
  # zorunlu, Home Phone/Fax opsiyonel) AYNI "en fazla 10 hane" input-
  # seviyesi kısıtlamasını paylaşıyor - tek bir Scenario Outline'da
  # konsolide edildi (TC-009-13 + TC-009-15, INVEST/DRY - üç ayrı, neredeyse
  # birebir aynı senaryo yazmak yerine). Kontrol tamamen yapısal (girilen
  # değerin uzunluğu), literal metin/mesaj karşılaştırmıyor.
  Scenario Outline: TC-EACRML-009-13/009-15 - Telefon Alanlarına 10 Haneden Fazla Rakam Girilmeye Çalışıldığında Fazla Hanelerin Kabul Edilmemesi
    Given kullanıcı düzenleme formundadır
    When "<alan>" alanına 11 haneli bir değer girilmeye çalışılır
    Then alan yalnızca ilk 10 haneyi kabul eder

    Examples:
      | alan         |
      | Mobile Phone |
      | Home Phone   |
      | Fax          |

  Scenario: TC-EACRML-009-14 - Email Alanının Çok Uzun Bir Değeri HTML Seviyesinde Bir Üst Karakter Sınırı Olmadan Kabul Etmesi
    Given kullanıcı düzenleme formundadır
    When Email alanına formatça geçerli ama çok uzun (150+ karakter) bir değer girilir
    Then alan girilen değerin tamamını kabul eder, herhangi bir HTML seviyesi kısıtlama uygulanmaz
