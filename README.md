# Restaurant inspections

This is a collection of scrapers to scrape restaurant health inspection data from multiple cities around Dallas as inspections occur. The end goal is to scrape all cities in Dallas and Tarrant Counties.

Then the scraped data will be exported as Django models and imported into a searchable database.


## An important note

**This code is unlicensed** — that is, it has not been licensed for use outside _The Dallas Morning News_. The scrapers and UI included here are pre-release versions, and are primarily published here to showcase the significant contribution our former intern has made to this project. Future releases of this data (and a public-facing UI) may be forthcoming.


## Installation

To install this demo yourself, first create a new folder and clone this repo into it:

```sh
mkdir restaurant-inspections-demo && cd restaurant-inspections-demo
git clone git@github.com:DallasMorningNews/restaurant-inspections-demo.git .
```

Then create a virtual environment (Python 3 is recommended, and earlier Python versions are not known to be compatible), activate it and install dependencies:

```sh
virtualenv venv --python=python3
source venv/bin/activate
pip install -r requirements.txt
```

Next, create a file named `.env`, and copy and place the settings listed in `.env.example`. Most importantly, you'll need to specify a Postgres connection string in `DATABASE_URL` and set `DEBUG_MODE=on`.

Then you'll need to initialize your database tables.

```sh
python manage.py migrate
```

To scrape a locale's data, run `python manage.py scrape <your_locale>` (for instance, `python manage.py scrape dallas`). Note: this will take awhile to run.

Once your scraping task has completed, start the Django development web server:

```sh
python manage.py runserver
```

Note the web address shown in the line that resembles the following output:

```
Starting development server at http://127.0.0.1:8000/
```

Run the following command to get the address of a specific restaurant:

```sh
python manage.py shell -c 'from inspections.models import Establishment; print("http://your-url-here/{}".format(Establishment.objects.all()[0].get_absolute_url().lstrip("/")))'
```

Replace `http://your-url-here/` with the name of the web address shown here. Open to see your restaurant page!

You can also add `card/` to the end of that URL to see a compact view for embedding in other pages.


## Cities to be included:

[Dallas](https://www.dallasopendata.com/City-Services/Restaurant-and-Food-Establishment-Inspections/dri5-wcct/data)

[Carrollton](http://www.cityofcarrollton.com/departments/departments-a-f/environmental-quality-services/food-consumer-safety/restaurant-scores)

[Plano](https://ecop.plano.gov/restaurantscores/)

[Fort Worth](http://apps.fortworthtexas.gov/health/)

[Tarrant County (with some exclusions)](https://publichealth.tarrantcounty.com/foodinspection/)


## Copyright

&copy; 2017 _The Dallas Morning News_. All rights reserved.
