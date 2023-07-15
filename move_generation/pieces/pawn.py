from move_generation.board_util import set_en_passant_state
from move_generation.converters import short_piece_to_index_dict, color_bit_dict
from move_generation.pieces.piece import Piece
from move_generation.short_board import board_size, piece_dict


def build_locations_arr(i, j, color_bit):
    first_row = 1 if color_bit == 0 else 6
    last_row = board_size - 1 if color_bit == 0 else 0
    direction = 1 if color_bit == 0 else - 1
    if i == last_row:
        return []
    result = [i + direction, j]
    if i == first_row:
        result += [i + 2 * direction, j]
    return result


white_promotion_options = [piece_dict['knight']['white'], piece_dict['bishop']['white'],
                           piece_dict['rook']['white'], piece_dict['queen']['white']]
black_promotion_options = [piece_dict['knight']['black'], piece_dict['bishop']['black'],
                           piece_dict['rook']['black'], piece_dict['queen']['black']]


def add_promotions(i, j, k, m, color_bit):
    promotion_options = white_promotion_options if color_bit == 0 else black_promotion_options
    possible_promotion_moves = []
    for option in promotion_options:
        possible_promotion_moves.append(((k, m, option), (i, j, 0)))
    return possible_promotion_moves


def convert_location_to_move(i, j, move_squares, move_dict, color_bit):
    last_row = board_size - 1 if color_bit == 0 else 0
    value = piece_dict['pawn']['white'] if color_bit == 0 else piece_dict['pawn']['black']
    possible_moves = []
    for k in range(0, len(move_squares), 2):
        if move_squares[k] != last_row:
            possible_moves.append(((move_squares[k], move_squares[k + 1], value), (i, j, 0)))
        else:
            possible_moves += add_promotions(i, j, move_squares[k], move_squares[k + 1], color_bit)
    move_dict[i + j * 10] = possible_moves


def build_attack_map_dict(attack_map_dict, direction, i, j, last_row, value):
    move_array = []
    not_last_row = i < last_row if direction == 1 else i > last_row
    if not_last_row:
        if j > 0:
            move_array.append(((i + direction, j - 1, value), (i, j, 0)))
        if j < board_size - 1:
            move_array.append(((i + direction, j + 1, value), (i, j, 0)))
    attack_map_dict[i + 10 * j] = move_array


