from abc import ABC, abstractmethod

from move_generation.converters import color_bit_dict,short_piece_to_index_dict
from move_generation.short_board import board_size, piece_dict


class Piece(ABC):
    def __init__(self, i, j, short_board, game_engine):
        self.attack_map_moves = []
        self.i = i
        self.j = j
        self.short_board = short_board
        self.game_engine = game_engine
        self.color_bit = color_bit_dict[short_board.short_array[i, j]]
        self.board_size = short_board.short_array.shape[0]
        self.piece_index = short_piece_to_index_dict[short_board.short_array[i, j]]
        self.move_array = []
        self.move_dict = {}

    @abstractmethod
    def move_does_influence(self, move):
        pass

    @abstractmethod
    def consider_board(self, moves, empty_move_array=None, empty_attack_map=None):
        pass

    def was_moved(self, move):
        return move[1][0] == self.i and move[1][1] == self.j

    def revert_move(self, reverted_last_move):
        self.update(reverted_last_move)

    @staticmethod
    def generate_move_dicts(attack_square_dict, white_move_dict, black_move_dict, name):
        white_piece_value = piece_dict[name]['white']
        black_piece_value = piece_dict[name]['black']
        for i in range(board_size):
            for j in range(board_size):
                attack_squares = attack_square_dict[i + 10 * j]
                possible_white_moves = []
                possible_black_moves = []
                for k in range(0, len(attack_squares), 2):
                    white_move = ((attack_squares[k], attack_squares[k + 1], white_piece_value), (i, j, 0))
                    possible_white_moves.append(white_move)
                    black_move = ((attack_squares[k], attack_squares[k + 1], black_piece_value), (i, j, 0))
                    possible_black_moves.append(black_move)
                white_move_dict[i + 10 * j] = possible_white_moves
                black_move_dict[i + 10 * j] = possible_black_moves

    def __str__(self):
        color = 'white' if self.color_bit == 0 else 'black'
        return f"{color} {str(type(self)).split('.')[2].split(''''>''')[0]} at {self.i, self.j} "

    def get_moves(self):
        king = self.game_engine.white_king if self.color_bit == 0 else self.game_engine.black_king
        if king.i == self.i or king.j == self.j or abs(self.i - king.i) == abs(self.j - king.j):
            return self.filter_pins(king)
        return self.move_array

    def update(self, move=None):
        was_moved = self.was_moved(move) if move else None
        if move is None or was_moved or self.move_does_influence(move):
            if move is not None and was_moved:
                self.i = move[0][0]
                self.j = move[0][1]
            self.attack_map_moves = self.consider_board(self.move_dict[self.i + self.j * 10])
            self.filter_if_blocked()

    def filter_if_blocked(self):
        self.move_array = [m for m in self.attack_map_moves if self.short_board.short_array[m[0][0], m[0][1]] == 0 or
                           color_bit_dict[self.short_board.short_array[m[0][0], m[0][1]]] != self.color_bit]

    def filter_pins(self, king, moves_to_filter=None):
        move_array = self.move_array if not moves_to_filter else moves_to_filter

        delta_i, delta_j = king.i - self.i, king.j - self.j
        on_diagonal = abs(delta_i) == abs(delta_j)
        on_straight = delta_i == 0 or delta_j == 0
        distance = max(abs(delta_i), abs(delta_j))
        i_step, j_step = delta_i // distance, delta_j // distance
        i, j = self.i, self.j
        for k in range(1, distance):
            if self.short_board.short_array[i + k * i_step, j + k * j_step] != 0:
                return move_array

        i -= i_step
        j -= j_step
        while 0 <= i < board_size and 0 <= j < board_size:
            other_piece = self.short_board.short_array[i, j]
            if other_piece != 0:
                if color_bit_dict[other_piece] == king.color_bit:
                    return move_array
                piece_index = short_piece_to_index_dict[other_piece]
                if on_straight and (piece_index == 4 or piece_index == 5):
                    return [m for m in move_array if self.filter_straight_move(king, i, j, m)]
                if on_diagonal and (piece_index == 3 or piece_index == 5):
                    return [m for m in move_array if self.filter_diagonal_move(king, i, j, m)]
                return move_array
            i -= i_step
            j -= j_step
        return move_array

    @staticmethod
    def filter_straight_move(king, other_piece_i, other_piece_j, move):
        lower_bound_i, lower_bound_j = min(king.i, other_piece_i), min(king.j, other_piece_j)
        upper_bound_i, upper_bound_j = max(king.i, other_piece_i), max(king.j, other_piece_j)
        return lower_bound_i <= move[0][0] <= upper_bound_i and lower_bound_j <= move[0][1] <= upper_bound_j

    @staticmethod
    def filter_diagonal_move(king, other_piece_i, other_piece_j, move):
        i, j = move[0][0], move[0][1]
        return abs(king.i - i) == abs(king.j - j) and abs(other_piece_i - i) == abs(other_piece_j - j)
