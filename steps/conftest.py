"""Tüm step modüllerinin paylaştığı fixture'lar.

pytest-bdd, step tanımlarını ve fixture'ları normal pytest kurallarıyla
çözer - `steps/` altındaki bu conftest her feature'a otomatik görünür.
Buradan önce projede hiç paylaşılan fixture yoktu: 16 step dosyası aynı
login bloğunu satır satır kopyalamıştı.
"""
import pytest

from pages.login_page import LoginPage
from utils import config


@pytest.fixture
def credentials():
    """Varsayılan test kullanıcısı (ortam değişkeniyle ezilebilir)."""
    return config.USERNAME, config.PASSWORD


@pytest.fixture
def authenticated_driver(driver, base_url, credentials):
    """Giriş yapılmış, müşteri listesine ulaşmış bir sürücü döndürür.

    login.feature BİLEREK bu fixture'ı kullanmaz: orada giriş akışının
    kendisi test edildiğinden adımların açık kalması gerekir.
    """
    login_page = LoginPage(driver)
    login_page.open(base_url)
    login_page.login(*credentials)
    # Giriş isteğinin gerçekten tamamlanıp yönlendirmenin oluşmasını
    # bekler - eskiden her dosyada elle kurulan WebDriverWait(driver, 10)
    # ile aynı zaman aşımı (BasePage.DEFAULT_TIMEOUT).
    login_page.wait_for_url_contains("/customers")
    return driver
