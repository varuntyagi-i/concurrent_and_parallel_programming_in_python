"""Small runner that wires the Wikipedia scraper and Yahoo workers.

This module demonstrates a simple producer/consumer pattern using
`multiprocessing.Queue` and a handful of `YahooFinancePriceScheduler`
threads to fetch prices concurrently for the S&P 500 symbols.
"""

from YahooFinanceWorkers import YahooFinancePriceScheduler
from WikiWorker import WikiWorker
import time
from multiprocessing import Queue


def main():
    # Queue used to distribute symbols to scheduler threads
    symbol_queue = Queue()
    scraper_start_time = time.time()

    wikiWorker = WikiWorker()
    yahoo_finance_price_scheduler_threads = []
    num_yahoo_finance_price_workers = 4

    # Start scheduler threads (they start on construction)
    for i in range(num_yahoo_finance_price_workers):
        yahooFinancePriceScheduler = YahooFinancePriceScheduler(input_queue=symbol_queue)
        yahoo_finance_price_scheduler_threads.append(yahooFinancePriceScheduler)

    # Enqueue symbols produced by the Wiki scraper
    for symbol in wikiWorker.get_sp_500_companies():
        symbol_queue.put(symbol)

    # Signal termination to each scheduler thread
    for _ in range(len(yahoo_finance_price_scheduler_threads)):
        symbol_queue.put("Done")

    # Wait for all schedulers to finish
    for t in yahoo_finance_price_scheduler_threads:
        t.join()

    print('Extracting time took: ', round(time.time() - scraper_start_time, 1))


if __name__ == "__main__":
    main()