# main link https://ecop.plano.gov/restaurantscores/
# no url params, paginates

import json
import requests

URL = ''.join([
    'https://ecop.plano.gov/restaurantscores/',
    'RestaurantScores.aspx/GetRestaurantList'
])

def get_restaurant_list():
    '''TK.

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
    r = requests.post(URL, headers=headers, data=data)
    restaurant_list = json.loads(r.json()['d'])
    return restaurant_list


def get_restaurant_inspections(locationID):
    '''TK.

    '''
    headers = { 'Content-Type': 'application/json; charset=UTF-8' }

    data = '{"locationId":9101,"invId":1}'

    r = requests.post(URL, headers=headers, data=data)

    restaurant = json.loads(r.json()['d'])

print(get_restaurant_list())
