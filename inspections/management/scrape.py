# Imports from inspections.  # NOQA
from inspections.data_loader import save_establishment


def scrape_source(locale):
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
    else:
        print('Please specify a locale.')
        return None

    establishment_list = scraper.get_formatted_establishment_list(verbose=True)

    normalized_list = scraper.normalize_establishment_list(establishment_list)

    for i, _ in enumerate(normalized_list):
        print(i)
        save_establishment(_)

    print('Done.')
