from move_generation.board_util import update_castle_state
from move_generation.pieces import pieces
from move_generation.converters import get_turn, move_turn, color_bit_dict
from move_generation.short_board import board_size, ShortBoard


class MoveGenerator:
    def __init__(self, short_board=None):
        self.piece_array = []
        self.white_pieces = []
        self.black_pieces = []
        self.white_removed_pieces = []
        self.black_removed_pieces = []
        self.white_promoted_pawns = []
        self.black_promoted_pawns = []
        self.white_king = None
        self.black_king = None
        self.short_board = None
        self.move_array = []
        self.previous_moves_stack = []
        self.revert_moves_stack = []
        self.state_stack = []
        self.short_board = short_board if short_board else ShortBoard()
        self.generate_pieces()
        self.update()

    def generate_pieces(self):
        board_size = self.short_board.short_array.shape[0]
        for i in range(board_size):
            for j in range(board_size):
                piece_number = self.short_board.short_array[i, j]
                if piece_number != 0:
                    piece = pieces.create_piece(i, j, self.short_board, self)
                    self.piece_array.append(piece)
                    side = self.white_pieces if piece.color_bit == 0 else self.black_pieces
                    side.append(piece)
                    if piece.piece_index == 6:
                        if piece.color_bit == 1:
                            self.black_king = piece
                        else:
                            self.white_king = piece

    def update(self):
        played_move = None
        if self.previous_moves_stack:
            played_move = self.previous_moves_stack[-1]
        turn = get_turn(self.short_board.state)
        king = self.white_king if turn == 0 else self.black_king
        turns_pieces = self.white_pieces if turn == 0 else self.black_pieces
        enemy_pieces = self.white_pieces if turn == 1 else self.black_pieces
        for piece in enemy_pieces:
            piece.update(played_move)
        for piece in turns_pieces:
            piece.update(played_move)
        self.update_move_array(king, turns_pieces)
        self.state_stack.append(self.short_board.state)
        return

    def update_move_array(self, king, turns_pieces):
        self.move_array = []
        for piece in turns_pieces:
            piece_moves = piece.get_moves()
            if king.checking_pieces:
                if king.checking_pieces > 1:
                    if piece != king:
                        piece_moves = []
                elif piece != king:
                    piece_moves = [m for m in piece_moves if
                                   [cm for cm in king.check_moves if cm[0][0] == m[0][0] and
                                    cm[0][1] == m[0][1]] or
                                   (m[0][0] == king.checking_piece_squares[0] and
                                    m[0][1] == king.checking_piece_squares[1]) or
                                   (len(m) == 3 and m[2][0] == king.checking_piece_squares[0] and
                                    m[2][1] == king.checking_piece_squares[1])]
            self.move_array += piece_moves

    def revert(self):
        last_move = self.previous_moves_stack.pop()
        reverted_last_move = self.revert_moves_stack.pop()
        previous_state = self.state_stack.pop()
        self.short_board.state = self.state_stack[-1]
        for change in reverted_last_move:
            i = change[0]
            j = change[1]
            piece = change[2]
            self.short_board.short_array[i, j] = piece

        turn = get_turn(self.short_board.state)
        turns_pieces = self.white_pieces if turn == 0 else self.black_pieces
        enemy_pieces = self.white_pieces if turn == 1 else self.black_pieces
        for piece in enemy_pieces:
            piece.revert_move(reverted_last_move)

        moved_piece = reverted_last_move[0][2] if len(reverted_last_move) == 2 else reverted_last_move[1][2]
        eaten_piece = reverted_last_move[1][2] if len(reverted_last_move) == 2 else reverted_last_move[0][2]
        if len(reverted_last_move) != 4:
            if eaten_piece != 0:
                self.add_eaten_piece(eaten_piece)

            promoted_piece = last_move[0][2]
            if promoted_piece != moved_piece:
                self.undo_promotion(reverted_last_move, last_move)

        for piece in turns_pieces:
            piece.revert_move(reverted_last_move)

        king = self.white_king if turn == 0 else self.black_king
        self.update_move_array(king, turns_pieces)

    def undo_promotion(self, reverted_last_move, last_move):
        promoted_piece_short = last_move[0][2]
        promoted_color_bit = color_bit_dict[promoted_piece_short]
        promoted_piece = list(filter(lambda p: p.color_bit == promoted_color_bit and
                                               p.i == reverted_last_move[1][0] and
                                               p.j == reverted_last_move[1][1], self.piece_array))[-1]
        relevant_color_pieces = self.white_pieces if promoted_color_bit == 0 else self.black_pieces

        relevant_color_pieces.remove(promoted_piece)
        self.piece_array.remove(promoted_piece)

        promoted_pawns = self.white_promoted_pawns if promoted_color_bit == 0 else self.black_promoted_pawns
        promoted_pawn = promoted_pawns[-1]
        relevant_color_pieces = self.white_pieces if promoted_color_bit == 0 else self.black_pieces

        relevant_color_pieces.append(promoted_pawn)
        self.piece_array.append(promoted_pawn)
        promoted_pawns.remove(promoted_pawn)

    def add_eaten_piece(self, eaten_piece_short):
        eaten_color_bit = color_bit_dict[eaten_piece_short]
        eaten_pieces = self.black_removed_pieces if eaten_color_bit == 1 else self.white_removed_pieces
        eaten_piece = eaten_pieces[-1]
        eaten_pieces.remove(eaten_piece)
        self.piece_array.append(eaten_piece)
        relevant_color_pieces = self.white_pieces if eaten_color_bit == 0 else self.black_pieces
        relevant_color_pieces.append(eaten_piece)
        return

    def make_move(self, index):
        turn = get_turn(self.short_board.state)
        played_move = self.move_array[index]
        self.previous_moves_stack.append(played_move)
        change = played_move[2] if len(played_move) == 3 else played_move[0]
        if self.short_board.short_array[change[0], change[1]] != 0:
            self.remove_eaten_piece(change, turn)
        moved_piece_value = self.short_board.short_array[played_move[1][0], played_move[1][1]]
        self.make_move_on_board(played_move)
        if moved_piece_value != played_move[0][2]:
            promoted_piece = pieces.create_piece(played_move[0][0], played_move[0][1], self.short_board, self)
            self.promote_pawn(played_move, turn, promoted_piece)
        self.update()

    def promote_pawn(self, played_move, turn, promoted_piece):
        turns_pieces = self.white_pieces if turn == 0 else self.black_pieces
        removed_pawn = [p for p in turns_pieces if p.i == played_move[1][0] and p.j == played_move[1][1]][0]
        promoted_pawns = self.white_promoted_pawns if turn == 0 else self.black_promoted_pawns
        promoted_pawns.append(removed_pawn)
        turns_pieces.remove(removed_pawn)
        self.piece_array.remove(removed_pawn)
        self.piece_array.append(promoted_piece)
        turns_pieces.append(promoted_piece)
        promoted_piece.update()
        return

    def remove_eaten_piece(self, change, turn):
        enemy_pieces = self.white_pieces if turn == 1 else self.black_pieces
        enemy_removed_pieces = self.white_removed_pieces if turn == 1 else self.black_removed_pieces
        eaten_piece = [p for p in enemy_pieces if p.i == change[0] and p.j == change[1]][0]
        enemy_pieces.remove(eaten_piece)
        self.piece_array.remove(eaten_piece)
        enemy_removed_pieces.append(eaten_piece)
        if eaten_piece.piece_index == 4 and \
                (eaten_piece.i == 0 or eaten_piece.i == board_size - 1) and \
                (eaten_piece.j == 0 or eaten_piece.j == board_size - 1) and \
                eaten_piece.castle:
            self.update_castle_removed_rook(eaten_piece)
        if eaten_piece.piece_index == 6:
            self.update_move_array(eaten_piece, enemy_pieces)
            raise Exception('king gets eaten !!!')

    def make_move_on_board(self, played_move):
        inverted_move = []
        for change in played_move:
            i, j = change[0], change[1]
            inverted_move.append((i, j, self.short_board.short_array[i, j]))
            self.short_board.short_array[i, j] = change[2]
        inverted_move.reverse()
        self.revert_moves_stack.append(inverted_move)
        move_turn(self.short_board)

    def update_castle_removed_rook(self, eaten_rook):
        if eaten_rook.i == 0:
            update_castle_state(self.short_board, 2) if eaten_rook.j == 0 else update_castle_state(self.short_board, 4)
        else:
            update_castle_state(self.short_board, 8) if eaten_rook.j == 0 else update_castle_state(self.short_board, 16)

