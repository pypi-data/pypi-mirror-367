import json
from pyselsearch import GoogleSearch


def basic_example():
    query = "latest technology trends"
    scraper = GoogleSearch()
    data = scraper.search(query)
    print(json.dumps(data, indent=3, ensure_ascii=False))


def with_proxy():
    query = "best remote work tools"
    proxy = "user:pass@4.224.105.40:8080"  # Replace with actual working proxy
    scraper = GoogleSearch(proxy=proxy)
    data = scraper.search(query)
    print(json.dumps(data, indent=3, ensure_ascii=False))


def non_headless():
    query = "open source AI projects"
    scraper = GoogleSearch(headless=False)
    data = scraper.search(query)
    print(json.dumps(data, indent=3, ensure_ascii=False))


def full_example():
    query = (
        'site:housing.com (inurl:/in/buy/projects/ OR inurl:-pid-) '
        '"PR/GJ/AHMEDABAD/AHMEDABAD CITY/AUDA/MAA12389/061023"'
    )
    proxy = "prime:6a0JL4uChppl@proxies.hawker.news:12852"
    scraper = GoogleSearch(headless=False, proxy=proxy)
    data = scraper.search(query)
    print(json.dumps(data, indent=3, ensure_ascii=False))


if __name__ == "__main__":
    print("Running basic example...\n")
    basic_example()

    print("\nRunning with proxy...\n")
    with_proxy()

    print("\nRunning in non-headless mode...\n")
    non_headless()

