import numpy as np
import pandas as pd

class Bucket:

    def __init__(self, num, cap):
        self.num = num
        self.cap = cap
        self.vec_load = np.zeros(8)

B1 = Bucket(1,28)

print(B1.vec_load)
