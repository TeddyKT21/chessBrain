from move_generation.board_util import update_castle_state
from move_generation.pieces.piece import Piece
from move_generation.short_board import board_size, piece_dict


class Rook(Piece):
    attack_square_dict = {}
    white_move_dict = {}
    black_move_dict = {}
    for i in range(board_size):
        for j in range(board_size):
            possible_locations_arr = []
            for k in range(board_size):
                for m in range(board_size):
                    if (k == i) != (j == m):
                        possible_locations_arr += [k, m]
            attack_square_dict[i + 10 * j] = possible_locations_arr

    Piece.generate_move_dicts(attack_square_dict, white_move_dict, black_move_dict, 'rook')

    white_castle_king_side = (
        (0, 2, piece_dict['rook']['white']), (0, 0, 0), (0, 1, piece_dict['king']['white']), (0, 3, 0))
    white_castle_queen_side = (
        (0, 4, piece_dict['rook']['white']), (0, 7, 0), (0, 5, piece_dict['king']['white']), (0, 3, 0))

    black_castle_king_side = (
        (7, 2, piece_dict['rook']['black']), (7, 0, 0), (7, 1, piece_dict['king']['black']), (7, 3, 0))
    black_castle_queen_side = (
        (7, 4, piece_dict['rook']['black']), (7, 7, 0), (7, 5, piece_dict['king']['black']), (7, 3, 0))

    def __init__(self, i, j, short_board, game_engine):
        super().__init__(i, j, short_board, game_engine)
        self.first_move = None
        self.move_dict = self.white_move_dict if self.color_bit == 0 else self.black_move_dict
        self.castle = None
        self.castle_squares = None
        self.castle_scale = None
        if self.color_bit == 0 and self.j == 0 and self.i == 0:
            self.castle = Rook.white_castle_king_side
            self.castle_squares = [[0, 1], [0, 2]]
            self.castle_scale = 2
        if self.color_bit == 1 and self.j == 0 and self.i == 7:
            self.castle = Rook.black_castle_king_side
            self.castle_squares = [[7, 1], [7, 2]]
            self.castle_scale = 8
        if self.color_bit == 0 and self.j == board_size - 1 and self.i == 0:
            self.castle = Rook.white_castle_queen_side
            self.castle_squares = [[0, 4], [0, 5], [0, 6]]
            self.castle_scale = 4
        if self.color_bit == 1 and self.j == board_size - 1 and self.i == 7:
            self.castle = Rook.black_castle_queen_side
            self.castle_squares = [[7, 4], [7, 5], [7, 6]]
            self.castle_scale = 16

    def consider_board(self, moves, empty_move_array=None, empty_attack_map=None):
        min_i, max_i, min_j, max_j = 0, board_size - 1, 0, board_size - 1
        for i in range(self.i - 1, 0, -1):
            if self.short_board.short_array[i, self.j] != 0:
                min_i = i
                break
        for j in range(self.j - 1, 0, -1):
            if self.short_board.short_array[self.i, j] != 0:
                min_j = j
                break
        for i in range(self.i + 1, board_size - 1):
            if self.short_board.short_array[i, self.j] != 0:
                max_i = i
                break
        for j in range(self.j + 1, board_size - 1):
            if self.short_board.short_array[self.i, j] != 0:
                max_j = j
                break
        # for m in moves:
        #     if min_i <= m[0][0] <= max_i and min_j <= m[0][1] <= max_j and (m[0][0] == self.i or m[0][1] == self.j):
        #         empty_attack_map.append(m)
        #         if color_bit_dict[self.short_board.short_array[m[0][0], m[0][1]]] != self.color_bit:
        #             empty_move_array.append(m)
        return [m for m in moves if min_i <= m[0][0] <= max_i and
                min_j <= m[0][1] <= max_j and
                (m[0][0] == self.i or m[0][1] == self.j)]

    def get_moves(self):
        legal_moves = [*super().get_moves()]
        if not self.first_move and \
                self.castle and \
                self.piece_index == 4 and \
                self.i == self.castle[1][0] and \
                self.j == self.castle[1][1]:
            king = self.game_engine.white_king if self.color_bit == 0 else self.game_engine.black_king
            if not king.first_move:
                free_back_row = True
                for square in self.castle_squares:
                    if self.short_board.short_array[square[0], square[1]] != 0:
                        free_back_row = False
                if free_back_row:
                    safe_for_king = True
                    for k in range(2):
                        square = self.castle_squares[k]
                        safe_for_king = safe_for_king and self.check_if_attacked(square)
                    if safe_for_king:
                        legal_moves.append(self.castle)
        return legal_moves

    def move_does_influence(self, move):
        for change in move:
            for m in self.attack_map_moves:
                if change[0] == m[0][0] and change[1] == m[0][1]:
                    return True
        return False

    def was_moved(self, move):
        answer = super().was_moved(move) or move is self.castle
        if answer and not self.first_move:
            self.first_move = len(self.game_engine.previous_moves_stack)
            if self.castle_scale:
                update_castle_state(self.short_board, self.castle_scale)
        return answer

    def check_if_attacked(self, square):
        enemies = self.game_engine.white_pieces if self.color_bit == 1 else self.game_engine.black_pieces
        for enemy in enemies:
            if [m for m in enemy.attack_map_moves if m[0][0] == square[0] and m[0][1] == square[1]]:
                return False
        return True

    def revert_move(self, reverted_last_move):
        if self.first_move and len(self.game_engine.previous_moves_stack) < self.first_move:
            self.first_move = None
        if len(reverted_last_move) != 4:
            self.revert_update(reverted_last_move)
        elif reverted_last_move[3][0] == self.i and reverted_last_move[3][1] == self.j:
            self.i = reverted_last_move[2][0]
            self.j = reverted_last_move[2][1]
            self.attack_map_moves = self.consider_board(self.move_dict[self.i + self.j * 10])
            self.filter_if_blocked()
        else:
            self.revert_update(reverted_last_move)

    def revert_update(self, reverted_last_move):
        was_moved = super().was_moved(reverted_last_move)
        if reverted_last_move is None or was_moved or self.move_does_influence(reverted_last_move):
            if reverted_last_move is not None and was_moved:
                self.i = reverted_last_move[0][0]
                self.j = reverted_last_move[0][1]
            self.attack_map_moves = self.consider_board(self.move_dict[self.i + self.j * 10])
            self.filter_if_blocked()

