# Imports from python.  # NOQA
from copy import deepcopy
from datetime import datetime
import json


# Imports from inspections.  # NOQA
from inspections.scrapers import SequentialEnhancementScraper


# Imports from other dependencies.
# import requests


class PlanoScraper(SequentialEnhancementScraper):
    '''TK.

    '''
    score_type = 'TK'

    def __init__(self):
        SequentialEnhancementScraper.__init__(self, 'City of Plano')

        self.set_url(
            'list',
            ''.join([
                'https://ecop.plano.gov/restaurantscores/',
                'RestaurantScores.aspx/GetRestaurantList',
            ])
        )

        self.set_url(
            'establishment_detail',
            ''.join([
                'https://ecop.plano.gov/restaurantscores/',
                'RestaurantScores.aspx/GetRestaurantHistory',
            ])
        )

    def get_raw_establishment_list(self):
        headers = {
            'Content-Type': 'application/json; charset=UTF-8',
        }

        data = {
            'criteria': {
                'restaurantName': '',
                'isStartWith': True,
                'gradeList': ['A', 'B', 'C', 'D', 'F'],
                'foodTypeList': [],
                'zipcodeList': [],
                'address': '',
                'zipcode': ''
            }
        }

        r = self.open_url(
            'list',
            http_method='POST',
            headers=headers,
            data=json.dumps(data)
        )

        raw_restaurant_list = json.loads(r.json()['d'])

        return raw_restaurant_list.get('restaurantDetailList', {})

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

        # # Get the raw list of establishments.
        # data = self.get_raw_establishment_list()
        #
        # establishments = []
        # for restaurant in data:
        #     name = restaurant.get('name', '')
        #     locationID = restaurant.get('locationId', '')
        #
        #     address_parts = restaurant.get('address', '').split(', Plano, TX')
        #
        #     formatted_establishment = {
        #         'establishment_name': name,
        #         'source_id': locationID,
        #         'address': address_parts[0].strip(),
        #         'city': 'Plano',
        #     }
        #
        #     if len(address_parts) > 1:
        #         formatted_establishment['zip_code'] = address_parts[1].strip()
        #
        #     establishments.append(formatted_establishment)
        #
        # return [self.get_formatted_establishment(_) for _ in establishments]

    def get_raw_establishment(self, establishment_obj):
        headers = {
            'Content-Type': 'application/json; charset=UTF-8'
        }

        data_raw = {
            'locationId': establishment_obj['locationId'],
            'invId': 1,
        }
        data = json.dumps(data_raw)

        r = self.open_url(
            'establishment_detail',
            http_method='POST',
            headers=headers,
            data=data
        )
        inspections = json.loads(r.json()['d'])

        establishment_obj['inspections'] = inspections['restaurantHistoryList']

        return establishment_obj

    def get_formatted_establishment(self, establishment_obj):
        establishment_raw = self.get_raw_establishment(establishment_obj)

        establishment_name = establishment_raw.get('name', '')
        source_id = establishment_raw.get('locationId')

        address_parts = establishment_raw.get('address', '').split(
            ', Plano, TX'
        )

        formatted_establishment = {
            'establishment_name': establishment_name,
            'source_id': source_id,
            'address': address_parts[0].strip(),
            'city': 'Plano',
        }

        if len(address_parts) > 1:
            formatted_establishment['zip_code'] = address_parts[1].strip()

        formatted_establishment['inspections'] = [
            self.get_formatted_inspection(_)
            for _ in establishment_raw['inspections']
        ]

        return formatted_establishment

    def get_raw_inspection(self, inspection_object):
        '''TK.

        '''
        return inspection_object

    def get_formatted_inspection(self, inspection_object):
        '''TK.

        '''
        raw_inspection = self.get_raw_inspection(inspection_object)

        if raw_inspection is None:
            return None

        raw_date = raw_inspection.get('date', None)
        raw_grade = raw_inspection.pop('grade', None)
        raw_inspection_type = raw_inspection.pop('name', None)
        raw_violations = raw_inspection.pop('violationList', [])

        formatted_inspection = deepcopy(raw_inspection)

        formatted_date = None
        if raw_date is not None:
            date_obj = datetime.strptime(raw_date, '%m/%d/%Y')
            formatted_date = date_obj.strftime('%Y-%m-%d')

        formatted_inspection['date'] = formatted_date

        formatted_grade = None
        if raw_grade is not None:
            formatted_grade = raw_grade

        formatted_inspection['raw_score'] = formatted_grade

        if raw_inspection_type is not None:
            formatted_inspection_type = raw_inspection_type
            formatted_inspection['inspection_type'] = formatted_inspection_type

        formatted_inspection['violations'] = [
            self.get_formatted_violation(_)
            for _ in raw_violations
        ]

        return formatted_inspection

    def get_raw_violation(self, violation_object):
        '''TK.

        '''
        return violation_object

    def get_formatted_violation(self, violation_object):
        '''TK.

        '''
        raw_violation = self.get_raw_violation(violation_object)

        return {
            'severity': raw_violation.get('severity', ''),
            'infraction_category': raw_violation.get('description', ''),
            'inspector_comment': raw_violation.get('comment', '')
        }
