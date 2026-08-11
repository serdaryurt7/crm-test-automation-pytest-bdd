from urllib.parse import urlparse

from faker import Faker
from pytest_bdd import given, scenarios, then, when
from selenium.webdriver.support.ui import WebDriverWait

from pages.address_delete_page import AddressDeletePage
from pages.billing_account_create_page import BillingAccountCreatePage
from pages.create_customer_page import CreateCustomerPage
from pages.login_page import LoginPage

scenarios("address_delete.feature")

fake = Faker("tr_TR")


def _create_fresh_customer_and_open_address_tab(driver, base_url):
    # Adres silme GERİ DÖNÜŞÜ OLMAYAN bir mutasyon olduğundan HER SENARYO
    # için fresh, tek kullanımlık bir disposable müşteri create_customer
    # akışıyla oluşturuluyor - address_update/address_add.feature'da
    # kurulan desenle tutarlı, tam bağımsızlık ve tekrarlanabilirlik için.
    login_page = LoginPage(driver)
    login_page.open(base_url)
    login_page.login("demo", "Password123")
    WebDriverWait(driver, 10).until(lambda d: "/customers" in d.current_url)

    origin = urlparse(driver.current_url)
    driver.get(f"{origin.scheme}://{origin.netloc}/customers/new")
    create_page = CreateCustomerPage(driver)
    create_page.fill_demographic_step_with_faker(gender="Erkek")
    create_page.click_demographic_next()
    create_page.wait_for_address_step()
    create_page.add_address_with_faker()
    create_page.wait_for_address_saved()
    create_page.click_address_next()
    create_page.wait_for_contact_step()
    create_page.fill_contact_step_with_faker()
    create_page.click_submit()
    create_page.wait_for_navigated_to_customer_info()

    return AddressDeletePage(driver)


def _new_address_args():
    return fake.street_name(), fake.building_number(), fake.sentence(nb_words=4)


@given("kullanıcı, birden fazla adresi olan bir müşterinin adres kartını görüntülemektedir", target_fixture="address_page")
def user_on_multi_address_customer(driver, base_url):
    page = _create_fresh_customer_and_open_address_tab(driver, base_url)
    page.add_new_address_and_wait_for_card(*_new_address_args())
    return page


@when('kullanıcı kart menüsünden "Sil"i seçer')
def user_selects_delete_from_card_menu(address_page):
    address_page.delete_last_added_card()


@then("sistem adresi kalıcı olarak siler (sayfa yenilense dahi adres listede görünmez)")
def system_permanently_deletes_address(address_page):
    assert address_page.wait_for_deletion_persisted_after_reload()


@given('kullanıcı "Sil" seçeneğine tıklamıştır', target_fixture="address_page")
def user_has_clicked_delete_option(driver, base_url):
    page = _create_fresh_customer_and_open_address_tab(driver, base_url)
    page.add_new_address_and_wait_for_card(*_new_address_args())
    page._count_before_delete = page.get_card_count()
    page.delete_last_added_card()
    return page


@then("herhangi bir onay penceresi GÖRÜNTÜLENMEZ")
def no_confirm_dialog_displayed(address_page):
    assert not address_page.is_confirm_dialog_present()


@then("kart listeden anında kaldırılır")
def card_removed_instantly(address_page):
    assert address_page.get_card_count() == address_page._count_before_delete - 1


@given("müşterinin yalnızca 1 kayıtlı adresi vardır", target_fixture="address_page")
def customer_has_single_address(driver, base_url):
    # Fresh müşteri create_customer wizard'ı sırasında zaten TAM OLARAK
    # 1 adresle oluşturuluyor - ek bir adım gerekmiyor.
    return _create_fresh_customer_and_open_address_tab(driver, base_url)


@when("kullanıcı adres kartı menüsünü açar")
def user_opens_address_card_menu(address_page):
    address_page.open_card_menu()


@then("Delete seçeneği pasif (disabled) olarak görüntülenir")
def delete_option_displayed_disabled(address_page):
    delete_option = address_page.driver.find_elements(*address_page.ADDRESS_CARD_DELETE)[0]
    assert not delete_option.is_enabled()


@then("tıklansa dahi adres silinemez")
def address_not_deleted_even_if_clicked(address_page):
    count_before = address_page.get_card_count()
    address_page.attempt_click_disabled_delete_option()
    assert address_page.get_card_count() == count_before


@given("müşterinin birden fazla adresi ve Primary işaretli biri vardır", target_fixture="address_page")
def customer_has_multiple_addresses_with_primary(driver, base_url):
    page = _create_fresh_customer_and_open_address_tab(driver, base_url)
    page.add_new_address_and_wait_for_card(*_new_address_args())
    return page


