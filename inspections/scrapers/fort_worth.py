# Imports from python.  # NOQA
from copy import deepcopy
from datetime import datetime
import re


# Imports from inspections.  # NOQA
from inspections.scrapers import CookieBasedScraper


# BASE_URL = 'https://publichealth.tarrantcounty.com/foodinspection/'
BASE_URL = 'http://apps.fortworthtexas.gov/health/'

END_STR = 'error'

EVENT_TARGETS = {
    'list_page': 'ctl00$ContentPlaceHolder1$GridView1',
    # 'inspection_tag_change': '',
    # 'report_retrieval': '',
}


class FortWorthScraper(CookieBasedScraper):
    '''TK.

    '''
    def __init__(self):
        locale = 'City of Fort Worth'
        score_type = 'demerits'

        CookieBasedScraper.__init__(
            self,
            locale=locale,
            score_type=score_type
        )

        self.set_url('base', BASE_URL)

        self.set_url(
            'initial',
            ''.join([
                BASE_URL,
                'Main.aspx',
            ])
        )

        self.set_url(
            'list',
            ''.join([
                BASE_URL,
                'FacilityList.aspx?Alpha=ALL',
            ])
        )

        self.update_browser_headers({
            'User-Agent': ' '.join([
                'Mozilla/5.0 (Windows NT 6.1)',
                'AppleWebKit/537.36 (KHTML, like Gecko)',
                'Chrome/41.0.2228.0 Safari/537.36',
            ]),
            'Content-Type': 'application/x-www-form-urlencoded'
        })

        self.open_url('initial')

    def get_raw_establishment_list(self, verbose=False):
        '''TK.

        '''
        all_results = []

        # Set counter and load first page of results.
        current_page = 1
        current_response = self.open_url('list')

        while END_STR not in current_response.find('title').text.lower():
            if verbose is True:
                print(current_page)
            # Parse current result page and add to running results list.
            all_results = all_results + self.parse_raw_establishment_list(
                current_response
            )

            current_page += 1
            current_response = self.load_list_page(current_page)

        return all_results

    def get_formatted_establishment_list(self, verbose=False, batch_size=20):
        '''Gets the full, formatted list of establishments and reports.

        Gathers all the details from each individual restaurant's page
        and stores them in an array of json objects.

        :param verbose: a boolean indicating whether to print progress
            messages as the script progresses

        :return all_details: an array of every restaurant and its health
                inspection details
        :rtype: array
        '''
        # Get the raw list of establishments.
        data = self.get_raw_establishment_list(verbose)

        if verbose is True:
            print('Scraping {} establishments...'.format(len(data)))

        formatted_data = []

        for i, _ in enumerate(data):
            formatted_data.append(self.get_formatted_establishment(_))

            if verbose is True:
                if (i % batch_size) == 0:
                    print('Finished establishment #{}'.format(i))
                print('.')

        return formatted_data

    def get_raw_establishment(self, establishment_object):
        detail_url = establishment_object['detail_link']

        self.set_url(
            'detail',
            '{0}{1}'.format(BASE_URL, detail_url)
        )

        restaurant_markup = self.open_url('detail')

        page_details = {
            'establishment_name': establishment_object['name'],
            'address': establishment_object['address'],
            'zip_code': establishment_object['zip_code'],
        }

        page_details['inspections'] = self.parse_inspection(restaurant_markup)

        return page_details

    def get_formatted_establishment(self, establishment_object):
        # Get the raw establishment detail object.
        raw_establishment = self.get_raw_establishment(establishment_object)

        return {
            'establishment_name': raw_establishment['establishment_name'],
            'address': raw_establishment['address'],
            'city': 'Fort Worth',
            'zip_code': raw_establishment['zip_code'],
            'inspections': [
                self.get_formatted_inspection(_)
                for _ in raw_establishment['inspections']
            ]
        }

    def parse_inspection(self, markup):
        main_table = markup.find(id='ContentPlaceHolder1_GridView1')

        areas = main_table.find_all('tr', recursive=False)[1:]

        all_areas_inspections = []
        for area in areas:
            this_area_inspections = []

            area_cells = area.find_all('td', recursive=False)

            area_name = area_cells[1].text.strip()
            area_inspection_table = area_cells[2].find('table')
            if area_inspection_table is not None:
                area_listed_inspections = area_inspection_table.find_all(
                    'tr',
                    recursive=False
                )[1:]

                for raw_inspection in area_listed_inspections:
                    inspection_cells = raw_inspection.find_all('td')

                    icon_text = inspection_cells[0].text.strip()

                    detail_link = None
                    if icon_text != 'N/A':
                        detail_link = inspection_cells[0].find('a')['href']

                    inspection = {
                        'area': area_name,
                        'detail_link': detail_link,
                        'date': inspection_cells[1].text.strip(),
                        'inspection_type': inspection_cells[2].text.strip(),
                        'demerits': inspection_cells[3].text.strip(),
                    }

                    this_area_inspections.append(inspection)
                all_areas_inspections.extend(this_area_inspections)

        return all_areas_inspections

    def get_raw_inspection(self, inspection_object):
        '''TK.

        '''
        inspection_detail = inspection_object.pop('detail_link', None)

        if inspection_detail is None:
            inspection_object['violations'] = []
            return inspection_object

        self.set_url(
            'inspection_detail',
            '{0}{1}'.format(self.get_url('base'), inspection_detail)
        )

        inspection_markup = self.open_url('inspection_detail')

        main_table = inspection_markup.find(id='ContentPlaceHolder1_GridView1')

        violation_rows = main_table.find_all('tr', recursive=False)[1:]

        inspection_object['violations'] = [
            self.get_formatted_violation(_) for _ in violation_rows
        ]

        return inspection_object

    def get_formatted_inspection(self, inspection_object):
        '''TK.

        '''
        raw_inspection = self.get_raw_inspection(inspection_object)

        if raw_inspection is None:
            return None

        raw_date = raw_inspection.get('date', None)
        raw_demerits = raw_inspection.pop('demerits', None)

        formatted_inspection = deepcopy(raw_inspection)

        formatted_date = None
        if raw_date is not None:
            date_obj = datetime.strptime(raw_date, '%m/%d/%Y')
            formatted_date = date_obj.strftime('%Y-%m-%d')

        formatted_demerits = None
        if raw_demerits is not None:
            formatted_demerits = int(raw_demerits)

        formatted_inspection['date'] = formatted_date
        formatted_inspection['raw_score'] = formatted_demerits

        return formatted_inspection

    def get_raw_violation(self, violation_object):
        '''TK.

        '''
        cells = violation_object.find_all('td')

        return {
            'statute_citation': cells[0].text.strip(),
            'inspector_comment': cells[2].text.strip(),
            'demerits': cells[3].text.strip(),
            'infraction_category': cells[1].text.strip(),
        }

    def get_formatted_violation(self, violation_object):
        '''TK.

        '''
        raw_violation = self.get_raw_violation(violation_object)

        raw_demerits = raw_violation.pop('demerits', None)

        formatted_violation = deepcopy(raw_violation)

        formatted_demerits = None
        if raw_demerits is not None:
            formatted_demerits = int(raw_demerits)

        formatted_violation['points_deducted'] = formatted_demerits

        return formatted_violation

    def load_list_page(self, new_page):
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
            new_page (int): The number of the page you wish to load.

        Returns:
            None
        '''
        current_markup = self.browser.get_current_page()

        page_change_form = self.browser.select_form('#Form2')

        changer_payload = self.get_list_page_payload(current_markup)

        changer_payload['__EVENTARGUMENT'] = 'Page${}'.format(new_page)

        toxic_el = current_markup.find(
            id='ContentPlaceHolder1_Searchby_Button'
        )
        toxic_el.extract()

        for k, v in changer_payload.items():
            page_change_form.set(k, v)

        self.browser.submit_selected()

        return self.browser.get_current_page()

    def get_list_page_payload(self, markup):
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

        payload = self.retrieve_form_payload(markup, payload_id_fields)

        payload['__EVENTTARGET'] = EVENT_TARGETS['list_page']

        return payload

    def parse_raw_establishment_list(self, markup):
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
                zip_code: Restaurant's stated ZIP code.
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
                restaurant_address = re.sub(
                    ' +',
                    ' ',
                    row_cells[2].text
                ).strip()
                restaurant_zip = row_cells[3].text.strip()

                map_link_matches = row_cells[4].find_all('a')
                map_link = None
                if len(map_link_matches) >= 1:
                    map_link = map_link_matches[0]['href']

                rows_formatted.append({
                    'name': restaurant_name,
                    'address': restaurant_address,
                    'zip_code': restaurant_zip,
                    'detail_link': detail_link,
                    'map_link': map_link,
                })

            return rows_formatted

        return None
