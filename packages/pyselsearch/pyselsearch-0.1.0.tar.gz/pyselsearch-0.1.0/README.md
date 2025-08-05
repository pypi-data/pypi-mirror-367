# pyselsearch

Get Google Search results using browser as requests sometimes sucks. It includes support for proxy authentication, headless browsing, and customizable search result parsing.

## Features

- Headless and non-headless scraping
- Authenticated proxy support (`username:password@host:port`)
- Dynamic Chrome extension creation for proxy auth
- Undetected ChromeDriver (via SeleniumBase)
- CLI tool for quick usage

## Installation

Clone the repository and install in editable mode:

```bash
git clone https://github.com/jisan09/pyselsearch.git
cd pyselsearch
pip install -e .[dev]
```

## Usage

### Python

```python
from pyselsearch.core import GoogleSearch

scrape = GoogleSearch(proxy="username:password@host:port")
results =scrape.search("OpenAI ChatGPT")

for result in results:
    print(result["title"], result["url"])
```

### Command Line

```bash
pyselsearch "search query"
```

Additional options:

```bash
pyselsearch "search query" --no-headless --proxy "user:pass@host:port"
```

## Project Structure

```
pyselsearch/
├── core.py             # Google search implementation
├── cli.py              # CLI entry point
└──proxy_gen.py         # Chrome extension generator

```

## License

This project is licensed under the MIT License.
