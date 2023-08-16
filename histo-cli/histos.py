import numpy as np
import math


class Histos:
    def __init__(self, count: int):
        self.count = count

    def process(self, array: np.ndarray) -> np.ndarray:
        chunks = np.array_split(array, self.count)
        output = np.array([0.0] * self.count)

        for i in range(len(chunks)):
            output[i] = np.mean(chunks[i])

        return output
