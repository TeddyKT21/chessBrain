import numpy as np
import math
from boards.byte_board import ByteBoard
from boards.str_board import StrBoard

board_size = 8
piece_size = 8

index_to_piece_dict = {0: "", 1: "p", 2: "k", 3: "b", 4: "r", 5: "q", 6: "ke"}

piece_to_index_dict = {"": 0, "p": 1, "k": 2, "b": 3, "r": 4, "q": 5, "ke": 6}

byte_piece_to_index_dict = {131: 6, 129: 6, 67: 5, 65: 5, 35: 4, 33: 4, 19: 3, 17: 3, 11: 2, 9: 2, 7: 1, 5: 1, 0: 0}

color_bit_dict = {131: 1, 129: 0, 67: 1, 65: 0, 35: 1, 33: 0, 19: 1, 17: 0, 11: 1, 9: 0, 7: 1, 5: 0}

white_king_value = 129
white_queen_value = 65
white_rook_value = 33
white_bishop_value = 17
white_knight_value = 9
white_pawn_value = 5
black_king_value = 131
black_queen_value = 67
black_rook_value = 35
black_bishop_value = 19
black_knight_value = 11
black_pawn_value = 7


def binary_to_byte_board(binary_number):
    byte_array = np.ndarray((board_size, board_size), dtype=np.uint8)
    state = int(binary_number, 2) % 0b100000
    binary_number = bin(int(binary_number, 2) // 0b100000)
    for h in range(0, board_size):
        for w in range(0, board_size):
            byte = int(binary_number, 2) % 256
            converted_byte = num_to_byte(byte)
            byte_array[h, w] = converted_byte
            binary_number = bin(int(binary_number, 2) // 0b100000000)

    return ByteBoard(byte_array, state)


def get_color_bit(byte):
    return byte // 2 % 2


def str_board_to_binary_number(str_board):
    byte_board = str_board_to_byte_board(str_board)
    return byte_board_to_binary_number(byte_board)


def byte_board_to_binary_number(byte_board):
    binary_number = 0
    for h in range(board_size - 1, -1, -1):
        for w in range(board_size - 1, -1, -1):
            binary_number = binary_number * 0b100000000 + int.from_bytes(byte_board.byte_array[h, w], 'big')
    binary_number *= 0b100000
    binary_number += byte_board.state

    return bin(binary_number)


def covert_to_str_state(byte_state):
    return {StrBoard.state_tuple[0]: byte_state % 2 == 0,
            StrBoard.state_tuple[1]: byte_state // 2 % 2 == 1,
            StrBoard.state_tuple[2]: byte_state // 4 % 2 == 1,
            StrBoard.state_tuple[3]: byte_state // 8 % 2 == 1,
            StrBoard.state_tuple[4]: byte_state // 16 % 2 == 1}


def byte_board_to_str_board(byte_board):
    vectorized_to_str = np.vectorize(byte_piece_to_str)
    str_array = vectorized_to_str(byte_board.byte_array)
    str_state = covert_to_str_state(byte_board.state)
    return StrBoard(str_array, str_state)


def covert_to_byte_state(str_state):
    byte_state = 0
    byte_state += 1 if not str_state[StrBoard.state_tuple[0]] else 0
    byte_state += 2 if str_state[StrBoard.state_tuple[1]] else 0
    byte_state += 4 if str_state[StrBoard.state_tuple[2]] else 0
    byte_state += 8 if str_state[StrBoard.state_tuple[3]] else 0
    byte_state += 16 if str_state[StrBoard.state_tuple[4]] else 0
    return byte_state
    pass


def str_board_to_byte_board(str_board):
    vectorized_to_byte = np.vectorize(str_piece_to_byte)
    byte_array = vectorized_to_byte(str_board.str_array)
    byte_state = covert_to_byte_state(str_board.state)
    return ByteBoard(byte_array, byte_state)


def byte_piece_to_str(byte_piece):
    str_piece = ""
    is_empty = byte_piece % 2 == 0
    if not is_empty:
        str_piece = "w" if byte_piece // 2 % 2 == 0 else "b"
        piece_index = byte_piece_to_index_dict[byte_piece]
        str_piece += index_to_piece_dict[piece_index]

    return str_piece

    return str_piece


def str_piece_to_byte(str_piece):
    byte_piece = 0
    if not str_piece == "":
        byte_piece += 1
        byte_piece += 2 if str_piece[0] == "b" else 0
        byte_piece += math.pow(2, piece_to_index_dict[str_piece[1:]] + 1)
    byte_piece = num_to_byte(byte_piece)
    return byte_piece


def num_to_byte(num):
    return np.clip(num, 0, 255).astype(np.uint8)


# def get_piece_index(byte_piece):
#     return byte_piece_to_index_dict[byte_piece]


def can_castle_queen_side(state, color_bit):
    divisor = 2 if color_bit == 0 else 8
    return state // divisor % 2 == 1


def can_castle_king_side(state, color_bit):
    divisor = 4 if color_bit == 0 else 16
    return state // divisor % 2 == 1


def update_state(byte_board):
    if byte_board.byte_array[0, 3] != 129:  # is white king in place
        if byte_board.state // 2 % 4 != 0:
            byte_board.state = byte_board.state // 8 * 8 + 1

    if byte_board.byte_array[7, 3] != 133:  # is black king in place
        if byte_board.state // 8 % 4 != 0:
            byte_board.state = byte_board.state % 8

    if byte_board.byte_array[0, 0] != 33:  # is white king side rook in place
        if byte_board.state // 4 % 2 != 0:
            byte_board.state = byte_board.state - 4

    if byte_board.byte_array[0, 7] != 33:  # is white queen side rook in place
        if byte_board.state // 4 % 2 != 0:
            byte_board.state = byte_board.state - 4

    if byte_board.byte_array[7, 0] != 35:  # is black king side rook in place
        if byte_board.state // 16 % 2 != 0:
            byte_board.state = byte_board.state - 16

    if byte_board.byte_array[7, 7] != 35:  # is black queen side rook in place
        if byte_board.state // 8 % 2 != 0:
            byte_board.state = byte_board.state - 8
    return


def move_turn(byte_board):
    if byte_board.state % 2 == 0:
        byte_board.state += 1
    else:
        byte_board.state -= 1
    return


def get_turn(byte_state):
    return byte_state % 2
