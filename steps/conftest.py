"""Tüm step modüllerinin paylaştığı fixture'lar.
 `steps/` altındaki bu conftest her feature'a otomatik görünür.
"""
import pytest

from pages.create_customer_page import CreateCustomerPage
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
    login_page.wait_for_url_contains("/customers")
    return driver


@pytest.fixture
def new_customer(authenticated_driver):
    """Yeni bir müşteri oluşturur ve Müşteri Bilgisi ekranını açar."""
    
    def _create(gender="Erkek", extra_addresses=0):
        authenticated_driver.get(config.url("/customers/new"))
        create_page = CreateCustomerPage(authenticated_driver)
        demographics = create_page.fill_demographic_step_with_faker(gender=gender)
        create_page.click_demographic_next()
        create_page.wait_for_address_step()
        create_page.add_address_with_faker()
        create_page.wait_for_address_saved()
        for _ in range(extra_addresses):
            create_page.add_address_with_faker()
            create_page.wait_for_address_saved()
        create_page.click_address_next()
        create_page.wait_for_contact_step()
        create_page.fill_contact_step_with_faker()
        create_page.click_submit()
        create_page.wait_for_navigated_to_customer_info()
        return demographics

    return _create


@pytest.fixture
def disposable_customer(authenticated_driver, new_customer):
    """Tek müşteri gerektiren senaryolar için kısayol.

    Müşteri oluşturulmuş ve Müşteri Bilgisi ekranı açılmış hâlde sürücüyü
    döndürür)
    """
    new_customer()
    return authenticated_driver
