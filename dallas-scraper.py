# API endpoint: https://www.dallasopendata.com/resource/44uy-sq8p.json
# original score search: http://www2.dallascityhall.com/FoodInspection/SearchScores.cfm
# database landing page: https://www.dallasopendata.com/City-Services/Restaurant-and-Food-Establishment-Inspections/dri5-wcct/
# socrata help: https://dev.socrata.com/consumers/getting-started.html

from datetime import datetime, time, timedelta
import json
import logging
import os
# import urllib2
import requests

FEED_URL= ('https://www.dallasopendata.com/resource/44uy-sq8p.json')

r = requests.get(FEED_URL)
if r.status_code == 200:
    data = r.json()
    # print(data)

def load_data(raw_data):
    row_dict = []
    for item in raw_data:
        row_dict.append(parse_inspection(item))
    return row_dict

def parse_inspection(raw_inspection):
    return {
    "2f7u_region_code": raw_inspection.get(':@computed_region_2f7u_b5gs', None),
    "sjyw_region_code": raw_inspection.get(':@computed_region_sjyw_rtbm', None),
    "inspection_date": raw_inspection.get('inspection_date', None),
    "inspection_score": raw_inspection.get('inspection_score', None),
    "inspection_type": raw_inspection.get('inspection_type', None),
    "inspection_year": raw_inspection.get('inspection_year', None),
    "lat_lon": raw_inspection.get('lat_long', {'coordinates':[]})['coordinates'],
    "city": raw_inspection.get('lat_long_city', None),
    "state": raw_inspection.get('lat_long_state', None),
    "zip": raw_inspection.get('lat_long_zip', None),
    "month": raw_inspection.get('month', None),
    "establishment_name": raw_inspection.get('program_identifier', None),
    "street_address": raw_inspection.get('street_address', None),
    "street_direction": raw_inspection.get('street_direction', None).strip(),
    "street_name": raw_inspection.get('street_name', None),
    "street_number": raw_inspection.get('street_number', None),
    "street_type": raw_inspection.get('street_type', None),
    "street_unit": raw_inspection.get('street_unit', None),
    "violations": parse_violations(raw_inspection)
    }

def parse_violations(inspection):
    # violations_dict = []
    for violation_num in range(1,25):
        if ('violation%s_points' % (violation_num)):
            description = ""
            if ('violation%s_description' % (violation_num)):
                description = inspection.get('violation%s_description' % (violation_num))
            else:
                description = inspection.get('violation_description_%s' % (violation_num))
            return {
            "points": inspection.get('violation%s_points' % (violation_num)),
            "memo": inspection.get('violation%s_memo' % (violation_num)),
            "text": inspection.get('violation%s_text' % (violation_num)),
            "description": description
            }
        else:
            break

test = load_data(data)
print(test)
