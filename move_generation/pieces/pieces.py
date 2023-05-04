from move_generation.pieces.bishop import Bishop
from move_generation.pieces.king import King
from move_generation.pieces.knight import Knight
from move_generation.pieces.pawn import Pawn
from move_generation.pieces.queen import Queen
from move_generation.pieces.rook import Rook
from move_generation.converters import short_piece_to_index_dict


def create_piece(i, j, short_board, game_engine):
    short = short_board.short_array[i, j]
    index = short_piece_to_index_dict[short]
    match index:
        case 1:
            return Pawn(i, j, short_board, game_engine)
        case 2:
            return Knight(i, j, short_board, game_engine)
        case 3:
            return Bishop(i, j, short_board, game_engine)
        case 4:
            return Rook(i, j, short_board, game_engine)
        case 5:
            return Queen(i, j, short_board, game_engine)
        case 6:
            return King(i, j, short_board, game_engine)
        case _:
            raise Exception('invalid self !')
    return
