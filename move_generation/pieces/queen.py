from move_generation.pieces.bishop import Bishop
from move_generation.pieces.piece import Piece
from move_generation.pieces.rook import Rook
from move_generation.short_board import board_size


class Queen(Rook, Bishop):
    attack_square_dict = {}
    white_move_dict = {}
    black_move_dict = {}
    for i in range(board_size):
        for j in range(board_size):
            possible_locations_arr = []
            for k in range(board_size):
                for m in range(board_size):
                    if (abs(i - k) == abs(j - m) or ((k == i) != (j == m))) and not (i == k and j == m):
                        possible_locations_arr += [k, m]
            attack_square_dict[i + 10 * j] = possible_locations_arr
    Piece.generate_move_dicts(attack_square_dict, white_move_dict, black_move_dict, 'queen')

    def __init__(self, i, j, short_board, game_engine):
        super().__init__(i, j, short_board, game_engine)
        self.move_dict = self.white_move_dict if self.color_bit == 0 else self.black_move_dict

    def consider_board(self, moves, empty_move_array=None, empty_attack_map=None):
        # bishop_moves = []
        # bishop_attack_map = []
        # Rook.consider_board(self, moves, empty_move_array, empty_attack_map)
        # Bishop.consider_board(self, moves, bishop_moves, bishop_attack_map)
        # empty_move_array += bishop_moves
        # empty_attack_map += bishop_attack_map
        return Rook.consider_board(self, moves) + Bishop.consider_board(self, moves)

    def was_moved(self, move):
        return move[1][0] == self.i and move[1][1] == self.j

    def move_does_influence(self, move):
        for change in move:
            for m in self.attack_map_moves:
                if change[0] == m[0][0] and change[1] == m[0][1]:
                    return True
        return False
