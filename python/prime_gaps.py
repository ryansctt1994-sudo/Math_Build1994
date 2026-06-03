import math

import matplotlib.pyplot as plt


def simple_sieve(limit: int) -> list[int]:
    """Return all primes up to limit."""
    if limit < 2:
        return []

    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[0:2] = b"\x00\x00"

    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            start = i * i
            sieve[start : limit + 1 : i] = b"\x00" * (((limit - start) // i) + 1)

    return [i for i, flag in enumerate(sieve) if flag]


def prime_gaps(limit: int) -> tuple[list[int], list[int]]:
    primes = simple_sieve(limit)
    gaps = [primes[i + 1] - primes[i] for i in range(len(primes) - 1)]
    return primes[:-1], gaps


def main() -> None:
    limit = 1_000_000
    xs, gaps = prime_gaps(limit)

    if not gaps:
        print("No gaps found.")
        return

    print(f"Checked primes up to {limit:,}")
    print(f"Largest gap: {max(gaps)}")

    ratios = [gap / (math.log(p) ** 2) for p, gap in zip(xs, gaps)]

    plt.figure(figsize=(10, 5))
    plt.scatter(xs, ratios, s=1, alpha=0.5)
    plt.xlabel("Prime p")
    plt.ylabel("gap divided by log(p)^2")
    plt.title("Prime gap ratios")
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    main()
