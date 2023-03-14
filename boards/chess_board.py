import numpy as np
import converters


class ChessBoard:
    board_size = 8

    def __init__(self):
        self.byte_board = np.ndarray((self.board_size, self.board_size), dtype=bytes)
        self.binary = 0
        self.str_board = converters.byte_board_to_str_board(self.byte_board)

    def __init__(self, num_board):
        self.byte_board = converters.binary_to_byte_board(num_board)
        self.binary = num_board
        self.str_board = converters.byte_board_to_str_board(self.byte_board)

    def __str__(self):
        return f'{self.byte_board}\n{self.str_board}'
