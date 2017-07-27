# Imports from python.  # NOQA
from datetime import datetime


# Imports from other dependencies.
from mechanicalsoup import StatefulBrowser


# main link https://publichealth.tarrantcounty.com/foodinspection/
# link that uses params:
# https://publichealth.tarrantcounty.com/foodinspection/
# search.aspx?name=&addr=&city=&zip=
# (if params left blank, includes all. paginates)


BASE_URL = 'https://publichealth.tarrantcounty.com/foodinspection/'

ALL_RESTAURANTS_LIST_URL = '{}search.aspx?name=&addr=&city=&zip='.format(
    BASE_URL
)

EVENT_TARGETS = {
    'list_page': 'ctl00$ContentPH1$GridView1',
    'inspection_tag_change': 'ctl00$ContentPH1$DropDownList1',
    'report_retrieval': 'ctl00$ContentPH1$GridView1'
}

END_STR = 'rejected'


# ################# #
# UTILITY FUNCTIONS #
# ################# #

def create_browser():
    '''TK.

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


def retrieve_form_payload(markup, payload_id_fields):
    '''TK.

    '''
    defined_keys = {
        _: markup.find(id=_)['value']
        for _ in payload_id_fields
        if 'value' in markup.find(id=_).attrs
    }

    existing_keys = defined_keys.keys()

    empty_keys = {
        _: ''
        for _ in payload_id_fields
        if _ not in existing_keys
    }

    return {**defined_keys, **empty_keys}  # NOQA


# #################################### #
# RESTAURANT-LIST COLLECTING FUNCTIONS #
# #################################### #

def get_all_restaurants():
    '''TK.

    '''
    browser = create_browser()

    all_results = []

    # Set counter and load first page of results.
    current_page = 1
    browser.open(ALL_RESTAURANTS_LIST_URL)

    while END_STR not in browser.get_current_page().find('title').text.lower():
        print(current_page)
        # Parse current result page and add to running results list.
        all_results = all_results + lift_table_from_page(
            browser.get_current_page()
        )
        current_page += 1
        load_page(browser, current_page)

    return all_results


def get_restaurant_list_page(page_number):
    '''TK.

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
    '''TK.

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
    '''TK.

    '''
    current_markup = browser.get_current_page()

    page_change_form = browser.select_form('#aspnetForm')

    changer_payload = get_page_change_payload(current_markup)

    changer_payload['__EVENTARGUMENT'] = 'Page${}'.format(new_page)

    toxic_el = current_markup.find(id='ctl00_ContentPH1_btnSearch')
    toxic_el.extract()

    for k, v in changer_payload.items():
        page_change_form.set(k, v)

    browser.submit_selected()


def get_page_change_payload(markup):
    '''TK.

    '''
    payload_id_fields = [
        '__LASTFOCUS',
        '__VIEWSTATE',
        '__VIEWSTATEGENERATOR',
        '__SCROLLPOSITIONX',
        '__SCROLLPOSITIONY',
        '__EVENTVALIDATION',
        'ctl00_ContentPH1_txtName',
        'ctl00_ContentPH1_txtAddress',
        'ctl00_ContentPH1_txtCity',
        'ctl00_ContentPH1_txtZip',
    ]

    payload = retrieve_form_payload(markup, payload_id_fields)

    changed_keys = {}
    keys_to_delete = []
    for k, v in payload.items():
        if k[:5] == 'ctl00':
            changed_keys[k.replace('_', '$')] = v
            keys_to_delete.append(k)

    for k, v in changed_keys.items():
        payload[k] = v

    for _ in keys_to_delete:
        del payload[_]

    payload['__EVENTTARGET'] = EVENT_TARGETS['list_page']

    return payload


def lift_table_from_page(markup):
    '''THIS ACTUALLY WORKS FOR TARRANT COUNTY ATM.

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


# ########################################## #
# PER-RESTAURANT REPORT COLLECTING FUNCTIONS #
# ########################################## #

