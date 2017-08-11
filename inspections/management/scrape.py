# Imports from inspections.  # NOQA
from inspections.data_loader import save_establishment


def scrape_source(locale, verbose=False):
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
        from inspections.scrapers.tarrant_county import TarrantCountyScraper
        scraper = TarrantCountyScraper()
    else:
        print('Please specify a locale.')
        return None

    establishment_list = scraper.get_formatted_establishment_list(
        verbose=verbose
    )

    normalized_list = scraper.normalize_establishment_list(establishment_list)

    records_count = 1
    for i, _ in enumerate(normalized_list):
        if verbose is True:
            print(i)
        save_establishment(_)
        records_count = i

    print('Scraped {} records from {}'.format(
        records_count,
        scraper.locale
    ))
