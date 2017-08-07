# Imports from inspections.  # NOQA
from inspections.scrapers import BulkDataScraper


MAX_RESULTS_NUM = 100000


class DallasScraper(BulkDataScraper):
    '''TK.

    '''
    score_type = 'TK'

    def __init__(self):
        BulkDataScraper.__init__(self, 'City of Dallas')

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
        simple_field_mapping = {
            # Source data field: New-object data field
            '2f7u_region_code': ':@computed_region_2f7u_b5gs',
            'sjyw_region_code': ':@computed_region_sjyw_rtbm',
            'inspection_date': 'inspection_date',
            'inspection_score': 'inspection_score',
            'inspection_type': 'inspection_type',
            'inspection_year': 'inspection_year',
            'city': 'lat_long_city',
            'state': 'lat_long_state',
            'zip': 'lat_long_zip',
            'month': 'month',
            'establishment_name': 'program_identifier',
            'street_address': 'street_address',
            'street_name': 'street_name',
            'street_number': 'street_number',
            'street_type': 'street_type',
            'street_unit': 'street_unit',
        }

        formatted_establishment = {
            # Remove second arg from `xx.get(yy, None)` as None is
            # the default.
            v: raw_establishment.get(k)
            for k, v in simple_field_mapping.items()
        }

        if 'coordinates' in raw_establishment.get('lat_long', {}):
            coords = raw_establishment.get('lat_long')['coordinates']
        else:
            coords = []
        formatted_establishment['lat_lon'] = coords

        formatted_establishment['street_direction'] = raw_establishment.get(
            'street_direction',
            ''
        ).strip(),

        formatted_establishment['violations'] = self.format_violations(
            raw_establishment
        )

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
                'points': 'violation{}_points'.format(_),
                # points_a: 'violation{}_points'.format(_),
                # points_b: 'violation_points_{}'.format(_),
                'description': 'violation{}_description'.format(_),
                # description_a: 'violation{}_description'.format(_),
                # description_b: 'violation_description_{}'.format(_),
                'memo': 'violation{}_memo'.format(_),
                'text': 'violation{}_text'.format(_),
            }

            if src_fields['points'] in raw_establishment:
                # description = ''
                # if description_a in raw_establishment:
                #     description = raw_establishment.get(
                #         src_fields['description_a']
                #     )
                # elif description_b in raw_establishment:
                #     description = raw_establishment.get(
                #         src_fields['description_b']
                #     )

                description = raw_establishment.get(src_fields['description'])

                violations.append({
                    'points': raw_establishment.get(src_fields['points']),
                    'memo': raw_establishment.get(src_fields['memo']),
                    'text': raw_establishment.get(src_fields['text']),
                    'description': description,
                })

        return violations