@when("Primary adres silinir")
def primary_address_is_deleted(address_page):
    address_page.delete_primary_card()


@then("kalan adreslerden birinin otomatik Primary olup olmadığı doğrulanır")
def verify_remaining_address_auto_primary(address_page):
    assert address_page.is_remaining_address_auto_primary()


@given("bir adres silinmiştir", target_fixture="stale_delete_context")
def an_address_has_been_deleted(driver, base_url):
    page = _create_fresh_customer_and_open_address_tab(driver, base_url)
    page.add_new_address_and_wait_for_card(*_new_address_args())
    stale_button = page.delete_last_added_card()
    return page, stale_button


@when("kullanıcı aynı adresi (artık silinmiş, stale bir referansla) tekrar silmeyi dener", target_fixture="duplicate_delete_result")
def user_attempts_to_delete_same_address_again(stale_delete_context):
    page, stale_button = stale_delete_context
    return page, page.attempt_duplicate_delete_with_stale_reference(stale_button)


@then("sistem ikinci denemeyi güvenli şekilde reddeder, uygulama tutarlı durumda kalır")
def second_attempt_safely_rejected(duplicate_delete_result):
    page, was_safely_rejected = duplicate_delete_result
    assert was_safely_rejected
    assert page.is_app_still_functional()


@given("bir adres, aktif bir Fatura Hesabının hizmet adresi olarak kullanılmaktadır", target_fixture="service_address_context")
def address_used_as_active_billing_account_service_address(driver, base_url):
    # ÖNEMLİ: hizmet adresi olarak billing-account formunun KENDİ "Yeni
    # Adres Ekle" alt-formuyla eklenen bir adres KULLANILMIYOR - canlı
    # keşifte bulundu ki O YOL üzerinden eklenen adres, sayfa tamamen
    # yenilendikten sonra bile Adres sekmesinin gerçek listesinde HİÇ
    # görünmüyor (kalıcı olarak persist edilmiyor). Bu yüzden Adres
    # sekmesinin KENDİ (address_add.feature'da doğrulanmış) "Yeni Adres
    # Ekle" akışıyla GERÇEK, kalıcı bir 2. adres oluşturulup, fatura
    # hesabı formunda BU adres hizmet adresi olarak seçiliyor.
    page = _create_fresh_customer_and_open_address_tab(driver, base_url)
    page.add_new_address_and_wait_for_card(*_new_address_args())
    service_address_title = page.get_all_card_titles()[-1]

    account_page = BillingAccountCreatePage(driver)
    account_page.click_create_account()
    titles_in_form = account_page.get_address_card_titles()
    target_index = titles_in_form.index(service_address_title)
    account_page.select_service_address_by_index(target_index)
    account_page.fill_account_name(fake.word().title())
    account_page.fill_account_description(fake.sentence(nb_words=3))
    account_page.click_save()
    account_page.wait.until(lambda d: len(d.find_elements(*account_page.ACCOUNT_ROW)) > 0)

    delete_page = AddressDeletePage(driver)
    return delete_page, service_address_title


@when("kullanıcı bu adresi silmeyi dener")
def user_attempts_to_delete_the_service_address(service_address_context):
    delete_page, service_address_title = service_address_context
    target_index = delete_page.get_all_card_titles().index(service_address_title)
    delete_page.delete_card_at_index(target_index)


@then("sistemin gerçek davranışı doğrulanır: adres herhangi bir engelleme veya uyarı olmadan serbestçe silinir")
def address_deleted_freely_without_blocking(service_address_context):
    # Canlı doğrulandı: sistem şu an bu ilişkiyi (adres <-> aktif Fatura
    # Hesabı'nın hizmet adresi) HİÇBİR şekilde korumuyor - engelleme
    # diyaloğu/uyarı mesajı YOK, silme sessizce ve tamamen başarılı
    # oluyor. Bu, olası bir veri bütünlüğü açığı (hesap artık var olmayan
    # bir adrese referans veriyor olabilir) olarak dev ekibine/PO'ya
    # AYRICA bildirilmesi gereken bir bulgu - ama manuel case'in kendisi
    # "sistemin davranışı doğrulanır" diyerek üç olası dalı (engelleme/
    # uyarı/serbest silme) GÖZLEMLEMEYİ istediğinden, bu test GERÇEK
    # (gözlemlenen) davranışı doğruluyor, kasıtlı kırmızı DEĞİL.
    delete_page, service_address_title = service_address_context
    assert not delete_page.is_confirm_dialog_present()
    assert service_address_title not in delete_page.get_all_card_titles()
