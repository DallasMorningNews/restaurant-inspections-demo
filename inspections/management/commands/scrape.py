# Imports from django.  # NOQA
from django.core.management.base import BaseCommand, CommandError  # NOQA


# Imports from inspections.
from inspections.data_loader import save_establishment


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        parser.add_argument('locale', nargs='+', type=str)

    def handle(self, *args, **options):
        for locale in options['locale']:
            verbose = True

            self.stdout.write('Running scraper for "{}"'.format(locale))

            if locale == 'carrollton':
                from inspections.scrapers.carrollton import CarrolltonScraper
                scraper = CarrolltonScraper()
            elif locale == 'dallas':
                from inspections.scrapers.dallas import DallasScraper
                scraper = DallasScraper()
            elif locale == 'fort_worth':
                from inspections.scrapers.fort_worth import FortWorthScraper
                scraper = FortWorthScraper()
            elif locale == 'plano':
                from inspections.scrapers.plano import PlanoScraper
                scraper = PlanoScraper()
            elif locale == '':
                from inspections.scrapers.tarrant_county import (
                    TarrantCountyScraper
                )
                scraper = TarrantCountyScraper()
            else:
                print('Please specify a locale.')
                return None

            establishment_list = scraper.get_formatted_establishment_list(
                verbose=verbose
            )

            normalized_list = scraper.normalize_establishment_list(
                establishment_list
            )

            records_count = 1
            for i, _ in enumerate(normalized_list):
                if verbose is True:
                    print(i)
                save_establishment(_)
                records_count = i

            self.stdout.write(
                self.style.SUCCESS(
                    'Scraped {} records from {}'.format(
                        records_count,
                        scraper.locale
                    )
                )
            )
