# Imports from python.  # NOQA
import re


# Imports from other dependencies.
from mechanicalsoup import StatefulBrowser


# main link: http://apps.fortworthtexas.gov/health/
# link to view all establishments, paginates:
# http://apps.fortworthtexas.gov/health/FacilityList.aspx?Alpha=ALL
# clickable details

BASE_URL = 'http://apps.fortworthtexas.gov/health/'

INITIAL_URL = '{}Main.aspx'.format(BASE_URL)

ALL_RESTAURANTS_LIST_URL = '{}FacilityList.aspx?Alpha=ALL'.format(BASE_URL)

EVENT_TARGET = 'ctl00$ContentPlaceHolder1$GridView1'


def create_browser():
    '''Creates a `mechanicalsoup.StatefulBrowser` with default settings.

    Utility class used by several other functions within this scraper.

    Returns:
        :class:`mechanicalsoup.StatefulBrowser`: A browser with the
        standard settings defined by this file.
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
    '''Retrieves all restaurants, traversing result pages one by one.

    Because of the pagination constraints imposed by Fort Worth's site,
    this is the far faster method to gather all restaurants' names,
    addresses and detail page links -- needing less than ten percent as
    many queries as the other capture method in this scraper -- but it
    cannot grab an individual page of results.

    Returns:
        :class:`bs4.BeautifulSoup`: A BeautifulSoup 4 representation of
        the page you requested.
    '''
    browser = create_browser()

    # Load initial page to set cookie.
    browser.open(INITIAL_URL)

    all_results = []

    # Set counter and load first page of results.
    current_page = 1
    browser.open(ALL_RESTAURANTS_LIST_URL)
    # current_title = browser.get_current_page().find('title').text.lower()

    while 'error' not in browser.get_current_page().find('title').text.lower():
        # Parse current result page and add to running results list.
        all_results = all_results + lift_table_from_page(
            browser.get_current_page()
        )
        # print('Added page {}'.format(current_page))
        current_page += 1
        load_page(browser, current_page)
        # current_title = browser.get_current_page().find('title').text.lower()

    return all_results

def get_restaurant_list_page(page_number):
    '''Retrieves an single page of restaurant listings.

    Unlike the `get_all_restaurants()` method in this scraper (which
    loads each results page sequentially), `get_restaurant_list_page()`
    loads only those pages necessary to capture the specific page passed
    as a parameter at runtime.

    This is far more efficient for individual list page loads, but will
    lead to more than 10 times as many queries (given 100 pages of
    results) than `get_all_restaurants()` if used to collect all pages
    at once.

    Args:
        page_number (int): The number of the page you wish to retrieve.

    Returns:
        :class:`bs4.BeautifulSoup`: A BeautifulSoup 4 representation of
        the page you requested.
    '''
    browser = create_browser()

    browser.open(INITIAL_URL)

    browser.open(ALL_RESTAURANTS_LIST_URL)

    if page_number > 1:
        needed_page_range = get_needed_page_range(page_number)

        needed_page_range.remove(1)  # Discard page 1; it's already loaded.

        for _ in needed_page_range:
            print('LOAD {}'.format(_))
            load_page(browser, _)

    return browser.get_current_page()


def get_needed_page_range(desired_number):
    '''Lists pages the scraper needs to load to reach a specified page.

    Fort Worth's scraper handles pagination in a baroque manner: when a
    user loads the first page of results, they can then load any page up
    to and including page 10.

    To see pages beyond this, the user has to click on an ellipsis,
    which loads page 11, at which point they can view any page up to and
    including page 20.

    (To go back to pages 1-10 requires a similar reversion to page 10,
    then to any others needed, but traversing backward through the page
    order is beyond the scope of this scraper.)

    This process — of needing to click on the last page in a decade, and
    then on the first in the next decade — manifests itself not only in
    the site's UI. The backend requires this flow, too.

    Accordingly, this function finds the end of each decade that will
    need to be traversed (using a range function that runs from the end
    of the first decade to the desired page number [plus one, to account
    for range() being zero-indexed], counting every tenth value).

    Once it has calculated a list of each decade, the function also
    identifies the page that will need to be loaded to begin the decade.

    It then merges these two lists together, adds the desired number (if
    not already included as the end of a decade) and the first value in
    the final decade (if not the same as the desired number). Then it
    adds page 1 (if not already included, as the list of decade ends
    will be blank when the desired page number is less than 10).

    Finally the function sorts and returns this list.

    Args:
        desired_number (int): The number of the page you ultimately want
        to load.

    Returns:
        list: A list of pages you'll needed to access in order to load
        the page you specified.
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
    '''Loads the specified restaurant list page.

    NOTE: Fort Worth's inspections site restricts its pagination -- one
    can only load page 12 after loading pages 1, 10 and 11; page 45
    requires loading pages 1, 10, 11, 20, 21, 30, 31, 40 and 41 first.

    Refer to the description of this behavior in the documentation for
    `scrapers.fort_worth.get_needed_page_range()` in this same package
    for more information, and run that function if in doubt about the
    necessary precursors to your desired page.

    This function does not return anything -- it just changes the state
    of the `browser` object passed to it.

    Args:
        browser (:class:`mechanicalsoup.StatefulBrowser`): The existing
        stateful browser object you're using to load pages. This browser
        object should already have accessed `INITIAL_URL` and
        `ALL_RESTAURANTS_LIST_URL`, at least, to establish the cookies
        and markup needed for this function to work. If the structure of
        the site being scraped requires intermediate pages to have been
        loaded before your desired page (see above), these should also
        have been loaded via `load_page` calls in the prescribed order.

        new_page (int): The number of the page you wish to load.

    Returns:
        None
    '''
    current_markup = browser.get_current_page()

    page_change_form = browser.select_form('#Form2')

    changer_payload = get_page_change_payload(current_markup)

    changer_payload['__EVENTARGUMENT'] = 'Page${}'.format(new_page)

    toxic_el = current_markup.find(id='ContentPlaceHolder1_Searchby_Button')
    toxic_el.extract()

    for k, v in changer_payload.items():
        page_change_form.set(k, v)

    browser.submit_selected()


