from move_generation.pieces.piece import Piece
from move_generation.board_util import remove_if_out_of_range, update_castle_state
from move_generation.short_board import board_size


class King(Piece):
    def consider_board(self, moves, empty_move_array=None, empty_attack_map=None):
        pass

    attack_square_dict = {}
    white_move_dict = {}
    black_move_dict = {}

    for i in range(board_size):
        for j in range(board_size):
            possible_locations_arr = [i + 1, j + 1,
                                      i, j + 1,
                                      i - 1, j + 1,
                                      i + 1, j,
                                      i - 1, j,
                                      i + 1, j - 1,
                                      i, j - 1,
                                      i - 1, j - 1]
            remove_if_out_of_range(possible_locations_arr)
            attack_square_dict[i + 10 * j] = possible_locations_arr

    Piece.generate_move_dicts(attack_square_dict, white_move_dict, black_move_dict, 'king')

    def __init__(self, i, j, short_board, game_engine):
        super().__init__(i, j, short_board, game_engine)
        self.move_dict = self.white_move_dict if self.color_bit == 0 else self.black_move_dict
        self.checking_pieces = 0
        self.check_moves = []
        self.checking_piece_squares = []
        self.first_move = None

    def move_does_influence(self, move):
        return True

    def update(self, move=None):
        if move is not None and self.was_moved(move):
            if len(move) == 4:
                self.i = move[2][0]
                self.j = move[2][1]
            else:
                self.i = move[0][0]
                self.j = move[0][1]
        self.generate_moves()

    def generate_moves(self):
        self.attack_map_moves = self.move_dict[self.i + self.j * 10]
        self.filter_if_blocked()
        enemies = self.game_engine.white_pieces if self.color_bit == 1 else self.game_engine.black_pieces
        self.find_checks(enemies)

    def revert_move(self, reverted_last_move):
        if self.first_move and len(self.game_engine.previous_moves_stack) < self.first_move:
            self.first_move = None
        if len(reverted_last_move) == 4 and reverted_last_move[1][0] == self.i and reverted_last_move[1][1] == self.j:
            self.i = reverted_last_move[0][0]
            self.j = reverted_last_move[0][1]
        else:
            if super().was_moved(reverted_last_move):
                self.i = reverted_last_move[0][0]
                self.j = reverted_last_move[0][1]
        self.generate_moves()

    def was_moved(self, move):
        answer = super().was_moved(move) or (len(move) == 4 and move[3][0] == self.i and move[3][1] == self.j)
        if answer and not self.first_move:
            self.first_move = len(self.game_engine.previous_moves_stack)
            if self.color_bit == 0:
                update_castle_state(self.short_board, 2)
                update_castle_state(self.short_board, 4)
            else:
                update_castle_state(self.short_board, 8)
                update_castle_state(self.short_board, 16)
        return answer

    def get_moves(self):
        if not self.move_array:
            return self.move_array
        enemies = self.game_engine.white_pieces if self.color_bit == 1 else self.game_engine.black_pieces
        legal_moves = self.move_array
        for enemy in enemies:
            if not legal_moves:
                break
            relevant_enemy_moves = [m for m in enemy.attack_map_moves if
                                    abs(self.i - m[0][0]) <= 1 and
                                    abs(self.j - m[0][1]) <= 1 and
                                    len(m) == 2]
            for enemy_move in relevant_enemy_moves:
                legal_moves = [m for m in legal_moves if not
                (m[0][0] == enemy_move[0][0] and
                 m[0][1] == enemy_move[0][1])]

        return legal_moves

    def find_checks(self, enemies):
        self.checking_pieces = 0
        self.check_moves.clear()
        self.checking_piece_squares.clear()
        for enemy in enemies:
            is_checking = [m for m in enemy.attack_map_moves if m[0][0] == self.i and m[0][1] == self.j]
            if is_checking:
                self.checking_pieces += 1
                self.checking_piece_squares = [enemy.i , enemy.j]
                min_i, max_i = min(self.i, enemy.i), max(self.i, enemy.i)
                min_j, max_j = min(self.j, enemy.j), max(self.j, enemy.j)
                if enemy.piece_index == 5:
                    if self.i != enemy.i and self.j != enemy.j:
                        self.check_moves = [m for m in enemy.attack_map_moves if
                                            min_i < m[0][0] < max_i and min_j < m[0][1] < max_j]
                    else:
                        self.check_moves = [m for m in enemy.attack_map_moves if
                                            min_i <= m[0][0] <= max_i and
                                            min_j <= m[0][1] <= max_j and
                                            (m[0][0] == self.i or m[0][1] == self.j)]
                else:
                    self.check_moves = [m for m in enemy.attack_map_moves if
                                        min_i <= m[0][0] <= max_i and min_j <= m[0][1] <= max_j]
                if 3 <= enemy.piece_index <= 5:
                    self.remove_move_backwards(enemy)

            # if self.checking_pieces and get_turn(self.short_board.state) != self.color_bit:
            #     raise Exception('king in self check state !!!')

    def remove_move_backwards(self, enemy):
        delta_j = self.j - enemy.j
        delta_i = self.i - enemy.i
        scale = max(abs(delta_i), abs(delta_j))
        step_i = delta_i // scale
        step_j = delta_j // scale
        self.move_array = [m for m in self.move_array if not
        (m[0][0] == self.i + step_i and m[0][1] == self.j + step_j)]