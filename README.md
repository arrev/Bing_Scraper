# Bing_Scraper
This project is meant to scrape the entries of the Bing search engine.
Coded in python and relying on `requests` and `BeautifulSoup`

## Running the code
The script can be run from docker. To do so:
```
docker-compose build
docker-compose up -d
docker-compose exec -it bingscraper bash
python3 bing_scraper.py
```
The output files will be stored in a volume named `bingscraper_data`.

To run a query, it's as simple as instantiating the class `BingScraper()` and calling the method `scrape(query)`. Where query is the desired query we want to scrape.

The class has 2 optional flags:

- `pagination`: Boolean, whether if we want to paginate or not. True for pagination ( default is False )

- `output_file`: filename of the file where the output will be stored. If no output_file is given, the output urls will be printed in screen as a list.