def get_page_change_payload(markup):
    '''Compile the needed form contents to change results list pages.

    Note that one field -- `__EVENTARGUMENT` -- is not set here, because
    this field's value changes depending on which page is to be loaded.
    Set this manually before submitting a form, in the following format:

        payload['__EVENTARGUMENT'] = 'Page$' + your_page_number

    Args:
        markup (:class:`mechanicalsoup.StatefulBrowser`): The
        BeautifulSoup 4 representation of a restaurant list page.

    Returns:
        dict of str: str: A mapping of form fields to the values they
        must receive before the page can be changed.
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
    '''Extracts the restaurant results table from a given page's markup.

    Used to convert a loaded page into a datastore-ready set of
    restaurant objects, with a bare set of related information.

    Args:
        markup (:class:`mechanicalsoup.StatefulBrowser`): The
        BeautifulSoup 4 representation of a restaurant list page.

    Returns:
        list: A list of restaurant objects. Each has 5 string values:
            name: Restaurant's name (all caps/some chains have store #).
            address: Restaurant's parsed address, without extra spaces.
            zip: Restaurant's stated ZIP code.
            detail_link: URL to restaurant's detail page.
            map_link: URL to map of restaurant. Missing on some entries.
    '''
    table_matches = markup.find_all(id='ContentPlaceHolder1_GridView1')

    if len(table_matches) == 1:
        table_rows = table_matches[0].find_all('tr', recursive=False)[1:-1]

        rows_formatted = []
        for _ in table_rows:
            row_cells = _.find_all('td')

            detail_link = row_cells[0].find_all('a')[0]['href']
            restaurant_name = row_cells[1].text
            restaurant_address = re.sub(' +', ' ', row_cells[2].text).strip()
            restaurant_zip = row_cells[3].text.strip()

            map_link_matches = row_cells[4].find_all('a')
            map_link = None
            if len(map_link_matches) >= 1:
                map_link = map_link_matches[0]['href']

            rows_formatted.append({
                'name': restaurant_name,
                'address': restaurant_address,
                'zip': restaurant_zip,
                'detail_link': detail_link,
                'map_link': map_link,
            })

        return rows_formatted

    return None

def get_details(all_restaurants):
    ''' Gets all the details from an individual restaurant's page and stores them in an array of json objects.

    :param all_restaurants: a list of json objects obtained after lift_table_from_page() is performed
    :return all_details: an array of every restaurant and its health inspection details
    :rtype: array
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
        page_details['details'] = lift_table_detail(restaurant_markup)
        page_details['establishment_name'] = restaurant['name']
        page_details['address'] = restaurant['address']
        page_details['zipcode'] = restaurant['zip']
        all_details.append(page_details)
    return all_details

