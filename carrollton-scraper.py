# main link, no no url params http://www.cityofcarrollton.com/departments/departments-a-f/environmental-quality-services/food-consumer-safety/restaurant-scores
# iframe link, with url param for each restaurant (&s=100&i=xxxxx) http://inspecthub.com/remote.cfm?k=F84JD93JJDOE83JFOE9JFK3893NFI938

import json
import logging
import os
import urllib3
from bs4 import BeautifulSoup
import requests
from urllib.request import urlopen

FEED_URL= ('http://www.cityofcarrollton.com/departments/departments-a-f/environmental-quality-services/food-consumer-safety/restaurant-scores')

def get_html():
    html = requests.get(FEED_URL).content
    soup = BeautifulSoup(html,"html.parser")
    iframe = soup.find('iframe')
    iframesrc = requests.get(iframe.attrs['src']).content
    # iframesrc = requests.get(iframe.attrs['src'], params={'s':100, 'i':restaurant-id}).content
    return iframesrc

def get_link():
    iframe = get_html()
    soup = BeautifulSoup(iframe, "html.parser")
    table = soup.find('tbody')
    results = []
    for row in table.find_all('tr'):
        results.append(row['onclick'])
    return results


# print(get_html())
print(get_link())
