from YahooFinanceWorkers import YahooFinancePriceWorker
from WikiWorker import WikiWorker
import time

def main():
    scraper_start_time = time.time()

    wikiWorker = WikiWorker()
    current_workers = []

    for symbol in wikiWorker.get_sp_500_companies():
        yahooFinanceProceWorker = YahooFinancePriceWorker(symbol=symbol)
        current_workers.append(yahooFinanceProceWorker)

    
    for i in range(len(current_workers)):
        current_workers[i].join()

    print('Extracting time took: ', round(time.time() - scraper_start_time, 1))



if __name__ == "__main__":
    main()