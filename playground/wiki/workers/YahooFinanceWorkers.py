"""Yahoo Finance worker utilities.

Provides a background `Thread`-based scheduler and worker that fetch
the latest price for a given stock symbol. The worker prefers the
Yahoo JSON chart API and falls back to HTML parsing when necessary.

Notes:
- Uses a browser-like `User-Agent` header to avoid basic blocking.
- Uses a `requests.Session` with retries for transient failures.
"""

import threading
import requests
from bs4 import BeautifulSoup
from lxml import html
import time
import random
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

class YahooFinancePriceScheduler(threading.Thread):
    """Thread that pulls symbols from a queue and fetches prices.

    Each scheduled item spawns a `YahooFinancePriceWorker` to fetch
    a single symbol's price and prints the result. The scheduler
    exits when it receives the string "Done" from the queue.
    """

    def __init__(self, input_queue, **kwargs):
        super(YahooFinancePriceScheduler, self).__init__(**kwargs)
        self._input_queue = input_queue
        self.start()

    def run(self):
        while True:
            val = self._input_queue.get()
            if val == "Done":
                break

            yahooFinancePriceWorker = YahooFinancePriceWorker(symbol=val)
            price = yahooFinancePriceWorker.get_price()
            print(price)
            time.sleep(random.random())

class YahooFinancePriceWorker(threading.Thread):
    """Worker thread that retrieves the current price for `symbol`.

    The worker starts itself on construction so callers can create
    an instance and immediately call `get_price()` to perform the
    fetch on the thread's context.
    """

    def __init__(self, symbol, **kwargs):
        super(YahooFinancePriceWorker, self).__init__(**kwargs)
        self._symbol = symbol
        base_url = "https://finance.yahoo.com/quote/"
        self._url = f'{base_url}{self._symbol}'
        self.start()

    def get_price(self):
        """Fetch the latest price for the worker's symbol.

        Flow:
        1. Sleep a small random interval to avoid thundering-herd effects.
        2. Try the Yahoo `/v8/finance/chart/{symbol}` JSON endpoint.
           This returns the `regularMarketPrice` in the `meta` block.
        3. If the JSON endpoint fails or is unavailable, fall back to
           fetching the public quote page and parse the `fin-streamer`
           element that usually contains the displayed price.

        Returns a `float` price on success or `None` on failure.
        """

        # small randomized delay to reduce simultaneous requests
        time.sleep(30 * random.random())

        headers = {
            # Browser-like header reduces simple blocking by servers
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }

        # Create a session with retries for transient failures (429/5xx)
        session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
        )
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        # Prefer the JSON chart API which is easier to parse reliably
        api_url = f"https://query1.finance.yahoo.com/v8/finance/chart/{self._symbol}"
        try:
            response = session.get(api_url, headers=headers, timeout=15)
            if response.status_code == 200:
                try:
                    data = response.json()
                    price_block = data.get("chart", {}).get("result", [None])[0]
                    if price_block:
                        meta = price_block.get("meta", {})
                        rm = meta.get("regularMarketPrice")
                        if rm is not None:
                            return float(rm)
                except (ValueError, KeyError, TypeError, IndexError):
                    # fall through to HTML parsing
                    pass
        except requests.RequestException:
            # network / timeout / connection errors -> try fallback
            pass

        # Fallback: parse the public HTML page. This is less reliable
        # but still works for many symbols when the JSON endpoint is
        # restricted or returns an error.
        try:
            response = session.get(self._url, headers=headers, timeout=15)
        except requests.RequestException:
            return

        if response.status_code != 200:
            return

        page_contents = html.fromstring(response.text)
        # fin-streamer elements often hold the numeric price in the page
        raw_price_elements = page_contents.xpath('//fin-streamer[@data-field="regularMarketPrice" or @data-test="qsp-price"]')
        if raw_price_elements:
            raw_price = raw_price_elements[0].text_content().strip()
            try:
                return float(raw_price.replace(',', ''))
            except ValueError:
                return
        return
