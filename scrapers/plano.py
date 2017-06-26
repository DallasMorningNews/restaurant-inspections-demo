# main link https://ecop.plano.gov/restaurantscores/
# no url params, paginates

import json
import requests

LIST_URL = ''.join([
    'https://ecop.plano.gov/restaurantscores/',
    'RestaurantScores.aspx/GetRestaurantList'
])

INSPECTION_URL = ''.join([
    'https://ecop.plano.gov/restaurantscores/',
    'RestaurantScores.aspx/GetRestaurantHistory'
])

def get_restaurant_ids():
    '''Gets list of restaurant ID's via GetRestaurantList post

    :return locationID_dict: an array of restaurant location ID's
    :rtype: array:
    '''
    headers = { 'Content-Type': 'application/json; charset=UTF-8' }
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
    locationID_dict = []
    for restaurant in restaurant_list:
        locationID = restaurant.get('locationId')
        grade = restaurant.get('grade')
        recentInspectedDate = restaurant.get('recentInspectedDate')
        locationID_dict.append(locationID)
        locationID_dict.append(grade)
        locationID_dict.append(recentInspectedDate)
    return locationID_dict

def get_restaurant_inspection(locationID_dict):
    '''TK.

    '''
    headers = { 'Content-Type': 'application/json; charset=UTF-8' }

    for locationID in locationID_dict:
        data_raw = { 'locationId': locationID, 'invId': 1}
        data = json.dumps(data_raw)

        r = requests.post(INSPECTION_URL, headers=headers, data=data)

        # restaurant = r.json()['d']
        # # restaurant.append(locationID)

    return restaurant

ids = get_restaurant_ids()
print(get_restaurant_ids())
