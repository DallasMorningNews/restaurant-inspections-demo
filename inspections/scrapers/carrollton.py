# Imports from python.  # NOQA
from datetime import datetime
import re


# Imports from inspections.  # NOQA
from inspections.scrapers import SequentialEnhancementScraper


# Imports from other dependencies.
from bs4 import BeautifulSoup
from urllib.parse import parse_qs, urlparse  # NOQA
# import requests


class CarrolltonScraper(SequentialEnhancementScraper):
    '''TK.

    '''
    def __init__(self):
        locale = 'City of Carrollton'
        score_type = 'TK'

        SequentialEnhancementScraper.__init__(
            self,
            locale=locale,
            score_type=score_type
        )

        self.set_url(
            'feed',
            ''.join([
                'http://www.cityofcarrollton.com/departments/departments-a-f/',
                'environmental-quality-services/food-consumer-safety/',
                'restaurant-scores'
            ])
        )

        feed_soup = BeautifulSoup(self.open_url('feed').content, 'html.parser')

        iframes = feed_soup.find_all('iframe', {'name': 'inspections'})
        if len(iframes) > 0:
            iframe_url = iframes[0].attrs['src']
            self.set_url('list', iframe_url)
        else:
            print('ERROR: Couldn\'t find a matching IFRAME on landing page.')

    def get_detail_page_id(self, linked_node):
        if linked_node.has_attr('onclick'):
            url_matches = re.search(
                '^window.location=\'(.*)\'',
                linked_node['onclick']
            )

            if len(url_matches.groups()) > 0:
                detail_url = url_matches.groups()[0]
                detail_qs = urlparse(detail_url).query
                return parse_qs(detail_qs).get('i', [None])[0]

        return None

    def get_raw_establishment_list(self):
        markup = BeautifulSoup(self.open_url('list').content, 'html.parser')

        establishments = []

        for _ in markup.find('tbody').find_all('tr'):
            detail_id = self.get_detail_page_id(_)

            establishments.append({
                'establishment_name': _.find_all('td')[0].text,
                'establishment_type': _.find_all('td')[2].text,
                'detail_id': detail_id,
                'latest_score': int(_.find_all('td')[1].text),
                'latest_inspection_date': _.find_all('td')[3].text,
            })

        return establishments

    def get_formatted_establishment_list(self, verbose=False, batch_size=20):
        # Get the raw list of establishments.
        data = self.get_raw_establishment_list()

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
        establisment_url_params = {'i': establishment_object['detail_id']}

        querystring = parse_qs(urlparse(self.get_url('list')).query)

        if 's' not in querystring or len(querystring['s']) == 0:
            establisment_url_params['s'] = 100
        elif querystring['s'][0] != '100':
            print('ERROR: Unexpected "s" value in detail-page querystring.')

        establishment_html = self.open_url(
            'list',
            params=establisment_url_params
        )

        soup = BeautifulSoup(establishment_html.content, 'html.parser')

        cleaned_title = soup.find('h3').text.split('-')
        clean_name = '-'.join(cleaned_title[:-1]).strip()
        clean_address = cleaned_title[-1].strip()

        # for date in soup.findAll('p')[1]:
        #     clean_date = date
        #
        # for score in soup.findAll('p')[2]:
        #     clean_score = score

        return {
            'establishment_name': clean_name,
            'address': clean_address,
            'city': 'Carrollton',
            # 'inspection_date': clean_date.strip(),
            # 'inspection_score': clean_score.strip(),
            'inspections': self.get_raw_inspections(
                soup,
                establishment_html
            )
        }

    def get_formatted_establishment(self, establishment_object):
        establishment_object = self.get_raw_establishment(establishment_object)

        establishment_name = establishment_object['establishment_name']

        formatted_establishment = {
            'establishment_name': establishment_name,
            'address': establishment_object['address'],
            'city': establishment_object['city'],
        }

        all_inspections = [
            self.get_formatted_inspection(_)
            for _ in establishment_object['inspections']
        ]

        formatted_establishment['inspections'] = [
            _ for _ in all_inspections
            if _['date'] is not None and _['raw_score'] is not None
        ]

        elided_inspections = [
            _ for _ in all_inspections
            if _['date'] is None or _['raw_score'] is None
        ]

        if len(elided_inspections) > 0:
            print(' '.join([
                'Removed {} inspections without dates and/or scores from',
                'establishment named "{}".'
            ]).format(len(elided_inspections), establishment_name))

        return formatted_establishment

    def get_raw_inspections(self, soup, request):
        all_inspections = [
            self.parse_inspection(soup, request)
        ]

        tables = soup.find_all('table')

        if len(tables) == 0:
            print('ERROR: Zero tables discovered on latest inspection page.')
            print('    URL: {}'.format(request.url))

        elif len(tables) == 1:
            first_table_headers = tables[0].find_all('tr')[0]
            first_header_cell = first_table_headers.find_all('th')[0]

            if first_header_cell.text.lower() == 'points deducted':
                # If there's only been one inspection of this establishment,
                # there won't be any tabular links to other inspections for us
                # to follow.
                pass

            else:
                print(' '.join([
                    'ERROR: Only one table discovered on latest',
                    'inspection page.',
                ]))
                print(' '.join([
                    'This table was not a standard deductions ledger, as is',
                    'expected when a result page has only one table.'
                ]))
                print('    URL: {}'.format(request.url))
        else:
            if len(tables) > 2:
                print(
                    ' '.join([
                        'WARNING: More tables discovered ({}) than expected',
                        '(2) on latest inspection page.',
                    ].format(len(tables)))
                )
                print('    URL: {}'.format(request.url))
                print('    Proceeding optimistically...')

            additional_inspection_rows = tables[1].find_all('tr')[1:]

            for _ in additional_inspection_rows:
                inspection_url_params = {'i': self.get_detail_page_id(_)}

                querystring = parse_qs(urlparse(self.get_url('list')).query)

                if 's' not in querystring or len(querystring['s']) == 0:
                    inspection_url_params['s'] = 100
                elif querystring['s'][0] != '100':
                    print(
                        ' '.join([
                            'ERROR: Unexpected "s" value in',
                            'detail-page querystring.',
                        ])
                    )

                inspection_request = self.open_url(
                    'list',
                    params=inspection_url_params
                )

                inspection_soup = BeautifulSoup(
                    inspection_request.content,
                    'html.parser'
                )

                all_inspections.append(
                    self.parse_inspection(inspection_soup, request)
                )

        return all_inspections

    def parse_inspection(self, soup, request):
        graphs = soup.find_all('p')
        if len(graphs) >= 3:
            if len(graphs) > 3:
                print('WARNING: More `p` tags discovered than were expected.')
                print('    Proceeding optimistically...')

            # Removed strong-tag removal for now, will replace text instead by
            # removing 'Date:' and 'Score:' manually.
            #
            # That way we'll get int conversion errors if we're actually
            # capturing demerits, since the prefix for that is 'Demerits:'
            # (which wouldn't be removed from the string under the logic above,
            # but would have been by the tag removal).
            # [
            #     [i.extract() for i in _.find_all('strong')]
            #     for _ in graphs
            # ]

            # inspection_date = datetime.strptime(
            #     text,
            #     '%B, %d %Y'
            # ).strftime('%Y-%m-%d')
            inspection_date = graphs[1].text.replace('Date:', '').strip()

            # inspection_score = int(
            #     graphs[2].text.replace('Score:', '').strip()
            # )
            inspection_score = graphs[2].text.replace('Score:', '').strip()

        else:
            if len(graphs) == 2:
                print('ERROR: Inspection does not list score.')
                print('    URL: {}'.format(request.url))

                inspection_date = graphs[1].text.replace('Date:', '').strip()
                inspection_score = None
            else:
                print('ERROR: Inspection does not list date or score.')
                print('    URL: {}'.format(request.url))

                inspection_date = None
                inspection_score = None

        tables = soup.find_all('table')

        violation_list = []
        if len(tables) == 0:
            print('ERROR: Zero tables discovered on inspection page.')
            print('    URL: {}'.format(request.url))

        else:
            proceed = False

            if len(tables) == 1:
                first_table_headers = tables[0].find_all('tr')[0]
                first_header_cell = first_table_headers.find_all('th')[0]

                if first_header_cell.text.lower() == 'points deducted':
                    # If there's only been one inspection of this
                    # establishment, there won't be any tabular links to other
                    # inspections for us to follow.
                    proceed = True
                else:
                    print(' '.join([
                        'ERROR: Only one table discovered on inspection page.',
                    ]))
                    print(' '.join([
                        'This table was not a standard deductions ledger,',
                        'as is expected when a result page has only one table.'
                    ]))
                    print('    URL: {}'.format(request.url))
            elif len(tables) > 2:
                print(
                    ' '.join([
                        'WARNING: More tables discovered ({}) than expected',
                        '(2) on inspection page.',
                    ])
                )
                print('    URL: {}'.format(request.url))
                print('    Proceeding optimistically...')

                proceed = True
            else:
                proceed = True

            if proceed is True:
                violation_nodes = tables[0].find_all('tr')[1:]

                violation_list = [
                    [td.text.strip() for td in _.find_all('td')]
                    for _ in violation_nodes
                ]

        return {
            'date': inspection_date,
            'raw_score': inspection_score,
            'violations': violation_list,
        }

    def get_formatted_inspection(self, raw_inspection):
        raw_date = raw_inspection['date']
        raw_score = raw_inspection['raw_score']

        inspected_date = None
        inspected_date_fmt = None
        inspection_score = None

        if raw_date is not None:
            inspected_date = datetime.strptime(raw_date, '%B, %d %Y')
            inspected_date_fmt = inspected_date.strftime('%Y-%m-%d')

        if raw_score is not None:
            inspection_score = int(raw_score.strip())

        formatted_inspection = {
            'date': inspected_date_fmt,
            'raw_score': inspection_score,
            'violations': [
                self.get_formatted_violation(_)
                for _ in raw_inspection['violations']
            ],
        }

        return formatted_inspection

    def get_formatted_violation(self, raw_violation):
        if len(raw_violation) == 1:
            return {
                'points_deducted': 0,
                'rule_violated': '',
                'corrective_action': '',
                'corrected_during_inspection': '',
                'extra_information': raw_violation[0],
            }

        was_corrected_during_inspection = (raw_violation[3].lower() == 'no')

        return {
            'points_deducted': int(raw_violation[0]),
            'rule_violated': raw_violation[1],
            'corrective_action': raw_violation[2],
            'corrected_during_inspection': was_corrected_during_inspection,
            'extra_information': None,
        }
