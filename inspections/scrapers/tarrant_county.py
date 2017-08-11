# Imports from python.  # NOQA
from datetime import datetime
# import re


# Imports from inspections.  # NOQA
from inspections.scrapers import CookieBasedScraper


BASE_URL = 'https://publichealth.tarrantcounty.com/foodinspection/'

END_STR = 'rejected'

EVENT_TARGETS = {
    'list_page': 'ctl00$ContentPH1$GridView1',
    'inspection_area_change': 'ctl00$ContentPH1$DropDownList1',
    'report_retrieval': 'ctl00$ContentPH1$GridView1',
}


class TarrantCountyScraper(CookieBasedScraper):
    '''TK.

    '''
    def __init__(self):
        locale = 'Tarrant County'
        score_type = 'demerits'

        CookieBasedScraper.__init__(
            self,
            locale=locale,
            score_type=score_type
        )

        self.set_url('base', BASE_URL)

        self.set_url(
            'list',
            ''.join([
                BASE_URL,
                'search.aspx?name=&addr=&city=&zip=',
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
        self.set_url(
            'detail',
            '{0}{1}'.format(
                self.get_url('base'),
                establishment_object['detail_link']
            )
        )

        restaurant_markup = self.open_url('detail')

        inspection_areas = [
            {'raw_text': _.text, 'value': _['value']}
            for _
            in restaurant_markup.find(
                'select',
                attrs={'name': 'ctl00$ContentPH1$DropDownList1'}
            ).find_all('option')
        ]

        # return [
        #     self.get_raw_inspections_for_area(self.get_url('detail'), _)
        #     for _ in inspection_areas
        # ]

        all_inspections_for_place = []
        for _ in inspection_areas:
            all_inspections_for_place.extend(
                self.get_raw_inspections_for_area(self.get_url('detail'), _)
            )

        return all_inspections_for_place

    def get_formatted_establishment(self, establishment_object):
        # Get the raw establishment detail object.
        raw_inspections = self.get_raw_establishment(establishment_object)

        formatted_inspections = []
        for _ in raw_inspections:
            formatted_inspections.append(
                self.get_formatted_inspection(self.get_url('detail'), _)
            )

        return {
            'establishment_name': establishment_object['establishment_name'],
            'address': establishment_object['address'],
            'city': establishment_object['city'],
            'zip_code': establishment_object['zip_code'],
            'inspections': formatted_inspections
        }

    def get_raw_inspections_for_area(self, detail_url, area):
        '''TK.

        '''
        self.set_url('detail', detail_url)
        current_markup = self.open_url('detail')

        area_change_form = self.browser.select_form('#aspnetForm')

        changer_payload = self.get_area_page_payload(current_markup)

        changer_payload['__EVENTARGUMENT'] = ''

        changer_payload['ctl00$ContentPH1$DropDownList1'] = area['value']

        for k, v in changer_payload.items():
            area_change_form.set(k, v)

        self.browser.submit_selected()

        raw_inspections_for_area = []

        inspection_table_for_area = self.browser.get_current_page().find(
            id='ctl00_ContentPH1_GridView1'
        )

        records = []
        if inspection_table_for_area is not None:
            raw_inspections_for_area = inspection_table_for_area.find_all('tr')

        if len(raw_inspections_for_area) > 0:
            for _ in raw_inspections_for_area[1:]:
                tds = _.find_all('td')

                records.append({
                    'date': datetime.strptime(
                        tds[0].text,
                        '%m/%d/%Y'
                    ).strftime('%Y-%m-%d'),
                    'inspection_type': tds[1].text,
                    'raw_score': tds[2].text,
                    'detail_postback': tds[3].find('a')['href'],
                    'area': area['raw_text'],
                    'dropdown_choice': area['value'],
                    'order_in_area': 0,
                })

        return records

    def get_formatted_inspection(self, detail_url, inspection_meta):
        '''TK.

        '''
        self.set_url('detail_inspection', detail_url)
        current_markup = self.open_url('detail_inspection')

        report_retrieval_form = self.browser.select_form('#aspnetForm')

        changer_payload = self.get_inspection_page_payload(current_markup)

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

        self.browser.submit_selected()

        violation_grid = self.browser.get_current_page().find(
            id='ctl00_ContentPH1_GridView2'
        )

        violations_raw = []
        if violation_grid is not None:
            violations_raw = violation_grid.find_all('tr')[1:]

        raw_score = None
        try:
            raw_score = int(inspection_meta['raw_score'])
        except Exception:
            print('Could not convert score to int: {}'.format(
                inspection_meta['raw_score']
            ))

        return {
            'violations': [
                self.get_formatted_violation(_) for _ in violations_raw
            ],
            'date': inspection_meta['date'],
            'raw_score': raw_score,
            'area': inspection_meta['area'],
            'inspection_type': inspection_meta['inspection_type']
            # 'meta': inspection_meta,
        }

    def get_formatted_violation(self, violation_el):
        row_cells = violation_el.find_all('td')

        infraction_category = row_cells[0].text
        violation_count = row_cells[1].text
        inspector_comment = row_cells[2].text

        points_deducted = None
        try:
            points_deducted = int(row_cells[3].text)
        except Exception:
            print('Could not convert score to int: {}'.format(
                row_cells[3].text
            ))

        return {
            'infraction_category': infraction_category,
            'violation_count': violation_count,
            'inspector_comment': inspector_comment.replace(
                u'\xa0',
                u''
            ),
            'points_deducted': points_deducted,
        }

    def load_list_page(self, new_page):
        '''TK.

        '''
        current_markup = self.browser.get_current_page()

        page_change_form = self.browser.select_form('#aspnetForm')

        changer_payload = self.get_list_page_payload(current_markup)

        changer_payload['__EVENTARGUMENT'] = 'Page${}'.format(new_page)

        toxic_el = current_markup.find(id='ctl00_ContentPH1_btnSearch')
        toxic_el.extract()

        for k, v in changer_payload.items():
            page_change_form.set(k, v)

        self.browser.submit_selected()

        return self.browser.get_current_page()

    def get_list_page_payload(self, markup):
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

        payload = self.retrieve_form_payload(markup, payload_id_fields)

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

    def get_area_page_payload(self, markup):
        '''TK.

        '''
        payload_id_fields = [
            '__LASTFOCUS',
            '__VIEWSTATE',
            '__VIEWSTATEGENERATOR',
            '__VIEWSTATEENCRYPTED',
            '__EVENTVALIDATION',
        ]

        payload = self.retrieve_form_payload(markup, payload_id_fields)

        payload['__EVENTTARGET'] = EVENT_TARGETS['inspection_area_change']

        return payload

    def get_inspection_page_payload(self, markup):
            '''TK.

            '''
            payload_id_fields = [
                '__LASTFOCUS',
                '__VIEWSTATE',
                '__VIEWSTATEGENERATOR',
                '__VIEWSTATEENCRYPTED',
                '__EVENTVALIDATION',
            ]

            payload = self.retrieve_form_payload(markup, payload_id_fields)

            payload['__EVENTTARGET'] = EVENT_TARGETS['report_retrieval']

            return payload

    def parse_raw_establishment_list(self, markup):
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
                'establishment_name': restaurant_name,
                'address': restaurant_address,
                'city': restaurant_city,
                'zip_code': restaurant_zip,
                'detail_link': detail_link,
                'map_link': map_link
            })
        return rows_formatted
