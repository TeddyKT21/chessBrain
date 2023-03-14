import copy

import numpy as np


class ByteBoard:
    def __init__(self):
        board_size = 8
        self.byte_array = np.ndarray((board_size, board_size), dtype=bytes)
        self.state = 0b00000

    def __init__(self, byte_array, state):
        self.byte_array = byte_array
        self.state = state

    def __str__(self):
        return f"{self.byte_array} \n state: {bin(self.state)}"

    def __deepcopy__(self, memodict={}):
        self_copy = type(self)(self.byte_array,self.state)
        self_copy.__dict__.update(self.__dict__)
        self_copy.byte_array = copy.deepcopy(self.byte_array)
        return self_copy

