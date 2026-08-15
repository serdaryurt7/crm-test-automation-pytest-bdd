from pytest_bdd import given, parsers, scenarios, then, when

from pages.address_add_page import AddressAddPage
from utils.test_data import new_address_args

scenarios("address_add.feature")


@given("kullanıcı bir müşterinin Adres sekmesindedir", target_fixture="address_page")
def user_on_address_tab(disposable_customer):
    return AddressAddPage(disposable_customer)


@given("müşterinin zaten kayıtlı bir adresi vardır", target_fixture="address_page")
def customer_already_has_one_address(disposable_customer):
    # Fresh müşteri create_customer wizard'ı sırasında zaten TAM OLARAK
    # 1 adresle oluşturuluyor - ek bir adım gerekmiyor.
    return AddressAddPage(disposable_customer)


@given("kullanıcı yeni adres formundadır", target_fixture="address_page")
def user_on_new_address_form(disposable_customer):
    page = AddressAddPage(disposable_customer)
    page.click_add_address()
    return page


@given("kullanıcı yeni adres formunu doldurmuştur", target_fixture="address_page")
def user_filled_new_address_form(disposable_customer):
    page = AddressAddPage(disposable_customer)
    page.snapshot_card_count()
    page.click_add_address()
    page.fill_new_address_form(*new_address_args())
    return page


@given("müşterinin 2 kayıtlı adresi vardır", target_fixture="address_page")
def customer_has_two_addresses(disposable_customer):
    page = AddressAddPage(disposable_customer)
    page.add_new_address_and_wait_for_card(*new_address_args())
    return page


@given("kullanıcı yeni bir adres eklemiştir", target_fixture="address_page")
def user_added_new_address(disposable_customer):
    page = AddressAddPage(disposable_customer)
    page.add_new_address_and_wait_for_card(*new_address_args())
    return page


@when("""kullanıcı "Yeni Adres Ekle" butonuna tıklayıp formu doldurup Save'e tıklar""")
def user_opens_fills_and_saves_new_address(address_page):
    address_page.add_new_address_and_wait_for_card(*new_address_args())


@then("sistem gerçek bir POST isteğiyle (…/addresses) yeni adresi kaydeder")
def system_persists_new_address_via_real_backend_call(address_page):
    assert address_page.wait_for_new_address_persisted_after_reload()


@when("kullanıcı yeni bir adres ekler")
def user_adds_a_new_address(address_page):
    address_page.add_new_address_and_wait_for_card(*new_address_args())


@then("önceki kart silinmez, yeni adres AYRI bir kart olarak eklenir")
def previous_card_not_deleted_new_card_added_separately(address_page):
    assert address_page.is_new_card_added_as_separate_card()


@when(parsers.parse('"{alan}" alanı boşaltılır'))
def user_leaves_field_empty_while_filling_others(address_page, alan):
    address_page.fill_new_address_form(
        *new_address_args(), skip_field=alan
    )


@then("Save butonu pasif kalır")
def save_button_stays_disabled(address_page):
    assert address_page.is_save_button_disabled()


@when(parsers.parse('Bina No alanına "{value}" gibi harf+rakam karışık bir değer girilir'), target_fixture="building_no_test_value")
def user_types_alphanumeric_building_no(address_page, value):
    address_page.type_into_building_no(value)
    return value


@then("değer sorunsuz kabul edilir")
def value_is_accepted_without_error(address_page, building_no_test_value):
    assert address_page.get_building_no_value() == building_no_test_value


@when("İptal butonuna tıklanır")
def user_clicks_cancel(address_page):
    address_page.click_cancel()


@then("hiçbir adres kaydedilmez")
def no_address_is_saved(address_page):
    assert not address_page.is_edit_form_open()
    assert address_page.card_count_matches_snapshot()


@when("Şehir dropdown'ı açılır")
def user_opens_city_dropdown(address_page):
    address_page.open_city_dropdown()


@then("yalnızca 81 il listelenir, serbest metin girişine izin verilmez")
def only_81_provinces_listed_no_free_text(address_page):
    assert address_page.is_city_dropdown_restricted_to_defined_provinces()


@when("kullanıcı 3. bir adres daha ekler")
def user_adds_third_address(address_page):
    address_page.add_new_address_and_wait_for_card(*new_address_args())


@then("herhangi bir üst sınır hatasıyla karşılaşılmadan 3 adres de listelenir")
def three_addresses_listed_without_upper_limit_error(address_page):
    assert address_page.get_card_count() == 3


@when("Adres sekmesi görüntülenir")
def address_tab_is_displayed(address_page):
    assert address_page.get_card_count() >= 1


@then('yeni kart "Şehir, Sokak Adı, No" formatında okunabilir şekilde listede yer alır')
def new_card_is_well_formed_last_in_list(address_page):
    assert address_page.is_new_card_last_and_well_formed()
