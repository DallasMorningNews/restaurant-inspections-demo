# Imports from python.  # NOQA
from copy import deepcopy


# Imports from other dependencies.
from mechanicalsoup import StatefulBrowser
import requests


class Scraper(object):
    '''TK.

    '''
    def __init__(self, locale=None, mode=None, score_type=None):
        self.locale = locale
        self.mode = mode
        self.score_type = score_type
        self.urls = {}

    def get_raw_establishment_list(self, establishment_id):
        raise NotImplementedError

    def get_formatted_establishment_list(self):
        raise NotImplementedError

    def get_formatted_establishment(self, establishment_raw):
        raise NotImplementedError

    def set_url(self, url_key, location):
        self.urls[url_key] = location

    def get_url(self, url_key):
        return self.urls[url_key]

    def open_url(self, url_key, http_method='GET', **kwargs):
        if http_method.upper() == 'GET':
            return requests.get(self.get_url(url_key), **kwargs)
        elif http_method.upper() == 'POST':
            return requests.post(self.get_url(url_key), **kwargs)

    def normalize_establishment_list(self, establishment_list):
        return [
            self.normalize_establishment(_) for _ in establishment_list
        ]

    def normalize_establishment(self, establishment):
        normalized_establishment = deepcopy(establishment)

        formatted_inspections = normalized_establishment.pop('inspections')

        normalized_establishment['inspections'] = [
            self.normalize_inspection(_) for _ in formatted_inspections
        ]

        return normalized_establishment

    def normalize_inspection(self, inspection):
        normalized_inspection = deepcopy(inspection)

        formatted_violations = normalized_inspection.pop('violations')

        normalized_inspection['violations'] = [
            self.normalize_violation(_) for _ in formatted_violations
        ]

        normalized_inspection['source_agency'] = self.locale

        number_grade = self.get_normalized_number_grade(
            inspection['raw_score']
        )
        normalized_inspection['normalized_numeric_grade'] = number_grade

        if self.score_type == 'letter_grade':
            letter_grade = inspection['raw_score']
        else:
            letter_grade = self.get_normalized_letter_grade(number_grade)

        normalized_inspection['normalized_letter_grade'] = letter_grade

        return normalized_inspection

    def normalize_violation(self, violation):
        normalized_violation = deepcopy(violation)

        return normalized_violation

    def get_normalized_letter_grade(self, raw_score):
        if raw_score >= 90:
            return 'A'
        elif raw_score >= 80:
            return 'B'
        elif raw_score >= 70:
            return 'C'
        elif raw_score >= 60:
            return 'D'

        return 'F'

    def get_normalized_number_grade(self, score):
        if self.score_type == 'demerits':
            return 100 - score
        elif self.score_type == 'points':
            return score
        elif self.score_type == 'letter_grade':
            return None

        raise NotImplementedError


class BulkDataScraper(Scraper):
    '''TK.

    '''
    def __init__(self, locale=None, score_type=None, mode=None):
        mode = 'bulk-data'
        Scraper.__init__(
            self,
            locale=locale,
            mode=mode,
            score_type=score_type
        )

    def get_formatted_establishment(self):
        raise NotImplementedError


class SequentialEnhancementScraper(Scraper):
    '''TK.

    '''
    def __init__(self, locale=None, score_type=None, mode=None):
        if mode is None:
            mode = 'sequential-enhancement'

        Scraper.__init__(
            self,
            locale=locale,
            mode=mode,
            score_type=score_type
        )

    def get_raw_establishment(self, establishment_id):
        raise NotImplementedError

    def get_formatted_establishment(self, raw_establishment):
        raise NotImplementedError


class CookieBasedScraper(SequentialEnhancementScraper):
    '''TK.

    '''
    def __init__(self, locale=None, score_type=None, mode=None):
        mode = 'cookie-based'
        SequentialEnhancementScraper.__init__(
            self,
            locale=locale,
            mode=mode,
            score_type=score_type
        )

        self.browser = StatefulBrowser(
            soup_config={'features': 'html.parser'}
        )

    def open_url(self, url_key, http_method='GET', **kwargs):
        if http_method.upper() == 'GET':
            self.browser.open(self.get_url(url_key))
            return self.browser.get_current_page()

        elif http_method.upper() == 'POST':
            raise NotImplementedError

    def update_browser_headers(self, new_headers):
        self.browser.session.headers.update(new_headers)

    def retrieve_form_payload(self, markup, payload_id_fields):
        '''TK.

        '''
        defined_keys = {
            _: markup.find(id=_)['value']
            for _ in payload_id_fields
            if 'value' in markup.find(id=_).attrs
        }

        existing_keys = defined_keys.keys()

        empty_keys = {
            _: ''
            for _ in payload_id_fields
            if _ not in existing_keys
        }

        return {**defined_keys, **empty_keys}  # NOQA
