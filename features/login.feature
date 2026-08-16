Feature: Login
  Kullanıcının CRM sistemine giriş yapabilmesi

  Background:
    Given kullanıcı login sayfasındadır

  Scenario Outline: Geçerli Kullanıcı Adı ve Şifre ile Başarılı Giriş
    When "<username>" kullanıcı adı ve "<password>" şifresi ile giriş yapar
    Then kullanıcı başarılı bir şekilde sisteme giriş yapmış olur

    Examples:
      | username | password    |
      | demo     | Password123 |

  Scenario Outline: Hatalı Kullanıcı Adı veya Şifre ile Giriş Denemesi
    When "<username>" kullanıcı adı ve "<password>" şifresi ile giriş yapar
    Then kullanıcı adı veya şifre hatalı uyarısı görüntülenir

    Examples:
      | username | password    |
      | yanlis_kullanici | YanlisSifre123 |

  Scenario Outline: Zorunlu Alan (Username/Password) Boş Bırakıldığında Login Butonunun Pasif Kalması
    When "<username>" kullanıcı adı ve "<password>" şifresi girilir
    Then giriş butonu pasif kalır

    Examples:
      | username | password    |
      | demo     |             |
      |          | Password123 |

  # Bu senaryo "admin-crm" hesabını GERÇEKTEN 15 dakika kilitler.
  # pytest.ini'deki `-m "not lockout"` sayesinde varsayılan koşumdan
  # hariç tutulur; bilinçli olarak çalıştırmak için: pytest -m lockout
  @lockout
  Scenario: 5 Başarısız Giriş Denemesi Sonrası Hesabın 15 Dakika Kilitlenmesi
    When kullanıcı art arda 5 kez hatalı bilgilerle giriş dener
    Then hesap kilitlenir ve doğru bilgilerle bile giriş yapılamaz

  Scenario: Şifre Alanı Karakterlerinin Varsayılan Olarak Maskeli Görüntülenmesi
    When kullanıcı şifre alanına "Password123" değerini girer
    Then şifre karakterleri maskeli görüntülenir

  Scenario: Şifre Alanında Göz İkonu ile Şifreyi Gösterme/Gizleme
    When kullanıcı şifre alanına "Password123" değerini girer
    Then şifre karakterleri maskeli görüntülenir
    When kullanıcı göz ikonuna tıklar
    Then şifre karakterleri düz metin olarak görüntülenir
    When kullanıcı göz ikonuna tekrar tıklar
    Then şifre karakterleri tekrar maskeli görüntülenir

  Scenario: 8 Saatlik Oturum Süresi Dolduğunda Otomatik Login Ekranına Yönlendirme
    When "demo" kullanıcı adı ve "Password123" şifresi ile giriş yapar
    And kullanıcının oturum süresi dolar
    Then kullanıcı otomatik olarak login ekranına yönlendirilir

  Scenario: Username Alanının Auto-Trim Doğrulaması
    When "  demo  " kullanıcı adı ve "Password123" şifresi ile giriş yapar
    Then kullanıcı başarılı bir şekilde sisteme giriş yapmış olur

  Scenario: Tam 50 Karakter Uzunluğunda Kullanıcı Adı ile Sınır Değeri
    When kullanıcı adı ve şifre alanlarına 50 karaktere eşit uzunlukta değerler girilir
    Then her iki alan da en fazla 50 karakter kabul eder

  Scenario: Username ve Password Alanının 50 Karakter Sınırı Doğrulaması
    When kullanıcı adı ve şifre alanlarına 51 karakter uzunluğunda değerler girilir
    Then her iki alan da en fazla 50 karakter kabul eder

  Scenario Outline: Username Doğrulamasının Büyük/Küçük Harf Duyarsız Olması
    When "<username>" kullanıcı adı ve "<password>" şifresi ile giriş yapar
    Then kullanıcı başarılı bir şekilde sisteme giriş yapmış olur

    Examples:
      | username | password    |
      | demo     | Password123 |
      | DEMO     | Password123 |

  Scenario: Kullanıcı Adında Baş/Son Boşlukla Birlikte Farklı Harf Büyüklüğü Kombinasyonuyla Başarılı Giriş
    When "   Demo   " kullanıcı adı ve "Password123" şifresi ile giriş yapar
    Then kullanıcı başarılı bir şekilde sisteme giriş yapmış olur

  Scenario: Hatalı giriş sonrası bilgiler düzeltilip tekrar denendiğinde giriş başarılı olur
    When "yanlis_kullanici" kullanıcı adı ve "YanlisSifre123" şifresi ile giriş yapar
    Then kullanıcı adı veya şifre hatalı uyarısı görüntülenir
    When "demo" kullanıcı adı ve "Password123" şifresi ile giriş yapar
    Then kullanıcı başarılı bir şekilde sisteme giriş yapmış olur

  Scenario Outline: Tanımsız kullanıcı için 5 başarısız denemeden sonra hesap kilitlendi mesajı gösterilmemelidir
    When "<username>" kullanıcı adı ile art arda 5 kez hatalı bilgilerle giriş dener
    Then son hata mesajı "Çok fazla başarısız deneme. Hesabınız 15 dakika süreyle kilitlendi." olmamalıdır

    Examples:
      | username   |
      | admin-123  |

  Scenario: Şifredeki baş/son boşluklar temizlenir ve giriş başarılı olur
    When "demo" kullanıcı adı ve "  Password123  " şifresi ile giriş yapar
    Then kullanıcı başarılı bir şekilde sisteme giriş yapmış olur

  Scenario: Hatalı Giriş Sonrası Bilgiler Düzeltildiğinde Hata Mesajının Kalkması
    When "yanlis_kullanici" kullanıcı adı ve "YanlisSifre123" şifresi ile giriş yapar
    Then kullanıcı adı veya şifre hatalı uyarısı görüntülenir
    When "demo" kullanıcı adı ve "Password123" şifresi girilir
    Then hata mesajı ekrandan kalkar

  Scenario: Her İki Alan Dolu Olduğunda Login Butonunun Aktif Hale Gelmesi
    When "demo" kullanıcı adı ve "" şifresi girilir
    Then giriş butonu pasif kalır
    When "demo" kullanıcı adı ve "Password123" şifresi girilir
    Then giriş butonu aktif hale gelir

  Scenario: Giriş İşlemi Sırasında Login Butonunun Pasifleşmesi
    When "demo" kullanıcı adı ve "Password123" şifresi girilir
    And kullanıcı Login butonuna tıklar
    Then Login butonu pasif duruma geçer

  Scenario Outline: Username ve Password Alanlarına SQL Injection / XSS Payload Girildiğinde Sistemin Etkilenmemesi
    When "<username>" kullanıcı adı ve "<password>" şifresi ile giriş yapar
    Then kullanıcı adı veya şifre hatalı uyarısı görüntülenir
    And herhangi bir script çalıştırılmaz ve yetkisiz erişim sağlanmaz

    Examples:
      | username    | password                  |
      | ' OR '1'='1 | <script>alert(1)</script> |

  Scenario: Zaten Giriş Yapmış Kullanıcının /login Adresini Tekrar Ziyaret Etmesi Durumunda Otomatik Yönlendirme
    When "demo" kullanıcı adı ve "Password123" şifresi ile giriş yapar
    And kullanıcı tarayıcıdan doğrudan login adresine gitmeyi dener
    Then kullanıcı login formu gösterilmeden Müşteri Arama ekranına yönlendirilir

