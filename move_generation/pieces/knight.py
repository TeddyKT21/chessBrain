from move_generation.pieces.piece import Piece
from move_generation.board_util import remove_if_out_of_range
from move_generation.short_board import board_size


class Knight(Piece):
    attack_square_dict = {}
    white_move_dict = {}
    black_move_dict = {}
    for i in range(board_size):
        for j in range(board_size):
            possible_locations_arr = [i + 1, j + 2,
                                      i + 1, j - 2,
                                      i + 2, j - 1,
                                      i + 2, j + 1,
                                      i - 1, j + 2,
                                      i - 1, j - 2,
                                      i - 2, j + 1,
                                      i - 2, j - 1]
            remove_if_out_of_range(possible_locations_arr)
            attack_square_dict[i + j * 10] = possible_locations_arr
    Piece.generate_move_dicts(attack_square_dict, white_move_dict, black_move_dict, 'knight')

    def __init__(self, i, j, short_board, game_engine):
        super().__init__(i, j, short_board, game_engine)
        self.move_dict = self.white_move_dict if self.color_bit == 0 else self.black_move_dict

    def consider_board(self, moves, empty_move_array=None, empty_attack_map=None):
        pass

    def update(self, move=None):
        if move is None or self.was_moved(move) or self.move_does_influence(move):
            if move is not None and self.was_moved(move):
                self.i = move[0][0]
                self.j = move[0][1]
            self.attack_map_moves = self.move_dict[self.i + self.j * 10]
            self.filter_if_blocked()

    def move_does_influence(self, move):
        for k in range(len(move)):
            change = move[k]
            if abs(self.i - change[0]) == 2 and abs(self.j - change[1]) == 1 \
                    or abs(self.i - change[0]) == 1 and abs(self.j - change[1]) == 2:
                return True
        return False
