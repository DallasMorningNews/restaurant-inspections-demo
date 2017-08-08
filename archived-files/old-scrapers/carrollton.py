# main link, no no url params:
# http://www.cityofcarrollton.com/departments/departments-a-f/
# environmental-quality-services/food-consumer-safety/
# restaurant-scores

# iframe link, with url param for each restaurant (&s=100&i=xxxxx):
# http://inspecthub.com/remote.cfm?k=F84JD93JJDOE83JFOE9JFK3893NFI938
import re
from urllib.parse import parse_qs, urlparse
import json
from bs4 import BeautifulSoup
import requests

FEED_URL = (''.join([
    'http://www.cityofcarrollton.com/departments/departments-a-f/',
    'environmental-quality-services/food-consumer-safety/restaurant-scores'
]))

IFRAME_URL = (''.join([
    'http://inspecthub.com/remote.cfm?k=',
    'F84JD93JJDOE83JFOE9JFK3893NFI938'
]))

def get_html():
    '''Gets HTML from main page and retrieves HTML from the iframe contained on the page

    :return iframesrc: HTML from the iframe that's not souped yet
    :rtype: HTML
    '''
    html = requests.get(FEED_URL).content
    soup = BeautifulSoup(html, 'html.parser')
    iframe = soup.find('iframe')
    iframesrc = requests.get(iframe.attrs['src']).content
    return iframesrc

def load_data():
    '''Main function to load all inspection data in an array

    :return row_dict: an array of every establishment and its health inspection information
    :rtype: array
    '''
    row_dict = []
    id_list = get_link_ids()
    for inspection_id in id_list:
        row_dict.append(parse_inspection(inspection_id))
    return row_dict

def get_link_ids():
    '''Retrieves inspection id's from URL's in an HTML page with list of all restaurants

    :return id_list: an array of inspection id's
    :rtype: array
    '''
    iframe = get_html()
    soup = BeautifulSoup(iframe, 'html.parser')
    table = soup.find('tbody')
    results = []
    for row in table.find_all('tr'):
        results.append(row['onclick'])
    id_list = []
    for link in results:
        url_match = re.search('^window.location=\'(.*)\'', link)
        inspection_url = urlparse(url_match.groups()[0])
        inspection_id = parse_qs(inspection_url.query)['i']
        id_list.append(inspection_id)
    return id_list

def parse_inspection(inspection_id):
    '''Parses an individual inspection page's HTML using its inspection id

    :param inspection_id: a unique id assigned to each inspection, added as a URL parameter
    :rtype: object
    '''
    inspection_page_html = requests.get(IFRAME_URL, params={'s':100, 'i':inspection_id}).content
    soup = BeautifulSoup(inspection_page_html, 'html.parser')
    body = soup.find('body')
    for name_and_address in body.find('h3'):
        clean_nad = clean_html_tags(name_and_address)
        clean_name = '-'.join(clean_nad.split('-')[:-1]).strip()
        clean_address = clean_nad.split('-')[-1].strip()
    for date in body.findAll('p')[1]:
        clean_date = date
    for score in body.findAll('p')[2]:
        clean_score = score
    return {
    "establishment_name": clean_name ,
    "street_address": clean_address,
    "city": "Carrollton",
    "inspection_date": clean_date.strip(),
    "inspection_score": clean_score.strip(),
    "violations": parse_violations(soup)
    }

def clean_html_tags(string):
    '''Cleans html tags from a string using the re.sub function

    :param string: a variable with HTML tags to clean, will be casted to string if not already string.
    :return clean_string: string without HTML tags
    :rtype: string
    '''
    clean_string = re.sub(r'(<\/?[^>]+(>|$))', r'', str(string))
    return clean_string

def parse_violations(inspection):
    '''Parses violations to make each violation an object in an array

    :param inspection: a souped HTML page for an individual inspection
    :return violations_dict: an array of violations where each violation is an object
    :rtype: array
    '''
    tbody = inspection.find('tbody')
    violations_dict = []
    for violation in tbody.findAll('tr'):
        points = violation.findAll('td')[0]
        description = violation.findAll('td')[1]
        memo = violation.findAll('td')[2]
        violation_info = {
            "points": clean_html_tags(points),
            "description": clean_html_tags(description),
            "memo": clean_html_tags(memo)
        }
        violations_dict.append(violation_info)
    return violations_dict
