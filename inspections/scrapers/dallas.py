# Imports from python.  # NOQA
from datetime import datetime


# Imports from inspections.
from inspections.scrapers import BulkDataScraper


MAX_RESULTS_NUM = 100000


class DallasScraper(BulkDataScraper):
    '''TK.

    '''
    def __init__(self):
        locale = 'City of Dallas'
        score_type = 'points'

        BulkDataScraper.__init__(
            self,
            locale=locale,
            score_type=score_type
        )

        results_limit_qs = '$limit={}'.format(MAX_RESULTS_NUM)

        self.set_url(
            'feed',
            'https://www.dallasopendata.com/resource/44uy-sq8p.json?{}'.format(
                results_limit_qs
            )
        )

    def get_raw_establishment_list(self):
        '''Main function to load all establishment data in an array.

        :param raw_data: JSON received from the requests.get function
        :return row_dict: Array of all establishments and their info.
        :rtype: array
        '''

        r = self.open_url('feed')

        if r.status_code == 200:
            return r.json()

        print(
            'Warning: HTTP GET request for "{0}" returned code {1}.'.format(
                r.url,
                r.status_code
            )
        )
        return []

    def get_formatted_establishment_list(self):
        '''TK.

        '''
        # Get the raw list of establishments.
        data = self.get_raw_establishment_list()

        return [self.get_formatted_establishment(item) for item in data]

    def get_formatted_establishment(self, raw_establishment):
        '''Formats an establishment object for placement into a database.

        Called via a for loop in get_formatted_establishment_list() to
        clean up variable names and parse violations into their own
        component objects.

        :param raw_establishment: JSON instance of an establishment.
        :return formatted_establishment: Consistently-formatted
            establishment object, with sub-objects for each violation.
        :rtype: object
        '''
        formatted_establishment = {
            'establishment_name': raw_establishment.get('program_identifier'),
            'address': raw_establishment.get('site_address', ''),
            'city': 'Dallas',
            'zip_code': raw_establishment.get('zip'),
        }

        inspection_list = []

        raw_date = raw_establishment.get('insp_date', None)
        raw_score = raw_establishment.get('score', None)

        inspection_date = None
        if raw_date is not None:
            date_obj = datetime.strptime(raw_date, '%Y-%m-%dT%H:%M:%S.%f')
            inspection_date = date_obj.strftime('%Y-%m-%d')

        initial_score = None
        if raw_score is not None:
            initial_score = int(raw_score)

        inspection_list.append({
            'inspection_type': raw_establishment['type'],
            'date': inspection_date,
            'raw_score': initial_score,
            'violations': self.format_violations(raw_establishment),
        })

        formatted_establishment['inspections'] = inspection_list

        # if 'coordinates' in raw_establishment.get('lat_long', {}):
        #     coords = raw_establishment.get('lat_long')['coordinates']
        # else:
        #     coords = []
        # formatted_establishment['lat_lon'] = coords
        #
        # formatted_establishment['street_direction'] = raw_establishment.get(
        #     'street_direction',
        #     ''
        # ).strip(),
        #
        # formatted_establishment['violations'] = self.format_violations(
        #     raw_establishment
        # )

        return formatted_establishment

    def format_violations(self, raw_establishment):
        '''Recasts an establishment's violations to individual objects.

        :param raw_establishment: JSON instance of an establishment.
        :return violations_formatted: List of consistently-formatted
            violation objects, ready for database loading.
        :rtype: object
        '''
        violations = []

        for _ in range(1, 25):
            # NOTE: Commented-out lines reflect past inconsistent use of
            # 'violationX_description' and 'violation_description_X'
            # (each was used for some violation numbers, depending on
            # how big X was), an arbitrary & pointless distinction that
            # appears to have been removed sometime before August 2017.

            src_fields = {
                'points_deducted': 'violation{}_points'.format(_),
                # points_a: 'violation{}_points'.format(_),
                # points_b: 'violation_points_{}'.format(_),
                'infraction_category': 'violation{}_description'.format(_),
                # description_a: 'violation{}_description'.format(_),
                # description_b: 'violation_description_{}'.format(_),
                'inspector_comment': 'violation{}_memo'.format(_),
                'statute_citation': 'violation{}_text'.format(_),
            }

            if src_fields['points_deducted'] in raw_establishment:
                # description = ''
                # if description_a in raw_establishment:
                #     description = raw_establishment.get(
                #         src_fields['description_a']
                #     )
                # elif description_b in raw_establishment:
                #     description = raw_establishment.get(
                #         src_fields['description_b']
                #     )

                violations.append({
                    'points_deducted': int(raw_establishment.get(
                        src_fields['points_deducted']
                    )),
                    'inspector_comment': raw_establishment.get(
                        src_fields['inspector_comment'],
                        ''
                    ),
                    'statute_citation': raw_establishment.get(
                        src_fields['statute_citation'],
                        ''
                    ),
                    'infraction_category': raw_establishment.get(
                        src_fields['infraction_category'],
                        ''
                    ),
                })

        return violations
