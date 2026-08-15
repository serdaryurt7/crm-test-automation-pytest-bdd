from pytest_bdd import given, parsers, scenarios, then, when
from selenium.webdriver.support.ui import WebDriverWait

from pages.search_customers_page import CustomersPage

scenarios("search_customers.feature")


@given("kullanıcı müşteri arama sayfasındadır", target_fixture="customers_page")
def user_on_customers_page(authenticated_driver):
    return CustomersPage(authenticated_driver)


@when("kullanıcı arama kriteri girmez")
def user_enters_no_search_criteria(customers_page):
    customers_page.clear_all_search_fields()


@then("Ara butonu pasif kalır")
def search_button_disabled(customers_page):
    assert customers_page.is_search_button_disabled()


@then("sistem tüm arama alanlarını görüntüler")
def all_search_fields_visible(customers_page):
    assert customers_page.are_all_search_fields_visible()


@then("sistem Search ve Clear butonlarını görüntüler")
def search_buttons_visible(customers_page):
    assert customers_page.are_search_buttons_visible()


@then("B2C sekmesi aktif, B2B sekmesi pasif görüntülenir")
def b2c_active_b2b_inactive(customers_page):
    assert customers_page.is_b2c_active()
    assert customers_page.is_b2b_inactive()


@when("kullanıcı B2B sekmesine tıklamayı dener")
def user_tries_to_click_b2b(customers_page):
    customers_page.try_click_b2b()


@when(parsers.parse('kullanıcı ID Number alanına "{value}" değerini girer'))
@when(parsers.parse('kullanıcı ID Number alanına "{value}" değerini girmeyi dener'))
def user_enters_identity_number(customers_page, value):
    customers_page.enter_identity_number(value)


@then(parsers.parse('ID Number alanında "{value}" değeri görüntülenir'))
def identity_number_value_shown(customers_page, value):
    assert customers_page.get_identity_number_value() == value


@then("Search butonu aktif hale gelir")
def search_button_enabled(customers_page):
    assert not customers_page.is_search_button_disabled()


@when("kullanıcı Search butonuna tıklar")
@when("kullanıcı Search butonuna tıklamayı dener")
def user_clicks_search_button(customers_page):
    customers_page.submit_search()


@then("girilen ID Number'a sahip müşteri kaydı sonuç tablosunda görüntülenir")
def matching_customer_shown(customers_page):
    customers_page.wait_for_matching_customer()


@then("ID Number alanı yalnızca ilk 11 haneyi kabul eder")
def identity_number_truncated_to_11(customers_page):
    assert len(customers_page.get_identity_number_value()) == 11


@then(parsers.parse('"{message}" mesajı görüntülenir'))
def validation_message_shown(customers_page, message):
    customers_page.wait_for_empty_state_message(message)


@then("sonuç bulunamadı durumu görüntülenir")
def no_results_state_shown(customers_page):
    customers_page.wait_for_no_results_state()


@then("ID Number'ın 11 haneli olması gerektiğine dair bir doğrulama hatası görüntülenir")
def identity_number_length_validation_error_shown(customers_page):
    customers_page.wait_for_identity_number_length_validation_error()


@when(parsers.parse('kullanıcı Customer ID alanına "{value}" değerini girer'))
def user_enters_customer_id(customers_page, value):
    customers_page.enter_customer_id(value)


@then("yalnızca bu Customer ID'ye tam eşleşen tek müşteri kaydı sonuç listesinde görüntülenir")
def matching_customer_id_shown(customers_page):
    customers_page.wait_for_matching_customer_id()


@then(parsers.parse('Customer ID alanında "{value}" değeri görüntülenir'))
def customer_id_value_shown(customers_page, value):
    assert customers_page.get_customer_id_value() == value


@then("Customer ID alanı 20 üzeri karakter alamaz")
def customer_id_rejects_more_than_20_chars(customers_page):
    assert len(customers_page.get_customer_id_value()) == 20


@when(parsers.parse('kullanıcı GSM alanına "{value}" değerini girer'))
def user_enters_gsm(customers_page, value):
    customers_page.enter_gsm(value)


@then(parsers.parse('GSM alanında "{value}" değeri görüntülenir'))
def gsm_value_shown(customers_page, value):
    assert customers_page.get_gsm_value() == value


@then("GSM alanı en fazla 10 haneyi kabul eder")
def gsm_accepts_max_10_digits(customers_page):
    assert len(customers_page.get_gsm_value()) == 10


