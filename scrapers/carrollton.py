# Imports from python.  # NOQA
# import json
# import logging
# import os
import re
from urllib.parse import parse_qs, urlparse  # NOQA
# from urllib.request import urlopen
# import urllib3


# Imports from other dependencies.
from bs4 import BeautifulSoup
import requests


# main link, no no url params:
# http://www.cityofcarrollton.com/departments/departments-a-f/
# environmental-quality-services/food-consumer-safety/
# restaurant-scores

# iframe link, with url param for each restaurant (&s=100&i=xxxxx):
# http://inspecthub.com/remote.cfm?k=F84JD93JJDOE83JFOE9JFK3893NFI938


FEED_URL = (''.join([
    'http://www.cityofcarrollton.com/departments/departments-a-f/',
    'environmental-quality-services/food-consumer-safety/restaurant-scores'
]))

IFRAME_URL = (''.join([
    'http://inspecthub.com/remote.cfm?k=F84JD93JJDOE83JFOE9JFK3893NFI938'
]))


def get_html():
    '''TK.

    '''
    html = requests.get(FEED_URL).content
    soup = BeautifulSoup(html, 'html.parser')
    iframe = soup.find('iframe')
    iframesrc = requests.get(iframe.attrs['src']).content
    # iframesrc = requests.get(
    #     iframe.attrs['src'],
    #     params={'s': 100, 'i': 'restaurant-id'}
    # ).content
    return iframesrc


def get_iframe_html():
    '''TK.

    '''
    html = requests.get(IFRAME_URL).content
    soup = BeautifulSoup(html, 'html.parser')

    return soup


def get_inspection_id(onclick_text):
    '''TK.

    '''
    url_match = re.search('^window.location=\'(.*)\'', onclick_text)
    inspection_url = urlparse(url_match.groups()[0])
    inspection_id = parse_qs(inspection_url.query)['i']

    return inspection_id

# print(get_html())
