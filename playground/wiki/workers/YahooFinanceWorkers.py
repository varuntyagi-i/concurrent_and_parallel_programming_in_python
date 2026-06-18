import threading
import requests
from bs4 import BeautifulSoup
from lxml import html
import time
import random

class YahooFinancePriceScheduler(threading.Thread):
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
    def __init__(self, symbol, **kwargs):
        super(YahooFinancePriceWorker, self).__init__(**kwargs)
        self._symbol = symbol 
        base_url = "https://finance.yahoo.com/quote/"
        self._url = f'{base_url}{self._symbol}'
        self.start()

    def get_price(self):
        time.sleep(30*random.random())
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }

        api_url = f"https://query1.finance.yahoo.com/v8/finance/chart/{self._symbol}"
        response = requests.get(api_url, headers=headers, timeout=15)
        if response.status_code == 200:
            try:
                data = response.json()
                price = data["chart"]["result"][0]["meta"]["regularMarketPrice"]
                return float(price)
            except (ValueError, KeyError, TypeError, IndexError):
                pass

        response = requests.get(self._url, headers=headers, timeout=15)
        if response.status_code != 200:
            return

        page_contents = html.fromstring(response.text)
        raw_price_elements = page_contents.xpath('//fin-streamer[@data-field="regularMarketPrice" or @data-test="qsp-price"]')
        if raw_price_elements:
            raw_price = raw_price_elements[0].text_content().strip()
            try:
                return float(raw_price.replace(',', ''))
            except ValueError:
                return
        return
