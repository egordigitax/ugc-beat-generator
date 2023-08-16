import numpy as np
import struct


class Packer:
    def pack(self, array: np.ndarray) -> bytes:
        return struct.pack("={}f".format(array.shape[0]), *array)