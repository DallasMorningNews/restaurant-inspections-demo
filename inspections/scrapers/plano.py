# Imports from python.  # NOQA
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

        data = ''.join([
            '{"criteria":{',
            '"restaurantName":"",',
            '"isStartWith":true,',
            '"gradeList":["A","B","C","D","F"],',
            '"foodTypeList":[],',
            '"zipcodeList":[],',
            '"address":"",',
            '"zipcode":""',
            '}}'
        ])

        r = self.open_url(
            'list',
            http_method='POST',
            headers=headers,
            data=data
        )

        raw_restaurant_list = json.loads(r.json()['d'])

        return raw_restaurant_list.get('restaurantDetailList', {})

    def get_formatted_establishment_list(self):
        # Get the raw list of establishments.
        data = self.get_raw_establishment_list()

        restaurant_dict = []
        for restaurant in data:
            name = restaurant.get('name', '')
            address = restaurant.get('address', '')
            locationID = restaurant.get('locationId', '')
            grade = restaurant.get('grade', '')
            recentInspectedDate = restaurant.get('recentInspectedDate', '')

            individualrestaurant = {
                'establishment_name': name,
                'address': address,
                'city': "Plano",
                'restaurantID': locationID,
                'latestInspectionGrade': grade,
                'latestInspectionDate': recentInspectedDate
            }

            restaurant_dict.append(individualrestaurant)

        return [self.get_formatted_establishment(_) for _ in restaurant_dict]

    def get_raw_establishment(self, establishment_object):
        headers = {
            'Content-Type': 'application/json; charset=UTF-8'
        }

        data_raw = {
            'locationId': establishment_object['restaurantID'],
            'invId': 1,
        }
        data = json.dumps(data_raw)

        r = self.open_url(
            'establishment_detail',
            http_method='POST',
            headers=headers,
            data=data
        )
        restaurant = json.loads(r.json()['d'])

        return restaurant

    def get_formatted_establishment(self, establishment_raw):
        establishment = self.get_raw_establishment(establishment_raw)

        establishment['address'] = establishment_raw.get('address', '')
        establishment['city'] = establishment_raw.get('city', '')
        establishment['establishment_name'] = establishment_raw.get(
            'establishment_name',
            ''
        )
        establishment['restaurantID'] = establishment_raw.get('restaurantID')

        return establishment
