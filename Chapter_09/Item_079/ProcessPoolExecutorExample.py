# Contains the example code for running gcd
# with a ProcessPoolExecutor for parallelism

import time
from concurrent.futures import ProcessPoolExecutor  # Change the import


def gcd(pair):
    a, b = pair
    low = min(a, b)
    for i in range(low, 0, -1):
        if a % i == 0 and b % i == 0:
            return i
    raise RuntimeError("Not reachable")


NUMBERS = [
    (19633090, 22659730),
    (20306770, 38141720),
    (15516450, 22296200),
    (20390450, 20208020),
    (18237120, 19249280),
    (22931290, 10204910),
    (12812380, 22737820),
    (38238120, 42372810),
    (38127410, 47291390),
    (12923910, 21238110),
]


def main():
    start = time.perf_counter()
    pool = ProcessPoolExecutor(max_workers=8)  # changed to ProcessPoolExecutor
    results = list(pool.map(gcd, NUMBERS))  # noqa: F841
    end = time.perf_counter()
    delta = end - start
    print(f"Took {delta:.3f} seconds")


if __name__ == "__main__":
    main()
