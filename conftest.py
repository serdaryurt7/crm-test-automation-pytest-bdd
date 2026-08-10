import html
import os

import allure
import pytest
from dotenv import load_dotenv
from pytest_html import extras
from selenium import webdriver

load_dotenv()


def pytest_bdd_before_step(request, feature, scenario, step, step_func):
    steps = request.node.__dict__.setdefault("bdd_steps", [])
    steps.append((step.keyword.strip(), step.name))


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)

    if report.when != "call":
        return

    steps = getattr(item, "bdd_steps", None)
    if not steps:
        return

    rows = "".join(
        f"<div><strong>{html.escape(keyword)}</strong> {html.escape(text)}</div>" for keyword, text in steps
    )
    report.extras = getattr(report, "extras", []) + [
        extras.html(f"<div style='font-family:monospace'>{rows}</div>")
    ]


def _build_driver(browser, headless):
    if browser == "firefox":
        options = webdriver.FirefoxOptions()
        if headless:
            options.add_argument("--headless")
        return webdriver.Firefox(options=options)

    if browser == "edge":
        options = webdriver.EdgeOptions()
        if headless:
            options.add_argument("--headless=new")
        return webdriver.Edge(options=options)

    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    return webdriver.Chrome(options=options)


@pytest.fixture
def driver(request):
    headless = os.getenv("HEADLESS", "false").lower() == "true"
    browser = os.getenv("BROWSER", "chrome").lower()

    driver = _build_driver(browser, headless)
    driver.maximize_window()
    # maximize_window() OS pencere yoneticisine bagli ve uzun/agir test
    # kosumlarinda (ardarda cok sayida Chrome oturumu) guvenilmez sekilde
    # kucuk bir pencerede kalabiliyor - bu da uygulamanin responsive
    # breakpoint'ini tetikleyip Gender <select>/native date picker gibi
    # elementlerin farkli (mobil) widget'lara donusmesine, sahte test
    # hatalarina yol aciyordu. set_window_size deterministik oldugu icin
    # guvenlik agi olarak ekleniyor.
    driver.set_window_size(1920, 1080)
    driver.implicitly_wait(10)

    yield driver

    test_failed = getattr(getattr(request.node, "rep_call", None), "failed", False)

    try:
        if test_failed:
            with allure.step("Ekran görüntüsü ve sayfa bilgisi eklenir"):
                allure.attach(driver.get_screenshot_as_png(), name="Ekran Görüntüsü", attachment_type=allure.attachment_type.PNG)
                allure.attach(driver.page_source, name="Sayfa Kaynağı", attachment_type=allure.attachment_type.HTML)
                allure.attach(driver.current_url, name="Mevcut URL", attachment_type=allure.attachment_type.TEXT)
    finally:
        driver.quit()


@pytest.fixture
def base_url():
    return os.getenv("BASE_URL", "https://example.com")