@when("kullanıcı First Name ve Last Name alanlarına 60 karakterden uzun değerler girer")
def user_enters_long_first_last_name(customers_page):
    customers_page.enter_long_first_last_name()


@then("First Name ve Last Name alanları en fazla 50 karakter kabul eder")
def first_last_name_accept_max_50(customers_page):
    assert len(customers_page.get_first_name_value()) == 50, "First Name alanı 50 karakteri aşıyor"
    assert len(customers_page.get_last_name_value()) == 50, "Last Name alanı 50 karakteri aşıyor"


@when(parsers.parse('kullanıcı Last Name alanına "{value}" değerini girer'))
def user_enters_last_name(customers_page, value):
    customers_page.enter_last_name(value)


@then(parsers.parse('"{last_name}" soyadına sahip müşteri kayıtları sonuç listesinde görüntülenir'))
def last_name_results_shown(customers_page, last_name):
    customers_page.wait_for_last_name_results(last_name)


@when(parsers.parse('kullanıcı First Name alanına "{value}" değerini girer'))
def user_enters_first_name(customers_page, value):
    customers_page.enter_first_name(value)


@then(parsers.parse('"{first_name}" adına sahip müşteri kayıtları sonuç listesinde görüntülenir'))
def first_name_results_shown(customers_page, first_name):
    customers_page.wait_for_first_name_results(first_name)


@then(parsers.parse('"{prefix}" ile başlayan soyadına sahip müşteri kayıtları sonuç listesinde görüntülenir'))
def last_name_prefix_results_shown(customers_page, prefix):
    customers_page.wait_for_last_name_results_starting_with(prefix)


@then(parsers.parse('"{prefix}" ile başlayan adına sahip müşteri kayıtları sonuç listesinde görüntülenir'))
def first_name_prefix_results_shown(customers_page, prefix):
    customers_page.wait_for_first_name_results_starting_with(prefix)


@when(parsers.parse('kullanıcı First Name alanına "{first_name}" ve Last Name alanına "{last_name}" değerlerini girer'))
def user_enters_first_and_last_name(customers_page, first_name, last_name):
    customers_page.enter_first_name(first_name)
    customers_page.enter_last_name(last_name)


@then(parsers.parse('yalnızca hem "{first_name}" hem "{last_name}" kriterine uyan müşteriler sonuç listesinde görüntülenir'))
def and_logic_results_shown(customers_page, first_name, last_name):
    customers_page.wait_for_results_matching_first_and_last_name(first_name, last_name)


@when(parsers.parse('kullanıcı First Name alanına "{first_name}" ve Customer ID alanına "{customer_id}" değerlerini girer'))
def user_enters_first_name_and_customer_id(customers_page, first_name, customer_id):
    customers_page.enter_first_name(first_name)
    customers_page.enter_customer_id(customer_id)


@then(parsers.parse('"{first_name}" ismine VEYA "{customer_id}" Customer ID\'sine uyan tüm müşteriler sonuç listesinde görüntülenir'))
def or_logic_results_shown(customers_page, first_name, customer_id):
    customers_page.wait_for_results_matching_first_name_or_customer_id(first_name, customer_id)


@then("ilk sayfada tam 15 kayıt gösterilir ve sayfalama kontrolleri aktiftir")
def first_page_shows_exactly_15_sorted_with_active_pagination(customers_page):
    assert customers_page.get_row_count() == 15, "İlk sayfada 15 kayıt gösterilmiyor"
    assert customers_page.is_customer_id_column_sorted_ascending(), "Kayıtlar Customer ID'ye göre artan sırada değil"
    assert customers_page.is_pagination_active(), "Sayfalama kontrolleri aktif değil"


@when("kullanıcı sayfalama kontrolleriyle diğer sayfalara geçer")
def user_navigates_to_next_page(customers_page):
    customers_page.capture_current_page_customer_ids()
    customers_page.go_to_next_page()


@then("her sayfada doğru sayıda kayıt gösterilir; hiçbir kayıt kaybolmaz veya tekrarlanmaz")
def next_page_shows_correct_records_without_loss_or_duplication(customers_page):
    comparison = customers_page.get_next_page_record_comparison()
    assert comparison["next_page_ids"], "Sonraki sayfada hiç kayıt yok"
    assert not comparison["overlapping_ids"], (
        "Sonraki sayfada önceki sayfayla çakışan (tekrarlanan) kayıtlar var: "
        f"{sorted(comparison['overlapping_ids'])}"
    )


