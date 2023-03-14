from converters import byte_board_to_binary_number, binary_to_byte_board, update_state, move_turn, \
    byte_piece_to_index_dict, \
    color_bit_dict, get_turn
import move_generator.pieces as pieces
from move_generator.board_util import get_attacking_squares


class LegalPosGenerator:

    def __init__(self):
        self.piece_array = []
        self.byte_board = None
        self.move_array = []
        self.positions_array = []
        self.white_king = None
        self.black_king = None

    def generate_pieces(self):
        board_size = self.byte_board.byte_array.shape[0]
        for i in range(board_size):
            for j in range(board_size):
                byte = self.byte_board.byte_array[i, j]
                if byte % 2 == 0 or byte < 4:
                    continue
                piece = pieces.create_piece(i, j, self.byte_board)
                self.piece_array.append(piece)
                if byte_piece_to_index_dict[byte] == 6:
                    if color_bit_dict[byte] == 1:
                        self.black_king = piece
                    else:
                        self.white_king = piece

        if self.white_king is None or self.black_king is None:
            raise Exception('missing Kings on the board !')
        return

    def generate_legal_positions(self, binary_pos):
        new_byte_board = binary_to_byte_board(binary_pos)
        if self.byte_board is None:
            self.byte_board = new_byte_board
            self.generate_pieces()
            self.get_moves()
        else:
            self.byte_board.byte_array = new_byte_board.byte_array
            self.byte_board.state = new_byte_board.state
            played_move = self.move_array[self.positions_array.index(binary_pos)]
            self.get_moves(played_move)
        return self.move_array

    def make_move(self, move_index):
        played_move = self.move_array[move_index]
        move_turn(self.byte_board)
        for change in played_move:
            i = change[0]
            j = change[1]
            piece = change[2]
            self.byte_board.byte_array[i, j] = piece
        update_state(self.byte_board)
        self.get_moves(played_move)
        return self.move_array

    def get_moves(self, played_move=None):
        if played_move is not None and len(played_move) != 4:
            i = played_move[0][0]
            j = played_move[0][1]
            if len(played_move) == 3:
                i = played_move[2][0]
                j = played_move[2][1]
            self.remove_piece_if_exists(i, j)
        for piece in self.piece_array:
            piece.generate_piece_moves(played_move)
        check_squares = self.get_check_squares()
        # if check_squares is not None:
        #     print("check !",played_move ,'\n')
        turn = get_turn(self.byte_board.state)
        relevant_pieces = [p for p in self.piece_array if p.color_bit == turn]
        self.move_array = sum(
            map(lambda p: self.filter_piece_moves(p, check_squares), relevant_pieces), [])
        self.check_promotions()
        return

    def check_promotions(self):
        # promotion_moves = list(
        #     filter((lambda move: (move[0][0] == 0 or move[0][0] == 7) and get_piece_index(move[0][2]) == 1),
        #            self.move_array))
        # if not promotion_moves:
        #     return
        # for promotion_move in promotion_moves:
        #     self.move_array.remove(promotion_move)
        #     promotion_options =
        pass

    def get_check_squares(self):
        turn = get_turn(self.byte_board.state)
        king = self.black_king if turn == 1 else self.white_king
        enemy_color_bit = abs(king.color_bit - 1)
        # self.test_self_check()
        if not self.is_square_attacked([king.i, king.j], enemy_color_bit):
            return None
        return get_attacking_squares(self.byte_board, king.i, king.j, enemy_color_bit)

    def test_self_check(self):
        turn = get_turn(self.byte_board.state)
        king = self.black_king if turn == 0 else self.white_king
        enemy_color_bit = abs(king.color_bit - 1)
        check_squares = get_attacking_squares(self.byte_board, king.i, king.j, enemy_color_bit)
        if check_squares is not None:
            print('self check state:!!!!!!!!!!!!!!!!!', '\n', self.byte_board,
                  check_squares)
            return

    def filter_piece_moves(self, piece, check_squares):
        turn = get_turn(self.byte_board.state)
        if turn != piece.color_bit:
            return []
        king = self.black_king if turn == 1 else self.white_king
        if piece == king:
            return self.filter_king_moves(king)
        possible_moves = self.filter_pins(piece, king)
        possible_moves = self.filter_if_blocked(piece, possible_moves)
        if piece.piece_index == 4:
            possible_moves = self.filter_rook_moves(piece, possible_moves)
        if check_squares is None or len(possible_moves) == 0:
            return possible_moves
        if check_squares[0][0] > 1:
            return []
        legal_moves = []
        for move in possible_moves:
            if len(move) == 3:  # en passant and the cause of check is a pawn
                return [move]
            for k in range(0, len(check_squares[1]), 2):
                i = check_squares[1][k]
                j = check_squares[1][k + 1]
                if move[0][0] == i and move[0][1] == j:
                    legal_moves.append(move)
        return legal_moves

    def filter_pins(self, piece, king):
        if piece == king:
            return king.move_array
        delta_i, delta_j = king.i - piece.i, king.j - piece.j
        on_diagonal = abs(delta_i) == abs(delta_j)
        on_straight = delta_i == 0 or delta_j == 0
        if not on_diagonal and not on_straight:
            return piece.move_array
        distance = max(abs(delta_i), abs(delta_j))
        i_step, j_step = delta_i // distance, delta_j // distance
        i, j = piece.i, piece.j
        for k in range(1, distance):
            if self.byte_board.byte_array[i + k * i_step, j + k * j_step] != 0:
                return piece.move_array

        i -= i_step
        j -= j_step
        while 0 <= i <= 7 and 0 <= j <= 7:
            other_piece = self.byte_board.byte_array[i, j]
            if other_piece != 0:
                if color_bit_dict[other_piece] == king.color_bit:
                    return piece.move_array
                piece_index = byte_piece_to_index_dict[other_piece]
                if on_straight and (piece_index == 4 or piece_index == 5):
                    # print('pinned piece !', king, piece, '\n', self.byte_board)
                    return list(filter(lambda move: self.filter_straight_move(king, i, j, move), piece.move_array))
                if on_diagonal and (piece_index == 3 or piece_index == 5):
                    # print('pinned piece !', king, piece, '\n', self.byte_board)
                    return list(filter(lambda move: self.filter_diagonal_move(king, i, j, move), piece.move_array))
                return piece.move_array
            i -= i_step
            j -= j_step
        return piece.move_array

    def filter_if_blocked(self, piece, possible_moves):
        blocked_moves = []
        for move in possible_moves:
            if len(move) > 2:
                continue
            blocking_piece = self.byte_board.byte_array[move[0][0], move[0][1]]
            if blocking_piece != 0 and color_bit_dict[blocking_piece] == piece.color_bit:
                blocked_moves.append(move)
        possible_moves = [m for m in possible_moves if m not in blocked_moves]
        return possible_moves

    def filter_king_moves(self, king):
        enemy_color_bit = abs(king.color_bit - 1)
        enemy_pieces = list(filter(lambda p: p.color_bit == enemy_color_bit, self.piece_array))
        king_possible_moves = self.filter_if_blocked(king, king.move_array)
        enemy_pawn_direction = 1 if enemy_color_bit == 0 else -1
        for enemy in enemy_pieces:
            if not king_possible_moves:
                break
            relevant_enemy_moves = [m for m in enemy.move_array if
                                    abs(king.i - m[0][0]) <= 1 and
                                    abs(king.j - m[0][1]) <= 1 and
                                    len(m) == 2]
            match enemy.piece_index:
                case 1:
                    king_possible_moves = [m for m in king_possible_moves if not (
                            m[0][0] == enemy.i + enemy_pawn_direction and
                            abs(m[0][1] - enemy.j) == 1)]
                    continue
                case 3:
                    if abs(king.i - enemy.i) == abs(king.j - enemy.j):
                        king_possible_moves = [m for m in king_possible_moves if
                                               (m[0][0] == enemy.i and m[0][1] == enemy.j) or not
                                               abs(m[0][0] - enemy.i) == abs(m[0][1] - enemy.j)]
                        continue
                case 4:
                    if king.i == enemy.i or king.j == enemy.j:
                        king_possible_moves = [m for m in king_possible_moves if
                                               (m[0][0] == enemy.i and m[0][1] == enemy.j) or not
                                               (m[0][0] == enemy.i or m[0][1] == enemy.j)]
                        continue
                case 5:
                    if king.i == enemy.i or king.j == enemy.j:
                        king_possible_moves = [m for m in king_possible_moves if
                                               (m[0][0] == enemy.i and m[0][1] == enemy.j) or not
                                               (m[0][0] == enemy.i or m[0][1] == enemy.j)]
                    elif abs(king.i - enemy.i) == abs(king.j - enemy.j):
                        king_possible_moves = [m for m in king_possible_moves if
                                               (m[0][0] == enemy.i and m[0][1] == enemy.j) or not
                                               abs(m[0][0] - enemy.i) == abs(m[0][1] - enemy.j)]

            if enemy.piece_index != 1:
                for enemy_move in relevant_enemy_moves:
                    king_possible_moves = [m for m in king_possible_moves if not
                    (m[0][0] == enemy_move[0][0] and m[0][1] == enemy_move[0][1])]

        return king_possible_moves

    def filter_rook_moves(self, rook, moves):
        if rook.did_move or not [m for m in moves if len(m) == 4]:
            return moves
        castle = [m for m in moves if len(m) == 4][0]
        enemy_color_bit = abs(rook.color_bit - 1)
        back_row = rook.i
        important_squares = [[back_row, 5], [back_row, 4]] if rook.j == 7 else [[back_row, 1], [back_row, 2]]
        can_castle = not self.is_square_attacked(important_squares[0], enemy_color_bit) and \
                     not self.is_square_attacked(important_squares[1], enemy_color_bit)
        if not can_castle:
            moves.remove(castle)
        return moves

    def is_square_attacked(self, square, enemy_color_bit):
        enemy_pieces = list(filter(lambda p: p.color_bit == enemy_color_bit, self.piece_array))
        i = square[0]
        j = square[1]
        enemy_pawn_direction = 1 if enemy_color_bit == 0 else -1
        for enemy in enemy_pieces:
            if enemy.piece_index == 1:
                if i == enemy.i + enemy_pawn_direction and abs(enemy.j - j) == 1:
                    return True
            else:
                relevant_enemy_moves = [m for m in enemy.move_array if m[0][0] == i and m[0][1] == j and len(m) == 2]
                if relevant_enemy_moves:
                    return True

        return False

    @staticmethod
    def filter_straight_move(king, other_piece_i, other_piece_j, move):
        lower_bound_i, lower_bound_j = min(king.i, other_piece_i), min(king.j, other_piece_j)
        upper_bound_i, upper_bound_j = max(king.i, other_piece_i), max(king.j, other_piece_j)
        return lower_bound_i <= move[0][0] <= upper_bound_i and lower_bound_j <= move[0][1] <= upper_bound_j

    @staticmethod
    def filter_diagonal_move(king, other_piece_i, other_piece_j, move):
        i, j = move[0][0], move[0][1]
        return abs(king.i - i) == abs(king.j - j) and abs(other_piece_i - i) == abs(other_piece_j - j)

    def move_to_bin_pos(self, move):
        saved_state = self.byte_board.state
        revert_changes = list(map(lambda t: (t[0], t[1], self.byte_board.byte_array[t[0], t[1]]), move))
        move_turn(self.byte_board)
        for change in move:
            i = change[0]
            j = change[1]
            piece = change[2]
            self.byte_board.byte_array[i, j] = piece
        update_state(self.byte_board)
        binary_pos = byte_board_to_binary_number(self.byte_board)

        self.byte_board.state = saved_state
        for revert in revert_changes:
            i = revert[0]
            j = revert[1]
            piece = revert[2]
            self.byte_board.byte_array[i, j] = piece
        return binary_pos

    def remove_piece_if_exists(self, i, j):
        for piece in self.piece_array:
            if piece.i == i and piece.j == j:
                if piece == self.white_king or piece == self.black_king:
                    print('king was eaten !!!!!!!!!!!!!!!!!')
                    print(self.byte_board)
                    for p in self.piece_array:
                        print(p)
                    print(self.black_king)
                    print(self.white_king)
                    # raise Exception('king cannot be eaten !')
                self.piece_array.remove(piece)
                # print('removed piece:', piece)
                break
        return
