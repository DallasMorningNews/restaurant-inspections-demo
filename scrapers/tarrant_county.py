# Imports from python.  # NOQA
import re

# Imports from other dependencies.
from mechanicalsoup import StatefulBrowser

# main link https://publichealth.tarrantcounty.com/foodinspection/
# link that uses params:
# https://publichealth.tarrantcounty.com/foodinspection/
# search.aspx?name=&addr=&city=&zip=
# (if params left blank, includes all. paginates)

BASE_URL = 'https://publichealth.tarrantcounty.com/foodinspection/'

ALL_RESTAURANTS_LIST_URL = '{}search.aspx?name=&addr=&city=&zip='.format(BASE_URL)

EVENT_TARGET = 'ctl00$ContentPH1$GridView1'

def create_browser():
    '''
    '''
    browser = StatefulBrowser(
        soup_config={'features': 'html.parser'}
    )

    browser.session.headers.update({
        'User-Agent': ' '.join([
            'Mozilla/5.0 (Windows NT 6.1)',
            'AppleWebKit/537.36 (KHTML, like Gecko)',
            'Chrome/41.0.2228.0 Safari/537.36',
        ]),
        'Content-Type': 'application/x-www-form-urlencoded'
    })

    return browser

def get_all_restaurants():
    '''
    '''
    browser = create_browser()

    # Load initial page to set cookie.
    browser.open(BASE_URL)

    all_results = []

    # Set counter and load first page of results.
    current_page = 1
    browser.open(ALL_RESTAURANTS_LIST_URL)

    while 'error' not in browser.get_current_page().find('title').text.lower():
        # Parse current result page and add to running results list.
        all_results = all_results + lift_table_from_page(
            browser.get_current_page()
        )
        current_page += 1
        load_page(browser, current_page)

    return all_results

def get_restaurant_list_page(page_number):
    '''
    '''
    browser = create_browser()

    browser.open(BASE_URL)

    browser.open(ALL_RESTAURANTS_LIST_URL)

    if page_number > 1:
        needed_page_range = get_needed_page_range(page_number)

        needed_page_range.remove(1)  # Discard page 1; it's already loaded.

        for _ in needed_page_range:
            print('LOAD {}'.format(_))
            load_page(browser, _)

    return browser.get_current_page()


def get_needed_page_range(desired_number):
    '''
    '''
    decade_ends = [_ for _ in range(10, (desired_number + 1), 10)]
    decade_starts = [(_ - 9) for _ in decade_ends]

    intermediate_jumps = sorted(decade_starts + decade_ends)

    if 1 not in intermediate_jumps:
        # Prepend 1 to list of jumps using list addition.
        intermediate_jumps = [1] + intermediate_jumps

    if desired_number > max(intermediate_jumps):
        # Adds start of last decade to list of jumps.
        intermediate_jumps.append(max(intermediate_jumps) + 1)

    if desired_number not in intermediate_jumps:
        intermediate_jumps.append(desired_number)

    return sorted(intermediate_jumps)


def load_page(browser, new_page):
    '''
    '''
    current_markup = browser.get_current_page()

    # page_change_form = browser.select_form('#Form2')

    changer_payload = get_page_change_payload(current_markup)

    changer_payload['__EVENTARGUMENT'] = 'Page${}'.format(new_page)

    # toxic_el = current_markup.find(id='ContentPlaceHolder1_Searchby_Button')
    # toxic_el.extract()

    # for k, v in changer_payload.items():
    #     page_change_form.set(k, v)

    # browser.submit_selected()


def get_page_change_payload(markup):
    '''
    '''
    payload_id_fields = [
        '__EVENTVALIDATION',
        '__VIEWSTATE',
        '__VIEWSTATEGENERATOR',
    ]

    payload = {
        _: markup.find(id=_)['value']
        for _ in payload_id_fields
    }

    payload['__EVENTTARGET'] = EVENT_TARGET

    return payload


def lift_table_from_page(markup):
    '''
    THIS ACTUALLY WORKS FOR TARRANT COUNTY ATM.
    '''
    table_matches = markup.find_all(id='ctl00_ContentPH1_GridView1')

    table_rows = table_matches[0].find_all('tr', recursive=False)[1:-1]

    rows_formatted = []
    for _ in table_rows:
        row_cells = _.find_all('td')
        detail_link = row_cells[0].find_all('a')[0]['href']
        restaurant_name = row_cells[0].text
        restaurant_address = row_cells[1].text
        restaurant_city = row_cells[2].text
        restaurant_zip = row_cells[3].text
        map_link = row_cells[4].find_all('a')[0]['href']
        rows_formatted.append({
            'name': restaurant_name,
            'address': restaurant_address,
            'city': restaurant_city,
            'zip': restaurant_zip,
            'detail_link': detail_link,
            'map_link': map_link
        })
    return rows_formatted

def get_details(all_restaurants):
    '''
    need to do a check for inspection category dropdown (if applicable), this is part of payload for that ctl00$ContentPH1$DropDownList1:
    need to also do a check if table exists (bc some dont have any)
    '''
    all_details = []
    for restaurant in all_restaurants:
        details = restaurant['detail_link']
        detail_link = '{0}{1}'.format(BASE_URL, details)
        browser=create_browser()
        browser.open(INITIAL_URL)
        browser.open(detail_link)
        restaurant_markup = browser.get_current_page()
        page_details = {}
        #page_details['details'] = lift_table_detail(restaurant_markup)
        page_details['establishment_name'] = restaurant['name']
        page_details['address'] = restaurant['address']
        page_details['city'] = restaurant['city']
        page_details['zipcode'] = restaurant['zip']
        all_details.append(page_details)
    return all_details


def lift_table_detail(markup):
    '''
    '''

def scrape_violation_page(link):
    '''
    '''

def clean_html_tags(string):
    '''
    '''
    clean_string = re.sub(r'(<\/?[^>]+(>|$))', r'', str(string))
    return clean_string.strip()
