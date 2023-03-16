from abc import ABC, abstractmethod

import converters
from converters import byte_piece_to_index_dict, color_bit_dict, can_castle_king_side, can_castle_queen_side
from move_generator.board_util import remove_if_out_of_range


def create_piece(i, j, byte_board):
    byte = byte_board.byte_array[i, j]
    if byte % 2 == 0:
        return
    index = byte_piece_to_index_dict[byte]
    match index:
        case 1:
            return Pawn(i, j, byte_board)
        case 2:
            return Knight(i, j, byte_board)
        case 3:
            return Bishop(i, j, byte_board)
        case 4:
            return Rook(i, j, byte_board)
        case 5:
            return Queen(i, j, byte_board)
        case 6:
            return King(i, j, byte_board)
        case _:
            raise Exception('invalid byte piece !')
    return


class Piece(ABC):
    def __init__(self, i, j, byte_board):
        self.move_array = []
        self.i = i
        self.j = j
        self.byte_board = byte_board
        self.color_bit = color_bit_dict[byte_board.byte_array[i, j]]
        self.board_size = byte_board.byte_array.shape[0]
        self.piece_index = byte_piece_to_index_dict[byte_board.byte_array[i, j]]
        self.legal_move_array = []
        self.was_updated = False

    def generate_piece_moves(self, move=None):
        self.was_updated = False
        if move is None or self.was_moved(move) or self.move_does_influence(move):
            self.was_updated = True
            if move is not None and self.was_moved(move):
                self.i = move[0][0]
                self.j = move[0][1]
            possible_locations = self.generate_move_locations(move)
            self._convert_locations_to_moves(possible_locations)
        return

    def _convert_locations_to_moves(self, possible_locations):
        i = self.i
        j = self.j
        byte_piece = self.byte_board.byte_array[i, j]
        self.move_array = []
        for k in range(0, len(possible_locations), 2):
            move = ((possible_locations[k], possible_locations[k + 1],
                     byte_piece), (i, j, 0))
            self.move_array.append(move)

        return

    @abstractmethod
    def generate_move_locations(self, move=None):
        pass

    @abstractmethod
    def move_does_influence(self, move):
        pass

    def was_moved(self, move):
        return move[1][0] == self.i and move[1][1] == self.j

    def __str__(self):
        color = 'white' if self.color_bit == 0 else 'black'
        return f"{color} {str(type(self)).split('.')[2].split(''''>''')[0]} at {self.i, self.j} "


# ----------------------------------------------------------------------------------------------------------------------------------------------


class King(Piece):

    def generate_move_locations(self, move=None):
        i = self.i
        j = self.j
        possible_locations_arr = [i + 1, j + 1,
                                  i, j + 1,
                                  i - 1, j + 1,
                                  i + 1, j,
                                  i - 1, j,
                                  i + 1, j - 1,
                                  i, j - 1,
                                  i - 1, j - 1]
        remove_if_out_of_range(possible_locations_arr)
        return possible_locations_arr

    def move_does_influence(self, move):
        for k in range(len(move)):
            change = move[k]
            if abs(change[0] - self.i) <= 1 and abs(change[1] - self.j) <= 1:
                return True
        return False

    def was_moved(self, move):
        return (move[1][0] == self.i and move[1][1] == self.j) or \
               (len(move) == 4 and color_bit_dict[move[1][2]] == self.color_bit)

    def generate_piece_moves(self, move=None):
        self.was_updated = False
        if move is None or self.was_moved(move) or self.move_does_influence(move):
            self.was_updated = True
            if move is not None and self.was_moved(move):
                if len(move) == 2:
                    self.i = move[0][0]
                    self.j = move[0][1]
                else:
                    self.i = move[1][0]
                    self.j = move[1][1]
            possible_locations = self.generate_move_locations(move)
            self._convert_locations_to_moves(possible_locations)
        return


