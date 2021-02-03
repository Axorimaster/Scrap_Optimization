import numpy as np

class Bucket:

    def __init__(self, num, cap):
        self.num = num
        self.cap = cap
        self.vec_layer = np.zeros(10)

