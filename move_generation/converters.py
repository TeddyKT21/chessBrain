import numpy as np

from move_generation.short_board import ShortBoard, board_size

state_size = 0b10000000000000
piece_size = 0b1000000000000

short_piece_to_index_dict = {2048: 6, 32: 6, 1024: 5, 16: 5, 512: 4, 8: 4, 256: 3, 4: 3, 128: 2, 2: 2, 64: 1, 1: 1,
                             0: 0}

color_bit_dict = {0: -1, 1: 0, 2: 0, 4: 0, 8: 0, 16: 0, 32: 0, 64: 1, 128: 1, 256: 1, 512: 1, 1024: 1, 2048: 1}


def binary_to_short_board(binary_number):
    short_array = np.ndarray((board_size, board_size), dtype=np.short)
    state = int(binary_number, 2) % state_size
    binary_number = bin(int(binary_number, 2) // state_size)
    for h in range(0, board_size):
        for w in range(0, board_size):
            short = int(binary_number, 2) % piece_size
            converted_short = num_to_short(short)
            short_array[h, w] = converted_short
            binary_number = bin(int(binary_number, 2) // piece_size)

    return ShortBoard(short_array, state)


def num_to_short(num):
    return np.clip(num, 0, 32767).astype(np.short)


def short_board_to_binary_number(short_board):
    binary_number = 0
    for h in range(board_size - 1, -1, -1):
        for w in range(board_size - 1, -1, -1):
            binary_number = binary_number * piece_size + int.from_bytes(short_board.short_array[h, w], 'little')
    binary_number *= state_size
    binary_number += short_board.state

    return bin(binary_number)


def get_turn(byte_state):
    return byte_state % 2


def can_castle_queen_side(state, color_bit):
    divisor = 2 if color_bit == 0 else 8
    return state // divisor % 2 == 1


def can_castle_king_side(state, color_bit):
    divisor = 4 if color_bit == 0 else 16
    return state // divisor % 2 == 1


def move_turn(short_board):
    short_board.state = short_board.state % pow(2, 6)
    if short_board.state % 2 == 0:
        short_board.state += 1
    else:
        short_board.state -= 1
    return


def is_same_move(m1, m2):
    if m1 == m2:
        return True
    if len(m1) != len(m2):
        return False
    if len(m1) == 4:
        return m1[0][0] == m2[0][0] and m1[0][1] == m2[0][1]
    return m1[0][0] == m2[0][0] and m1[0][1] == m2[0][1] and m1[1][0] == m2[1][0] and m1[1][1] == m2[1][1]