# ----------------------------------------------------------------------------------------------------------------------------------------------
class Rook(Piece):

    def __init__(self, i, j, byte_board):
        super().__init__(i, j, byte_board)
        self.did_move = False

    def generate_move_locations(self, move=None):
        possible_locations = self.generate_straight_locations()
        return possible_locations

    def generate_straight_locations(self):
        possible_locations = []
        i = self.i
        j = self.j

        d = i + 1
        while d < 8:
            possible_locations.append(d)
            possible_locations.append(j)
            if self.byte_board.byte_array[d, j] != 0:
                break
            d += 1

        d = i - 1
        while d >= 0:
            possible_locations.append(d)
            possible_locations.append(j)
            if self.byte_board.byte_array[d, j] != 0:
                break
            d -= 1

        d = j + 1
        while d < 8:
            possible_locations.append(i)
            possible_locations.append(d)
            if self.byte_board.byte_array[i, d] != 0:
                break
            d += 1

        d = j - 1
        while d >= 0:
            possible_locations.append(i)
            possible_locations.append(d)
            if self.byte_board.byte_array[i, d] != 0:
                break
            d -= 1

        return possible_locations

    def move_does_influence(self, move):
        for change in move:
            for m in self.move_array:
                if change[0] == m[0][0] and change[1] == m[0][1]:
                    return True
        return False

    def _convert_locations_to_moves(self, possible_locations):
        super()._convert_locations_to_moves(possible_locations)
        if self.did_move:
            return
        castle_location = self.get_castle()
        if castle_location is not None:
            back_row = castle_location[0]
            self_byte = self.byte_board.byte_array[self.i, self.j]
            king_byte = self.byte_board.byte_array[back_row, 3]
            if castle_location[1] == 0:
                self.move_array.append(((back_row, 0, 0),
                                        (back_row, 1, king_byte),
                                        (back_row, 2, self_byte),
                                        (back_row, 3, 0)))
            else:
                self.move_array.append(((back_row, 7, 0),
                                        (back_row, 5, king_byte),
                                        (back_row, 4, self_byte),
                                        (back_row, 3, 0)))
        return

    def get_castle(self):
        state = self.byte_board.state
        back_row = 0 if self.color_bit == 0 else 7
        if self.j == 0 and can_castle_king_side(state, self.color_bit):
            f_square = self.byte_board.byte_array[back_row, 2]
            g_square = self.byte_board.byte_array[back_row, 1]
            if f_square == 0 and g_square == 0:
                return [back_row, 0]

        if self.j == 7 and can_castle_queen_side(state, self.color_bit):
            d_square = self.byte_board.byte_array[back_row, 4]
            c_square = self.byte_board.byte_array[back_row, 5]
            b_square = self.byte_board.byte_array[back_row, 6]
            if d_square == 0 and c_square == 0 and b_square == 0:
                return [back_row, 7]
        return None

    def was_moved(self, move):
        answer = super().was_moved(move) or move in self.move_array
        if answer:
            self.did_move = True
        return answer

    def generate_piece_moves(self, move=None):
        self.was_updated = False
        if move is None or self.was_moved(move) or self.move_does_influence(move):
            self.was_updated = True
            if move is not None and self.was_moved(move):
                if len(move) == 2:
                    self.i = move[0][0]
                    self.j = move[0][1]
                else:
                    self.i = move[2][0]
                    self.j = move[2][1]
            possible_locations = self.generate_move_locations(move)
            self._convert_locations_to_moves(possible_locations)
        return


# ----------------------------------------------------------------------------------------------------------------------------------------------


class Bishop(Piece):

    def generate_move_locations(self, move=None):
        return self.generate_diagonal_locations()

    def generate_diagonal_locations(self):
        possible_locations = []
        i = self.i
        j = self.j
        d = 1
        while i + d < 8 and j + d < 8:
            possible_locations.append(i + d)
            possible_locations.append(j + d)
            if self.byte_board.byte_array[i + d, j + d] != 0:
                break
            d += 1

        d = 1
        while i - d >= 0 and j + d < 8:
            possible_locations.append(i - d)
            possible_locations.append(j + d)
            if self.byte_board.byte_array[i - d, j + d] != 0:
                break
            d += 1

        d = 1
        while i + d < 8 and j - d >= 0:
            possible_locations.append(i + d)
            possible_locations.append(j - d)
            if self.byte_board.byte_array[i + d, j - d] != 0:
                break
            d += 1

        d = 1
        while i - d >= 0 and j - d >= 0:
            possible_locations.append(i - d)
            possible_locations.append(j - d)
            if self.byte_board.byte_array[i - d, j - d] != 0:
                break
            d += 1
        return possible_locations

    def move_does_influence(self, move):
        for change in move:
            for m in self.move_array:
                if change[0] == m[0][0] and change[1] == m[0][1]:
                    return True
        return False


# ----------------------------------------------------------------------------------------------------------------------------------------------
class Queen(Rook, Bishop):

    def generate_move_locations(self, move=None):
        return self.generate_straight_locations() + self.generate_diagonal_locations()

    def move_does_influence(self, move):
        for change in move:
            for m in self.move_array:
                if change[0] == m[0][0] and change[1] == m[0][1]:
                    return True
        return False


# ----------------------------------------------------------------------------------------------------------------------------------------------


