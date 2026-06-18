import requests
from bs4 import BeautifulSoup

class WikiWorker():
    def __init__(self):
        self._url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    
    @staticmethod
    def _extract_company_symbols(page_html):
        soup = BeautifulSoup(page_html, 'lxml')
        table = soup.find(id="constituents")
        table_rows = table.find_all("tr")
        for table_row in table_rows[1:]:
            symbol = table_row.find('td').text.strip("\n")
            yield symbol
    
    def get_sp_500_companies(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
        }
        response = requests.get(self._url, headers=headers)
        if response.status_code != 200:
            print("Couldn't get entries")
            return []
        
        yield from self._extract_company_symbols(response.text)
