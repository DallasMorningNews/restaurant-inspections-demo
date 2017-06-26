# Imports from python.  # NOQA
import json


# Imports from other dependencies.
import requests


# main link https://ecop.plano.gov/restaurantscores/
# no url params, paginates
LIST_URL = ''.join([
    'https://ecop.plano.gov/restaurantscores/',
    'RestaurantScores.aspx/GetRestaurantList'
])

INSPECTION_URL = ''.join([
    'https://ecop.plano.gov/restaurantscores/',
    'RestaurantScores.aspx/GetRestaurantHistory',
])


def get_restaurant_list():
    '''Gets list of restaurant ID's via GetRestaurantList post

    :return restaurant_dict: an array of restaurant info
    :rtype: array
    '''
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
    r = requests.post(LIST_URL, headers=headers, data=data)
    raw_restaurant_list = json.loads(r.json()['d'])
    restaurant_list = raw_restaurant_list.get('restaurantDetailList')
    restaurant_dict = []
    for restaurant in restaurant_list:
        locationID = restaurant.get('locationId')
        grade = restaurant.get('grade')
        recentInspectedDate = restaurant.get('recentInspectedDate')
        individualrestaurant = {
            'restaurantID': locationID,
            'latestInspectionGrade': grade,
            'latestInspectionDate': recentInspectedDate
        }
        restaurant_dict.append(individualrestaurant)

    return restaurant_dict


def get_restaurant_inspection(restaurant_dict, start_val=0, end_val=None):
    '''TK.

    '''
    headers = {
        'Content-Type': 'application/json; charset=UTF-8'
    }

    if end_val is None:
        end_val = len(restaurant_dict)

    inspections_dict = []
    for counter, item in enumerate(restaurant_dict):
        if start_val <= (counter+1) <= end_val:
            data_raw = {
                'locationId': item['restaurantID'],
                'invId': 1,
            }
            data = json.dumps(data_raw)

            print('Getting item #{}'.format(counter))

            r = requests.post(INSPECTION_URL, headers=headers, data=data)

            restaurant = {r.json()['d']}
            inspections_dict.append(restaurant)

        # # restaurant.append(locationID)

    return inspections_dict
