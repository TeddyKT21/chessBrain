import numpy as np

board_size = 8

piece_dict = {"pawn": {"white": 0b000000000001, "black": 0b000001000000},
              "knight": {"white": 0b000000000010, "black": 0b000010000000},
              "bishop": {"white": 0b000000000100, "black": 0b000100000000},
              "rook": {"white": 0b000000001000, "black": 0b001000000000},
              "queen": {"white": 0b000000010000, "black": 0b010000000000},
              "king": {"white": 0b000000100000, "black": 0b100000000000}}


class ShortBoard:
    def __init__(self, short_array=None, state=None):
        if short_array is not None and state:
            self.short_array = short_array
            self.state = state
            return
        self.short_array = np.zeros((board_size, board_size), dtype=np.short)
        self.state = 0b0000000011110
        for i in range(8):
            self.short_array[1,i] = piece_dict["pawn"]["white"]
            self.short_array[6, i] = piece_dict["pawn"]["black"]

        self.short_array[7, 0] = piece_dict["rook"]["black"]
        self.short_array[7, 7] = piece_dict["rook"]["black"]

        self.short_array[7, 1] = piece_dict["knight"]["black"]
        self.short_array[7, 6] = piece_dict["knight"]["black"]

        self.short_array[7, 2] = piece_dict["bishop"]["black"]
        self.short_array[7, 5] = piece_dict["bishop"]["black"]

        self.short_array[7, 4] = piece_dict["queen"]["black"]
        self.short_array[7, 3] = piece_dict["king"]["black"]

        self.short_array[0, 0] = piece_dict["rook"]["white"]
        self.short_array[0, 7] = piece_dict["rook"]["white"]

        self.short_array[0, 1] = piece_dict["knight"]["white"]
        self.short_array[0, 6] = piece_dict["knight"]["white"]

        self.short_array[0, 2] = piece_dict["bishop"]["white"]
        self.short_array[0, 5] = piece_dict["bishop"]["white"]

        self.short_array[0, 4] = piece_dict["queen"]["white"]
        self.short_array[0, 3] = piece_dict["king"]["white"]

    def __str__(self):
        return f"{self.short_array} \n state: {bin(self.state)}"
