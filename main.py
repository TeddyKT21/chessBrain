import random
import time
import cProfile
import re

from boards.chess_board import ChessBoard
import converters
from move_generator.legal_pos_generator import LegalPosGenerator
from boards.str_board import StrBoard


def select_move(moves):
    prefered_moves = list(filter(lambda move: move[0][2] < 100, moves))
    if not prefered_moves:
        random_num = random.randrange(0, len(moves))
        return random_num
    random_num = random.randrange(0, len(prefered_moves))
    return random_num


def main_program():
    str_board = StrBoard()
    str_board.str_array[0, 3] = 'wke'
    str_board.str_array[0, 0] = 'wr'
    str_board.str_array[0, 7] = 'wr'
    str_board.str_array[0, 1] = 'wk'
    str_board.str_array[0, 6] = 'wk'
    str_board.str_array[0, 2] = 'wb'
    str_board.str_array[0, 5] = 'wb'
    str_board.str_array[0, 4] = 'wq'

    str_board.str_array[7, 3] = 'bke'
    str_board.str_array[7, 0] = 'br'
    str_board.str_array[7, 7] = 'br'
    str_board.str_array[7, 1] = 'bk'
    str_board.str_array[7, 6] = 'bk'
    str_board.str_array[7, 2] = 'bb'
    str_board.str_array[7, 5] = 'bb'
    str_board.str_array[7, 4] = 'bq'

    for k in range(8):
        str_board.str_array[1, k] = 'wp'
        str_board.str_array[6, k] = 'bp'

    # str_board.str_array[0, 7] = 'wke'
    # str_board.str_array[1, 7] = 'wp'
    # str_board.str_array[2, 6] = 'wp'
    # str_board.str_array[6, 3] = 'bke'
    # str_board.str_array[7, 2] = 'wr'
    # str_board.str_array[0, 2] = 'br'
    # str_board.str_array[1, 4] = 'bk'
    #
    # str_board.str_array[7, 0] = 'bb'
    # str_board.str_array[4, 3] = 'bp'

    long_num = converters.str_board_to_binary_number(str_board)
    print('original number:\n', long_num, '\n', 'length:', len(long_num), '\n')
    random_board = ChessBoard(long_num)
    print(random_board)

    for k in range(200):
        generator = LegalPosGenerator()
        moves = generator.generate_legal_positions(long_num)
        # print(ChessBoard(long_num).byte_board.byte_array)
        # print('\n')
        counter = 0
        while counter < 250 and len(moves) > 0 and len(generator.piece_array) > 2:
            next_move = select_move(moves)
            # print(generator.move_array[next_move])
            moves = generator.make_move(next_move)
            # print(generator.byte_board)
            counter += 1
        if counter < 250:
            print(generator.byte_board)
            print('done ! after:', counter, " positions")
        print(k)


start = time.time()
main_program()
# cProfile.run('re.compile(main_program())', sort='time')
end = time.time()
print('total run time: ', end-start)