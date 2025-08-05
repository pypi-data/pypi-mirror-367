# sample.py

import numpy as np
from math import (
    sqrt,
)
from collections import Counter

print(np.array([1, 2, 3]))

def compute_area(radius):
    return np.pi * radius ** 2

result = sqrt(16)
count = Counter([1,2,2,3,3,3])

print(result, count)
