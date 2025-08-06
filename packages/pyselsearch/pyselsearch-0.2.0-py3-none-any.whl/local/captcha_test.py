import json

from pyselsearch import GoogleSearch


scraper = GoogleSearch(headless=False, proxy="prime:6a0JL4uChppl@proxies.hawker.news:12852")
results = scraper.search('site:housing.com (inurl:/in/buy/projects/ OR inurl:-pid-) "PR/GJ/AHMEDABAD/AHMEDABAD CITY/AUDA/MAA12389/061023"',
                         sleep_time=2)
print(json.dumps(results, indent=3))