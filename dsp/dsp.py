import numpy as np

class MovingAvg:
    def __init__(self, size=3):
        self.size = size
        self.samples = np.zeros(self.size)

    def update(self, x):
        self.samples = np.roll(self.samples, -1)
        self.samples[-1] = x

    def get_avg(self):
        return np.average(self.samples)
        