"""Wikipedia scraper for S&P 500 company symbols.

This module fetches the Wikipedia page that lists S&P 500 companies
and yields their stock symbols. A browser-like `User-Agent` header
is used to avoid simple blocks by the site.
"""

import requests
from bs4 import BeautifulSoup


class WikiWorker():
    """Simple scraper that yields S&P 500 ticker symbols.

    Usage:
        wiki = WikiWorker()
        for symbol in wiki.get_sp_500_companies():
            process(symbol)
    """

    def __init__(self):
        self._url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

    @staticmethod
    def _extract_company_symbols(page_html):
        """Parse the constituents table and yield the ticker symbol for each row.

        The function expects the Wikipedia table with id="constituents" where
        each row's first data cell contains the ticker symbol.
        """
        soup = BeautifulSoup(page_html, 'lxml')
        table = soup.find(id="constituents")
        if not table:
            return
        table_rows = table.find_all("tr")
        for table_row in table_rows[1:]:
            # first td in the row holds the ticker symbol
            symbol = table_row.find('td').text.strip("\n")
            yield symbol

    def get_sp_500_companies(self):
        """Fetch the Wikipedia page and yield symbols.

        Returns an iterator (generator). On fetch failure an empty
        list-like iterator is returned.
        """
        headers = {
            # Use a common browser UA to reduce the chance of a 403
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
        }
        try:
            response = requests.get(self._url, headers=headers, timeout=15)
        except requests.RequestException:
            print("Couldn't get entries: network error")
            return []

        if response.status_code != 200:
            print("Couldn't get entries")
            return []

        yield from self._extract_company_symbols(response.text)
