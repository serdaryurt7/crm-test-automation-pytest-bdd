"""Ortam bağımlı tüm sabitlerin TEK kaynağı.

Buradan önce kimlik bilgileri 17 ayrı step satırında, uygulama origin'i ise
14 ayrı dosyada `urlparse(driver.current_url)` ile yeniden hesaplanıyordu.
Farklı bir ortama (test/staging) veya farklı bir kullanıcıya geçmek 30+
dosyada arama-değiştirme gerektiriyordu; artık ortam değişkeni yetiyor.
"""
import os
from urllib.parse import urlparse

from dotenv import load_dotenv

load_dotenv()

# BASE_URL geri uyumluluk için OLDUĞU GİBİ korunuyor - .env'de login
# yolunu da içeriyor (http://localhost:4200/login) ve LoginPage.open()
# ile test_login_steps.py bu davranışa bağlı.
BASE_URL = os.getenv("BASE_URL", "http://localhost:4200/login")

USERNAME = os.getenv("CRM_USERNAME", "demo")
PASSWORD = os.getenv("CRM_PASSWORD", "Password123")


def _origin_of(url):
    parts = urlparse(url)
    return f"{parts.scheme}://{parts.netloc}"


# DAVRANIŞ NOTU (bilinçli, küçük bir değişiklik): eskiden origin, login
# SONRASINDAKİ canlı `driver.current_url`den türetiliyordu. Bu, BASE_URL'in
# login yolunu da içermesinin yan etkisiydi - tasarım tercihi değil. Artık
# origin yapılandırmadan DETERMİNİSTİK olarak türetiliyor; uygulama testi
# beklenmedik bir host'a yönlendirse dahi istekler yapılandırılan origin'e
# gider. localhost:4200 kurulumunda iki yol da aynı sonucu verir.
APP_ORIGIN = os.getenv("APP_ORIGIN") or _origin_of(BASE_URL)


def url(path):
    """Uygulama origin'ine göre mutlak URL üretir: url("/customers/new")."""
    return f"{APP_ORIGIN}/{path.lstrip('/')}"
