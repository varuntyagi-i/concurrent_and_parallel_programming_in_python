import time

from workers.SleepyWorkers import SleepyWorker
from workers.SquaredSumWorkers import SquaredSumWorker

def main():
    calc_start_time = time.time()

    current_workers = []
    for i in range(5):
        maximum_value = (i+1) * 1e6
        squaredsum = SquaredSumWorker(n = int(maximum_value))
        current_workers.append(squaredsum)

    for i in range(len(current_workers)):
        current_workers[i].join()

    
    print(f"Calculating time for sum of square: {round(time.time() - calc_start_time)}")

    sleep_start_time = time.time()

    current_workers = []

    for seconds in range(1,6):
        sleepWorker = SleepyWorker(seconds, daemon=False) # daemon needs to be initialized before 
        current_workers.append(sleepWorker)

    for i in range(len(current_workers)):
        current_workers[i].join()

    print(f"sleep took: {round(time.time() - sleep_start_time)}")


if __name__ == "__main__":
    main()