def parse_restaurant_page(browser, raw_restaurant):
    '''TK.

    '''
    detail_url = '{0}{1}'.format(BASE_URL, raw_restaurant['detail_link'])

    browser.open(detail_url)
    restaurant_markup = browser.get_current_page()

    inspection_tags = [
        {'raw_text': _.text, 'value': _['value']}
        for _
        in restaurant_markup.find(
            'select',
            attrs={'name': 'ctl00$ContentPH1$DropDownList1'}
        ).find_all('option')
    ]

    all_inspections_for_place = []
    for _ in inspection_tags:
        all_inspections_for_place.extend(
            list_establishment_inspections_by_tag(browser, detail_url, _)
        )

    all_full_reports = []
    for _ in all_inspections_for_place:
        all_full_reports.append(get_full_report(browser, detail_url, _))

    return all_full_reports


def get_inspection_tag_change_payload(markup):
    '''TK.

    '''
    payload_id_fields = [
        '__LASTFOCUS',
        '__VIEWSTATE',
        '__VIEWSTATEGENERATOR',
        '__VIEWSTATEENCRYPTED',
        '__EVENTVALIDATION',
    ]

    payload = retrieve_form_payload(markup, payload_id_fields)

    payload['__EVENTTARGET'] = EVENT_TARGETS['inspection_tag_change']

    return payload


def list_establishment_inspections_by_tag(browser, detail_url, tag):
    '''TK.

    '''
    browser.open(detail_url)

    current_markup = browser.get_current_page()

    tag_change_form = browser.select_form('#aspnetForm')

    changer_payload = get_inspection_tag_change_payload(current_markup)

    changer_payload['__EVENTARGUMENT'] = ''

    changer_payload['ctl00$ContentPH1$DropDownList1'] = tag['value']

    for k, v in changer_payload.items():
        tag_change_form.set(k, v)

    browser.submit_selected()

    tag_inspection_records = browser.get_current_page().find(
        id='ctl00_ContentPH1_GridView1'
    ).find_all('tr')

    records = []
    for _ in tag_inspection_records[1:]:
        tds = _.find_all('td')

        records.append({
            'date': datetime.strptime(
                tds[0].text,
                '%m/%d/%Y'
            ).strftime('%Y-%m-%d'),
            'type': tds[1].text,
            'demerits': tds[2].text,
            'detail_postback': tds[3].find('a')['href'],
            'tag': tag['raw_text'],
            'dropdown_choice': tag['value'],
            'order_in_tag': 0,
        })

    return records


def get_full_report(browser, detail_url, inspection_meta):
    '''TK.

    '''
    browser.open(detail_url)

    current_markup = browser.get_current_page()

    report_retrieval_form = browser.select_form('#aspnetForm')

    changer_payload = get_report_retrieval_payload(current_markup)

    changer_payload['__EVENTARGUMENT'] = inspection_meta[
        'detail_postback'
    ].replace('javascript:__doPostBack(', '').replace(')', '').split(',')[
        1
    ].replace("'", '')

    changer_payload['ctl00$ContentPH1$DropDownList1'] = inspection_meta[
        'dropdown_choice'
    ]

    for k, v in changer_payload.items():
        report_retrieval_form.set(k, v)

    browser.submit_selected()

    return {
        'violations': browser.get_current_page().find(
            id='ctl00_ContentPH1_GridView2'
        ),
        'meta': inspection_meta,
    }


def get_report_retrieval_payload(markup):
    '''TK.

    '''
    payload_id_fields = [
        '__LASTFOCUS',
        '__VIEWSTATE',
        '__VIEWSTATEGENERATOR',
        '__VIEWSTATEENCRYPTED',
        '__EVENTVALIDATION',
    ]

    payload = retrieve_form_payload(markup, payload_id_fields)

    payload['__EVENTTARGET'] = EVENT_TARGETS['report_retrieval']

    return payload


