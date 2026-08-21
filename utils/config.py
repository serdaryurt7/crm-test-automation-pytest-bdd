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

BASE_URL = os.getenv("BASE_URL", "http://localhost:4200/login")

USERNAME = os.getenv("CRM_USERNAME", "demo")
PASSWORD = os.getenv("CRM_PASSWORD", "Password123")


def _origin_of(url):
    parts = urlparse(url)
    return f"{parts.scheme}://{parts.netloc}"


APP_ORIGIN = os.getenv("APP_ORIGIN") or _origin_of(BASE_URL)


def url(path):
    """Uygulama origin'ine göre mutlak URL üretir: url("/customers/new")."""
    return f"{APP_ORIGIN}/{path.lstrip('/')}"