def lift_table_detail(markup):
    ''' This lifts the table details from an individual restaurant's page in json format after receiving the page's markup, this function is called in get_details()

    :param markup: the html markup of a restaurant page
    :return area_dict: an array of information on each area's inspection history in a restaurant
    :rtype: array
    '''
    main_table = markup.find(id='ContentPlaceHolder1_GridView1')

    area_rows = main_table.findAll('tr', recursive=False)[1:] # finds each area row
    area_dict = []
    inspections_dict = []
    violations_dict = []
    for row in area_rows:
        row_cells = row.find_all('td')
        area_name = row_cells[1]
        inspection_table = row_cells[2]
        i_row_cells = inspection_table.find_all('td')
        for i_row in i_row_cells:
            raw_link_cell = i_row_cells[0]
            if(clean_html_tags(i_row_cells[0]) != "N/A"):
                i_detail_link = i_row_cells[0].find_all('a')[0]['href']
            else:
                i_detail_link = None
            inspection_date = i_row_cells[1]
            inspection_type = i_row_cells[2]
            inspection_demerits = i_row_cells[3]
            inspection_info = {
                "area_name": clean_html_tags(area_name),
                "i_detail_link": i_detail_link,
                "inspection_date": clean_html_tags(inspection_date),
                "inspection_type": clean_html_tags(inspection_type),
                "inspection_demerits": clean_html_tags(inspection_demerits),
                "violations": scrape_violation_page(i_detail_link)
            }
        inspections_dict.append(inspection_info)

        row_info = {
            "inspection_info": inspections_dict
        }
    area_dict.append(row_info)

    return area_dict

def scrape_violation_page(link):
    ''' This is called in lift_table_detail() to scrape the violation page, because each inspection has its own page for what the exact violation details were. And it stores them in an array as well.

    :param link: the end of the link to each inspection page, obtained from scraping the individual restaurant page
    :return violations_dict: an array of information about each violation
    :rtype: array
    '''
    if(link != None):
        violations_link = '{0}{1}'.format(BASE_URL, link)
        browser=create_browser()
        browser.open(INITIAL_URL)
        browser.open(violations_link)
        markup = browser.get_current_page()
        main_table = markup.find(id='ContentPlaceHolder1_GridView1')
        violation_rows = main_table.findAll('tr')[1:]
        violations_dict = []
        for row in violation_rows:
            row_cells = row.find_all('td')
            code = row_cells[0]
            description = row_cells[1]
            specific_infraction = row_cells[2]
            demerits = row_cells[3]
            violation = {
                "code": clean_html_tags(code),
                "description": clean_html_tags(description),
                "specific_infraction": clean_html_tags(specific_infraction),
                "demerits": clean_html_tags(demerits)
            }
            violations_dict.append(violation)
        return violations_dict
    else:
        return None

def clean_html_tags(string):
    '''Cleans html tags from a string using the re.sub function

    :param string: a variable with HTML tags to clean, will be casted to string if not already string.
    :return clean_string: string without HTML tags
    :rtype: string
    '''
    clean_string = re.sub(r'(<\/?[^>]+(>|$))', r'', str(string))
    return clean_string.strip()