# ############################# #
# ARCHIVED & DISABLED FUNCTIONS #
# ############################# #

# def get_details(all_restaurants):
#     '''TK.

#     need to do a check for inspection category dropdown (if applicable).
#     this is part of payload for that ctl00$ContentPH1$DropDownList1:
#     need to also do a check if table exists (bc some dont have any)
#     '''
#     all_details = []
#     for restaurant in all_restaurants:
#         details = restaurant['detail_link']
#         detail_link = '{0}{1}'.format(BASE_URL, details)
#         browser = create_browser()
#         browser.open(BASE_URL)
#         browser.open(detail_link)
#         restaurant_markup = browser.get_current_page()
#         page_details = {}
#         # page_details['details'] = lift_table_detail(
#         #     browser,
#         #     restaurant_markup
#         # )
#         page_details['establishment_name'] = restaurant['name']
#         page_details['address'] = restaurant['address']
#         page_details['city'] = restaurant['city']
#         page_details['zipcode'] = restaurant['zip']
#         all_details.append(page_details)
#     return


# def test():
#     browser=create_browser()
#     browser.open("https://publichealth.tarrantcounty.com/foodinspection/detail.aspx?id=1248833")
#     markup = browser.get_current_page()
#     lift_table_detail(browser, markup)
#
#
# def lift_table_detail(browser, markup):
#     '''TK.
#
#     '''
#     page_change_form = browser.select_form('#aspnetForm')
#
#     changer_payload = get_page_change_payload(markup)
#
#     drop_down = markup.find('select')
#     options = drop_down.find_all('option')
#     for option in options:
#         changer_payload['ctl00$ContentPH1$DropDownList1:'] += 1
#         for k, v in changer_payload.items():
#             page_change_form.set(k, v)
#         browser.submit_selected()
#         main_table = markup.find(id='ctl00_ContentPH1_GridView1')
#         print(main_table)
#
#
#     # drop_down = markup.find('select')
#     # options = drop_down.find_all('option')
#     # for option in options:
#     #     main_table = markup.find(id='ctl00_ContentPH1_GridView1')
#     #     print(main_table)
#     #     select = ""
#     # inspection_rows = main_table.findAll('tr', recursive=False)[1:]
#
# def change_dropdown_payload(markup):
#     payload_id_fields = [
#         '__EVENTTARGET',
#         '__EVENTARGUMENT',
#         '__LASTFOCUS',
#         '__VIEWSTATE',
#         '__VIEWSTATEGENERATOR',
#         '__VIEWSTATEENCRYPTED',
#         '__EVENTVALIDATION',
#         'ctl00$ContentPH1$DropDownList1'
#     ]
# ##########
#     defined_keys = {
#         _: markup.find(id=_)['value']
#         for _ in payload_id_fields
#         if 'value' in markup.find(id=_).attrs
#     }
#
#     existing_keys = defined_keys.keys()
#
#     empty_keys = {
#         _: ''
#         for _ in payload_id_fields
#         if _ not in existing_keys
#     }
#
#     payload = {
#         **defined_keys,  # NOQA
#         **empty_keys
#     }
#
#     changed_keys = {}
#     keys_to_delete = []
#     for k, v in payload.items():
#         if k[:5] == 'ctl00':
#             changed_keys[k.replace('_', '$')] = v
#             keys_to_delete.append(k)
#
#     for k, v in changed_keys.items():
#         payload[k] = v
#
#     for _ in keys_to_delete:
#         del payload[_]
#
#     payload['__EVENTTARGET'] = EVENT_TARGET
#
#     return payload

# def scrape_violation_page(link):
#     '''TK.
#
#     '''
#     pass


# def clean_html_tags(string):
#     '''TK.
#
#     '''
#     clean_string = `re.`sub(r'(<\/?[^>]+(>|$))', r'', str(string))
#     return clean_string.strip()