@then("sonuç listesi varsayılan olarak Customer ID'ye göre artan sırada listelenir")
def default_sort_is_customer_id_ascending(customers_page):
    assert customers_page.is_customer_id_column_sorted_ascending()


@then("Müşteri Oluştur butonu görüntülenir")
def create_customer_button_visible(customers_page):
    assert customers_page.is_create_customer_button_visible()


@when("kullanıcı Müşteri Oluştur butonuna tıklar")
def user_clicks_create_customer_button(customers_page):
    customers_page.click_create_customer_button()


@then("kullanıcı müşteri oluşturma sayfasına yönlendirilir")
def redirected_to_create_customer_page(driver):
    WebDriverWait(driver, 10).until(lambda d: "/customers/new" in d.current_url)
    assert "/customers/new" in driver.current_url


@when("kullanıcı sonuç listesindeki Customer ID linkine tıklar")
def user_clicks_customer_row_link(customers_page):
    customers_page.click_customer_row_link()


@then(parsers.parse('kullanıcı aynı sekmede "{customer_id}" numaralı müşterinin Customer Info ekranına yönlendirilir'))
def navigated_to_customer_detail_same_tab(customers_page, customer_id):
    state = customers_page.get_customer_detail_navigation_state(customer_id)
    assert state["window_count"] == state["window_count_before_click"], (
        "Müşteri detayına geçişte yeni bir sekme/pencere açıldı"
    )
    assert f"/customers/{customer_id}" in state["url"], (
        f"Beklenen müşteri detay adresine gidilmedi: {state['url']}"
    )


@when("kullanıcı tüm arama alanlarına Tab ile sırayla değer girer")
def user_fills_all_fields_via_tab(customers_page):
    customers_page.fill_all_search_fields_via_tab_navigation()


@when("kullanıcı Clear butonuna tıklar")
def user_clicks_clear_button(customers_page):
    customers_page.click_clear_button()


@then("tüm arama alanları boşalır ve sonuç listesi varsayılan hale döner")
def all_fields_cleared_and_results_reset(customers_page):
    values = customers_page.get_all_search_field_values()
    not_cleared = {locator: value for locator, value in values.items() if value}
    assert not not_cleared, f"Temizlenmeyen alanlar: {not_cleared}"
    customers_page.verify_results_reset_to_default()


@then("toplam kayıt sayısı bilgisi görüntülenir")
def results_count_displayed(customers_page):
    assert customers_page.get_results_count_number() > 0


@then("görüntülenen aralık bilgisi görüntülenir")
def results_range_displayed(customers_page):
    lower, upper = customers_page.get_results_range_bounds()
    assert lower >= 1 and upper >= lower, f"Aralık tutarsız: {lower}-{upper}"


@then("aralık bilgisindeki üst değer o sayfadaki gerçek satır sayısıyla tutarlıdır")
def results_range_matches_row_count(customers_page):
    assert customers_page.is_results_range_consistent_with_row_count()


@given("sonuç listesi varsayılan (Customer ID artan) sırada görüntülenmektedir")
def default_sort_state_before_column_sort(customers_page):
    assert customers_page.is_customer_id_column_sorted_ascending()


@when(parsers.parse('kullanıcı "{column}" sütun başlığına tıklar'))
def click_sort_column_first_time(customers_page, column):
    customers_page._sort_column_label = column
    customers_page._sort_values_before_click = customers_page.capture_sort_column_values(column)
    customers_page.click_sort_column(column)


@then(parsers.parse('sonuç listesi "{column}" sütununa göre yeniden sıralanır (varsayılan sıradan farklı)'))
def verify_sort_changed_from_default(customers_page, column):
    customers_page.wait_for_sort_column_values_to_change(column, customers_page._sort_values_before_click)
    customers_page._sort_values_after_first_click = customers_page.capture_sort_column_values(column)


@when(parsers.parse('kullanıcı "{column}" sütun başlığına tekrar tıklar'))
def click_sort_column_second_time(customers_page, column):
    customers_page.click_sort_column(column)


@then("sıralama yönü değişir (ilk tıklamadaki sıradan farklı bir sıraya geçilir)")
def verify_sort_order_changes_again(customers_page):
    column = customers_page._sort_column_label
    customers_page.wait_for_sort_column_values_to_change(column, customers_page._sort_values_after_first_click)
