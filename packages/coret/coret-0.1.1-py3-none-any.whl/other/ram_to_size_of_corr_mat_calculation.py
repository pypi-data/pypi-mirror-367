"""
Compute the largest dimension n for an n×n dense matrix that fits into a
given memory budget, for 16-, 32-, or 64-bit floating-point numbers.

The script reports two values:
  • Full matrix (store every element)
  • Upper-triangle only (store one copy of each symmetric pair)
"""

import math


def max_n(memory_gib: float, bits: int, upper_triangle: bool = False) -> int:
    """
    Return the largest integer n such that an n×n matrix of the given
    precision fits into `memory_gib` GiB of RAM.

    Parameters
    ----------
    memory_gib : float
        Available memory in *binary* gibibytes (1 GiB = 1 073 741 824 bytes).
    bits : int
        Precision in bits per element: must be 16, 32 or 64.
    upper_triangle : bool, optional
        If True, assume you will store only the upper-triangle of the matrix.

    Returns
    -------
    int
        Maximum dimension n that fits in memory.
    """
    if bits not in (16, 32, 64):
        raise ValueError("bits must be one of 16, 32, 64")

    bytes_per_value = bits // 8
    bytes_available = memory_gib * (1024**3)  # convert GiB → bytes
    factor = 0.5 if upper_triangle else 1.0

    # n = floor( sqrt( bytes_available / (bytes_per_value * factor) ) )
    return int(math.floor(math.sqrt(bytes_available / (bytes_per_value * factor))))


if __name__ == "__main__":
    mem = float(input("How much RAM is available (GiB)? "))
    prec = int(input("Precision in bits (16 / 32 / 64)? "))

    n_full = max_n(mem, prec, upper_triangle=False)
    n_half = max_n(mem, prec, upper_triangle=True)

    print(f"\nWith {mem:g} GiB and {prec}-bit floats:")
    print(f"  • Full matrix   : up to n = {n_full:,d}")
    print(f"  • Upper-triangle: up to n = {n_half:,d}")
