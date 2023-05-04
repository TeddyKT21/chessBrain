from move_generation.pieces.piece import Piece
from move_generation.converters import color_bit_dict
from move_generation.short_board import board_size


class Bishop(Piece):
    attack_square_dict = {}
    white_move_dict = {}
    black_move_dict = {}
    for i in range(board_size):
        for j in range(board_size):
            possible_locations_arr = []
            for k in range(board_size):
                for m in range(board_size):
                    if abs(i - k) == abs(j - m) and i != k:
                        possible_locations_arr += [k, m]
            attack_square_dict[i + 10 * j] = possible_locations_arr

    Piece.generate_move_dicts(attack_square_dict, white_move_dict, black_move_dict, 'bishop')

    def __init__(self, i, j, short_board, game_engine):
        super().__init__(i, j, short_board, game_engine)
        self.move_dict = self.white_move_dict if self.color_bit == 0 else self.black_move_dict

    def consider_board(self, moves, empty_move_array=None, empty_attack_map=None):
        i, j = self.i, self.j
        d_one_max, d_one_min, d_two_max, d_two_min = j, j, j, j
        d = 1
        while i + d < board_size and j + d < board_size:
            d_one_max += 1
            if self.short_board.short_array[i + d, j + d] != 0:
                break
            d += 1
        d = 1
        while i - d >= 0 and j + d < board_size:
            d_two_max += 1
            if self.short_board.short_array[i - d, j + d] != 0:
                break
            d += 1

        d = 1
        while i + d < board_size and j - d >= 0:
            d_two_min -= 1
            if self.short_board.short_array[i + d, j - d] != 0:
                break
            d += 1

        d = 1
        while i - d >= 0 and j - d >= 0:
            d_one_min -= 1
            if self.short_board.short_array[i - d, j - d] != 0:
                break
            d += 1
        # for m in moves:
        #     if (m[0][0] - self.i == m[0][1] - self.j and d_one_min <= m[0][1] <= d_one_max) or \
        #             (m[0][0] - self.i == -1 * (m[0][1] - self.j) and d_two_min <= m[0][1] <= d_two_max):
        #         empty_attack_map.append(m)
        #         if color_bit_dict[self.short_board.short_array[m[0][0], m[0][1]]] != self.color_bit:
        #             empty_move_array.append(m)
        return [m for m in moves if (m[0][0] - self.i == m[0][1] - self.j and d_one_min <= m[0][1] <= d_one_max) or
                (m[0][0] - self.i == -1 * (m[0][1] - self.j) and d_two_min <= m[0][1] <= d_two_max)]

    def move_does_influence(self, move):
        for change in move:
            for m in self.attack_map_moves:
                if change[0] == m[0][0] and change[1] == m[0][1]:
                    return True
        return False