class Pawn(Piece):
    attack_square_dict = {'white': {}, 'black': {}}
    white_move_dict = {}
    black_move_dict = {}
    white_attack_map_dict = {}
    black_attack_map_dict = {}

    for i in range(board_size):
        for j in range(board_size):
            attack_square_dict['white'][i + 10 * j] = build_locations_arr(i, j, 0)
            attack_square_dict['black'][i + 10 * j] = build_locations_arr(i, j, 1)

    @staticmethod
    def generate_attack_map_dicts(white_attack_map_dict, black_attack_map_dict):
        for i in range(board_size):
            for j in range(board_size):
                build_attack_map_dict(white_attack_map_dict, 1, i, j, board_size - 1, piece_dict['pawn']['white'])
                build_attack_map_dict(black_attack_map_dict, -1, i, j, 0, piece_dict['pawn']['black'])

    @staticmethod
    def generate_move_dicts(attack_square_dict, white_move_dict, black_move_dict, name):
        for i in range(board_size):
            for j in range(board_size):
                convert_location_to_move(i, j, attack_square_dict['white'][i + 10 * j], white_move_dict, 0)
                convert_location_to_move(i, j, attack_square_dict['black'][i + 10 * j], black_move_dict, 1)

    generate_move_dicts(attack_square_dict, white_move_dict, black_move_dict, 'pawn')
    generate_attack_map_dicts(white_attack_map_dict, black_attack_map_dict)

    def __init__(self, i, j, short_board, game_engine):
        super().__init__(i, j, short_board, game_engine)
        self.move_dict = Pawn.white_move_dict if self.color_bit == 0 else Pawn.black_move_dict
        self.attack_map_dict = Pawn.white_attack_map_dict if self.color_bit == 0 else Pawn.black_attack_map_dict
        self.en_passant_row = 4 if self.color_bit == 0 else 3

    def update(self, move=None):
        if move is None or self.was_moved(move) or self.move_does_influence(move):
            if move is not None and self.was_moved(move):
                self.i = move[0][0]
                self.j = move[0][1]
            self.move_array = self.consider_board([*self.move_dict[self.i + self.j * 10]])
            self.attack_map_moves = self.attack_map_dict[self.i + self.j * 10]

    def revert_move(self, reverted_last_move):
        if len(reverted_last_move) != 3 or (reverted_last_move[2][0] != self.i or reverted_last_move[2][1] != self.j):
            self.update(reverted_last_move)
        else:
            self.i = reverted_last_move[1][0]
            self.j = reverted_last_move[1][1]
            self.move_array = self.consider_board([*self.move_dict[self.i + self.j * 10]])
            self.attack_map_moves = self.attack_map_dict[self.i + self.j * 10]

    def get_moves(self):
        legal_moves = [*self.move_array]
        if self.i == self.en_passant_row and self.game_engine.previous_moves_stack:
            played_move = self.game_engine.previous_moves_stack[-1]
            piece_value = played_move[0][2]
            if short_piece_to_index_dict[piece_value] == 1 and \
                    self.color_bit != color_bit_dict[piece_value] and \
                    abs(played_move[0][1] - self.j) == 1 and \
                    abs(played_move[0][0] - played_move[1][0]) == 2:
                self.add_en_passant_move(legal_moves, played_move)
        king = self.game_engine.white_king if self.color_bit == 0 else self.game_engine.black_king
        if king.i == self.i or king.j == self.j or abs(self.i - king.i) == abs(self.j - king.j):
            return self.filter_pins(king, legal_moves)
        return legal_moves

    def add_en_passant_move(self, legal_moves, played_move):
        direction = 1 if self.color_bit == 0 else -1
        color = 'white' if self.color_bit == 0 else 'black'
        en_passant_move = ((self.i + direction, played_move[0][1], piece_dict['pawn'][color]),
                           (self.i, self.j, 0),
                           (self.i, played_move[0][1], 0))
        legal_moves.append(en_passant_move)
        set_en_passant_state(self.short_board, played_move[0][1])

    def consider_board(self, moves, empty_move_array=None, empty_attack_map=None):
        i, j, color_bit = self.i, self.j, self.color_bit
        direction = 1 if color_bit == 0 else - 1
        last_row = board_size - 1 if color_bit == 0 else 0
        self.remove_if_piece_blocks(direction, moves)
        self.consider_pawn_captures(color_bit, direction, i, j, last_row, moves)
        return moves

    def consider_pawn_captures(self, color_bit, direction, i, j, last_row, moves):
        value = piece_dict['pawn']['white'] if color_bit == 0 else piece_dict['pawn']['black']
        self.consider_capture_side(color_bit, direction, i, j, last_row, moves, value, -1)
        self.consider_capture_side(color_bit, direction, i, j, last_row, moves, value, 1)

    def consider_capture_side(self, color_bit, vertical_direction, i, j, last_row, moves, value, horizontal_direction):
        not_edge = (j > 0) if horizontal_direction == -1 else (j < 7)
        if not_edge:
            other_piece = self.short_board.short_array[i + vertical_direction, j + horizontal_direction]
            if other_piece != 0 and color_bit_dict[other_piece] != color_bit:
                if i == (last_row - vertical_direction):
                    moves += add_promotions(i, j, i + vertical_direction, j + horizontal_direction, color_bit)
                else:
                    moves.append(((i + vertical_direction, j + horizontal_direction, value), (i, j, 0)))
        return moves

    def remove_if_piece_blocks(self, direction, moves):
        if self.short_board.short_array[self.i + direction, self.j] != 0:
            moves.clear()
        if len(moves) == 2 and self.short_board.short_array[self.i + 2 * direction, self.j] != 0:
            invalid_move = [m for m in moves if m[0][0] == self.i + 2 * direction]
            moves.remove(invalid_move[0])

    def move_does_influence(self, move):
        i = self.i
        j = self.j
        direction = 1 if self.color_bit == 0 else -1
        for change in move:
            if change[0] == i + direction and abs(change[1] - j) <= 1:
                return True
            starting_row = 1 if direction == 1 else 6
            if i == starting_row and change[0] == i + 2 * direction and change[1] == j:
                return True
        return False

    def was_moved(self, move):
        return move[1][0] == self.i and move[1][1] == self.j and \
               short_piece_to_index_dict[move[0][2]] == self.piece_index
