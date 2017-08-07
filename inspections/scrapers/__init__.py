# Imports from python.  # NOQA


# Imports from other dependencies.
from mechanicalsoup import StatefulBrowser
import requests


class Scraper(object):
    '''TK.

    '''
    urls = {}

    def __init__(self, locale=None, mode=None):
        self.locale = locale
        self.mode = mode

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

    def letterify_scores(self, raw_score):
        if raw_score >= 90:
            return 'A'
        elif raw_score >= 80:
            return 'B'
        elif raw_score >= 70:
            return 'C'
        elif raw_score >= 60:
            return 'D'

        return 'F'

    def get_normalized_score(self, score):
        if self.score_type == 'demerits':
            return self.letterify_scores(100 - score)
        elif self.score_type == 'numeric':
            return self.letterify_scores(score)
        elif self.score_type == 'letter_grade':
            return score


class BulkDataScraper(Scraper):
    '''TK.

    '''
    def __init__(self, locale):
        mode = 'bulk-data'
        Scraper.__init__(self, locale, mode)

    def get_formatted_establishment(self):
        raise NotImplementedError


class SequentialEnhancementScraper(Scraper):
    '''TK.

    '''
    def __init__(self, locale, mode):
        mode = 'sequential-enhancement'
        Scraper.__init__(self, locale, mode)

    def get_raw_establishment(self, establishment_id):
        raise NotImplementedError

    def get_formatted_establishment(self, raw_establishment):
        raise NotImplementedError


class CookieBasedScraper(SequentialEnhancementScraper):
    '''TK.

    '''
    def __init__(self, locale):
        mode = 'cookie-based'
        SequentialEnhancementScraper.__init__(self, locale, mode)

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
