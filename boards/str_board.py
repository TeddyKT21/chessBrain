import numpy as np


class StrBoard:

    state_tuple = ("white's turn",
                   "white can castle queen side",
                   "white can castle king side",
                   "black can castle queen side",
                   "black can castle king side")

    def __init__(self):
        board_size = 8
        self.str_array = np.ndarray((board_size, board_size), dtype=str)
        self.state = {self.state_tuple[0]: True,
                      self.state_tuple[1]: True,
                      self.state_tuple[2]: True,
                      self.state_tuple[3]: True,
                      self.state_tuple[4]: True}

    def __init__(self, str_array=None, state=None):
        self.str_array = np.zeros((8, 8), dtype='U3') if str_array is None else str_array
        self.state = {self.state_tuple[0]: True,
                      self.state_tuple[1]: True,
                      self.state_tuple[2]: True,
                      self.state_tuple[3]: True,
                      self.state_tuple[4]: True} if state is None else state

    def __str__(self):
        return f"{self.str_array} \n state: {self.state}"
