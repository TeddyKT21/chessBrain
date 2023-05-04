import random
import time

import numpy as np
import cProfile
import re

from move_generation.short_board import ShortBoard
from move_generation.move_generator import MoveGenerator


def main_program():
    moves = 0
    n = 200

    for m in range(n):
        state = 0b0000000011110
        short_array = np.array([[8, 2, 4, 32, 16, 4, 2, 8],
                                [1, 1, 1, 1, 1, 1, 1, 1],
                                [0, 0, 0, 0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0, 0, 0, 0],
                                [64, 64, 64, 64, 64, 64, 64, 64],
                                [512, 128, 256, 2048, 1024, 256, 128, 512]], dtype=np.short)
        # short_array = np.array([[8, 64, 0, 0, 32, 0, 64, 64],
        #                         [0, 64, 0, 0, 1, 0, 64, 64],
        #                         [0, 0, 0, 16, 0, 0, 64, 64],
        #                         [0, 0, 0, 0, 0, 0, 64, 64],
        #                         [0, 0, 0, 0, 0, 0, 64, 64],
        #                         [0, 0, 0, 0, 0, 0, 64, 64],
        #                         [0, 0, 0, 0, 0, 0, 64, 64],
        #                         [0, 0, 0, 0, 0, 0, 64, 2048]], dtype=np.short)
        board = ShortBoard(short_array, state)
        # print(board)
        game_engine = MoveGenerator(board)
        k = make_random_moves(game_engine, 250)
        revert_game(game_engine)
        make_random_moves(game_engine, 250)
        print(m, k)
        # if k < 249:
        #     print(move_generator.short_board)
        moves += k
    print('avg length: ', moves / n)


def revert_game(game_engine):
    while game_engine.previous_moves_stack:
        game_engine.revert()
        # print(move_generator.short_board)


def make_random_moves(game_engine, n):
    for k in range(n):
        if not game_engine.move_array:
            break
        if len(game_engine.piece_array) < 3:
            break
        move_index = random.randint(0, len(game_engine.move_array) - 1)
        game_engine.make_move(move_index)
        # print(move_generator.short_board)
        # print(k)
    return k


start = time.time()
main_program()
end = time.time()
print('total run time: ', end - start)
# cProfile.run('re.compile(main_program())', sort='tottime')