class Knight(Piece):

    def generate_move_locations(self, move=None):
        i = self.i
        j = self.j
        possible_moves = [i + 1, j + 2,
                          i + 1, j - 2,
                          i + 2, j - 1,
                          i + 2, j + 1,
                          i - 1, j + 2,
                          i - 1, j - 2,
                          i - 2, j + 1,
                          i - 2, j - 1]
        remove_if_out_of_range(possible_moves)
        return possible_moves

    def move_does_influence(self, move):
        for k in range(len(move)):
            change = move[k]
            if abs(self.i - change[0]) == 2 and abs(self.j - change[1]) == 1 \
                    or abs(self.i - change[0]) == 1 and abs(self.j - change[1]) == 2:
                return True
        return False


# ----------------------------------------------------------------------------------------------------------------------------------------------
class Pawn(Piece):

    def __init__(self, i, j, byte_board):
        super().__init__(i, j, byte_board)
        self.en_passant = None

    def generate_move_locations(self, move=None):
        i = self.i
        j = self.j
        possible_locations = []
        direction = 1 if self.color_bit == 0 else -1
        limit = 7 if direction == 1 else 0

        if i != limit and self.byte_board.byte_array[i + direction, j] == 0:
            possible_locations += [i + direction, j]
            starting_row = 1 if direction == 1 else 6  # double step at start
            if i == starting_row and self.byte_board.byte_array[i + 2 * direction, j] == 0:
                possible_locations += [i + 2 * direction, j]

        if i > 0 and direction == -1 or i < 7 and direction == 1:  # checking if there is a piece to take diagonally
            if j < 7:
                other_piece = self.byte_board.byte_array[i + direction, j + 1]
                if other_piece != 0 and color_bit_dict[other_piece] != self.color_bit:
                    possible_locations += [i + direction, j + 1]
            if j > 0:
                other_piece = self.byte_board.byte_array[i + direction, j - 1]
                if other_piece != 0 and color_bit_dict[other_piece] != self.color_bit:
                    possible_locations += [i + direction, j - 1]

        if self.check_en_passant(move):
            colum = move[0][1]

            if abs(j - colum) == 1:
                self.en_passant = [i + direction, colum]
                # print('en passant possible')

        return possible_locations

    def move_does_influence(self, move):
        if self.en_passant:
            self.reset_en_passant()
            return True
        self.reset_en_passant()
        i = self.i
        j = self.j
        direction = 1 if self.color_bit == 0 else -1
        for change in move:
            if change[0] == self.i + direction and change[1] == self.j:
                return True
            if change[0] == i + direction and abs(change[1] - j) == 1:
                return True
            if self.check_en_passant(move):
                return True

            starting_row = 1 if direction == 1 else 6
            on_starting_row = i == starting_row
            if on_starting_row and abs(change[0] - i) <= 2 and change[1] == j:
                return True
            if self.en_passant is not None and not self.check_en_passant(move):
                self.en_passant = None
                return True
        return False

    def reset_en_passant(self):
        self.en_passant = None
        self.move_array = [move for move in self.move_array if len(move) < 3]

    def check_en_passant(self, move):
        direction = 1 if self.color_bit == 0 else -1
        en_passant_row = 4 if direction == 1 else 3
        if self.i == en_passant_row and move is not None:
            if byte_piece_to_index_dict[move[0][2]] == 1 and color_bit_dict[move[0][2]] != self.color_bit:
                if abs(move[0][0] - move[1][0]) == 2 and abs(move[0][1] - self.j) == 1:
                    return True
        return False

    def _convert_locations_to_moves(self, possible_locations):
        super()._convert_locations_to_moves(possible_locations)
        last_row = 0 if self.color_bit == 1 else 7
        promotion_moves = [m for m in self.move_array if m[0][0] == last_row]
        if promotion_moves:
            self.move_array = [m for m in self.move_array if m not in promotion_moves]
            possible_promotions = []
            if self.color_bit == 1:
                for m in promotion_moves:
                    i = m[0][0]
                    j = m[0][1]

                    possible_promotions += [((i, j, converters.black_queen_value), m[1]),
                                            ((i, j, converters.black_rook_value), m[1]),
                                            ((i, j, converters.black_bishop_value), m[1]),
                                            ((i, j, converters.black_knight_value), m[1])]
            else:
                for m in promotion_moves:
                    i = m[0][0]
                    j = m[0][1]

                    possible_promotions += [((i, j, converters.white_queen_value), m[1]),
                                            ((i, j, converters.white_rook_value), m[1]),
                                            ((i, j, converters.white_bishop_value), m[1]),
                                            ((i, j, converters.white_knight_value), m[1])]
            self.move_array += possible_promotions

        if self.en_passant is not None:
            byte_piece = self.byte_board.byte_array[self.i, self.j]
            move = ((self.en_passant[0], self.en_passant[1], byte_piece),
                    (self.i, self.j, 0),
                    (self.i, self.en_passant[1], 0))
            self.move_array.append(move)

        return

# ----------------------------------------------------------------------------------------------------------------------------------------------
