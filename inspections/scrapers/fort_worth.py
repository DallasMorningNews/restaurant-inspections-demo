# Imports from python.  # NOQA
# from datetime import datetime
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
    score_type = 'TK'

    def __init__(self):
        CookieBasedScraper.__init__(self, 'Tarrant County')

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
            'zip': establishment_object['zip'],
        }

        page_details['inspections'] = self.parse_inspection(
            restaurant_markup
        )

        return page_details

    def get_formatted_establishment(self, establishment_object):
        # Get the raw establishment detail object.
        raw_establishment = self.get_raw_establishment(establishment_object)

        # return raw_inspections
        #
        # formatted_inspections = []
        # for _ in raw_inspections:
        #     formatted_inspections.append(
        #         self.get_formatted_inspection(self.get_url('detail'), _)
        #     )

        return {
            'establishment_name': raw_establishment['establishment_name'],
            'address': raw_establishment['address'],
            'city': 'Fort Worth',
            'zip': raw_establishment['zip'],
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
            area_listed_inspections = area_cells[2].find('table').find_all(
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
                    'area_name': area_name,
                    'detail_link': detail_link,
                    'date': inspection_cells[1].text.strip(),
                    'inspection_type': inspection_cells[2].text.strip(),
                    'demerits': inspection_cells[3].text.strip(),
                }

                this_area_inspections.append(inspection)
            all_areas_inspections.extend(this_area_inspections)

        return all_areas_inspections

    # def get_raw_inspections_for_tag(self, detail_url, tag):
    #     '''TK.
    #
    #     '''
    #     self.set_url('detail', detail_url)
    #     current_markup = self.open_url('detail')
    #
    #     tag_change_form = self.browser.select_form('#aspnetForm')
    #
    #     changer_payload = self.get_tag_page_payload(current_markup)
    #
    #     changer_payload['__EVENTARGUMENT'] = ''
    #
    #     changer_payload['ctl00$ContentPH1$DropDownList1'] = tag['value']
    #
    #     for k, v in changer_payload.items():
    #         tag_change_form.set(k, v)
    #
    #     self.browser.submit_selected()
    #
    #     raw_inspections_for_tag = []
    #
    #     inspection_table_for_tag = self.browser.get_current_page().find(
    #         id='ctl00_ContentPH1_GridView1'
    #     )
    #
    #     records = []
    #     if inspection_table_for_tag is not None:
    #         raw_inspections_for_tag = inspection_table_for_tag.find_all('tr')
    #
    #     if len(raw_inspections_for_tag) > 0:
    #         for _ in raw_inspections_for_tag[1:]:
    #             tds = _.find_all('td')
    #
    #             records.append({
    #                 'date': datetime.strptime(
    #                     tds[0].text,
    #                     '%m/%d/%Y'
    #                 ).strftime('%Y-%m-%d'),
    #                 'type': tds[1].text,
    #                 'demerits': tds[2].text,
    #                 'detail_postback': tds[3].find('a')['href'],
    #                 'tag': tag['raw_text'],
    #                 'dropdown_choice': tag['value'],
    #                 'order_in_tag': 0,
    #             })
    #
    #     return records

    def get_raw_inspection(self, inspection_object):
        '''TK.

        '''
        if 'detail_link' not in inspection_object:
            return None

        inspection_detail = inspection_object['detail_link']

        self.set_url(
            'inspection_detail',
            '{0}{1}'.format(self.get_url('base'), inspection_detail)
        )

        inspection_markup = self.open_url('inspection_detail')

        main_table = inspection_markup.find(id='ContentPlaceHolder1_GridView1')

        violation_rows = main_table.findAll('tr')[1:]

        violations_list = []
        for row in violation_rows:
            row_cells = row.find_all('td')

            violation = {
                'code': row_cells[0].text.strip(),
                'specific_infraction': row_cells[2].text.strip(),
                'demerits': row_cells[3].text.strip(),
                'description': row_cells[1].text.strip(),
            }
            violations_list.append(violation)

        inspection_object['violations'] = violations_list

        return inspection_object

    def get_formatted_inspection(self, inspection_object):
        '''TK.

        '''
        raw_inspection = self.get_raw_inspection(inspection_object)

        return raw_inspection

    # def get_formatted_violation(self, violation_el):
    #     row_cells = violation_el.find_all('td')
    #
    #     violation_name = row_cells[0].text
    #     violation_count = row_cells[1].text
    #     violation_description = row_cells[2].text
    #     violation_points = row_cells[3].text
    #
    #     return {
    #         'violation_name': violation_name,
    #         'violation_count': violation_count,
    #         'violation_description': violation_description.replace(
    #             u'\xa0',
    #             u''
    #         ),
    #         'violation_points': violation_points
    #     }

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

    # def get_tag_page_payload(self, markup):
    #     '''TK.
    #
    #     '''
    #     payload_id_fields = [
    #         '__LASTFOCUS',
    #         '__VIEWSTATE',
    #         '__VIEWSTATEGENERATOR',
    #         '__VIEWSTATEENCRYPTED',
    #         '__EVENTVALIDATION',
    #     ]
    #
    #     payload = self.retrieve_form_payload(markup, payload_id_fields)
    #
    #     payload['__EVENTTARGET'] = EVENT_TARGETS['inspection_tag_change']
    #
    #     return payload
    #
    # def get_inspection_page_payload(self, markup):
    #         '''TK.
    #
    #         '''
    #         payload_id_fields = [
    #             '__LASTFOCUS',
    #             '__VIEWSTATE',
    #             '__VIEWSTATEGENERATOR',
    #             '__VIEWSTATEENCRYPTED',
    #             '__EVENTVALIDATION',
    #         ]
    #
    #         payload = self.retrieve_form_payload(markup, payload_id_fields)
    #
    #         payload['__EVENTTARGET'] = EVENT_TARGETS['report_retrieval']
    #
    #         return payload
    #
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
                    'zip': restaurant_zip,
                    'detail_link': detail_link,
                    'map_link': map_link,
                })

            return rows_formatted

        return None
