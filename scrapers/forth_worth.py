# Imports from python.  # NOQA
import json


# Imports from other dependencies.
from mechanicalsoup import StatefulBrowser


# main link: http://apps.fortworthtexas.gov/health/
# link to view all establishments, paginates:
# http://apps.fortworthtexas.gov/health/FacilityList.aspx?Alpha=ALL
# clickable details

BASE_URL = 'http://apps.fortworthtexas.gov/health/'

INITIAL_URL = '{}/Main.aspx'.format(BASE_URL)

ALL_RESTAURANTS_LIST_URL = '{}/FacilityList.aspx?Alpha=ALL'.format(BASE_URL)


def get_restaurant_list():
    pass
