import math

import numpy as np
import torch

from move_generation.converters import get_turn, move_turn, short_piece_to_index_dict, color_bit_dict, \
    can_castle_queen_side, can_castle_king_side
from move_generation.short_board import board_size

piece_size = 12


def generate_bit_position(short_board):
    bit_position = np.zeros((1, piece_size * board_size ** 2 + 21), dtype=np.float32)
    get_short_array_bits(bit_position, short_board.short_array)
    get_state_bits(bit_position, short_board.state)
    return bit_position


def get_short_array_bits(bit_position, short_array):
    for i in range(board_size):
        for j in range(board_size):
            pos0 = (i * board_size + j) * piece_size
            piece_val = short_array[i, j]
            scale = round(math.log(piece_val, 2)) if piece_val else -1
            if scale > -1:
                bit_position[0, pos0 + scale] = 1


def get_state_bits(bit_position, state):
    pos0 = piece_size * board_size ** 2
    if state > 0b11111:
        en_passant_location = math.floor(math.log(state))
        en_passant_location += 8 if get_turn(state) == 0 else 0
        bit_position[0, pos0 + en_passant_location] = 1
    for i in range(5 + 16):
        bit_position[0, -1 - i] = (state // math.pow(2, i)) % 2


class Evaluator:
    def __init__(self, eval_net, short_board):
        self.eval_net = eval_net
        self.short_board = short_board
        self.bit_position = generate_bit_position(short_board)

    def evaluate(self, move):
        self.update_position(move)
        result = self.eval_net.predict(self.bit_position)
        # result = random.uniform(-1, 1)
        self.revert_position(move)
        return result

    def revert_position(self, move):
        for change in move:
            current_piece = self.short_board.short_array[change[0], change[1]]
            if current_piece:
                location = (change[0] * board_size + change[1]) * 12 + round(math.log(current_piece, 2))
                self.bit_position[0, location] = 1
            if change[2]:
                location = (change[0] * board_size + change[1]) * 12
                location += round(math.log(change[2], 2)) if change[2] else 0
                self.bit_position[0, location] = 0
            get_state_bits(self.bit_position, self.short_board.state)

    def update_position(self, move):
        for change in move:
            current_piece = self.short_board.short_array[change[0], change[1]]
            if current_piece:
                location = (change[0] * board_size + change[1]) * 12 + round(math.log(current_piece, 2))
                self.bit_position[0, location] = 0
            if change[2]:
                location = (change[0] * board_size + change[1]) * 12
                location += round(math.log(change[2], 2)) if change[2] else 0
                self.bit_position[0, location] = 1
        self.update_state(move)

    def make_move(self, move):
        self.update_position(move)

    def update_state(self, move):
        state = self.short_board.state
        state = state % pow(2, 6)
        self.change_turn(state)
        self.check_did_castle(move, state)
        if len(move) == 2:
            piece_index = short_piece_to_index_dict[move[0][2]]
            piece_color = color_bit_dict[move[0][2]]
            self.check_can_castle(move, piece_color, piece_index)
            if piece_index == 1 and abs(move[0][0] - move[1][1]) == 2:
                self.check_en_passant(move, piece_color)

    def check_en_passant(self, move, piece_color):
        if move[0][1] < board_size - 1:
            other_piece = self.short_board.short_array[move[0][1] + 1, move[0][0]]
            other_piece_index = short_piece_to_index_dict[other_piece]
            other_piece_color = color_bit_dict[other_piece]
            if other_piece_index == 1 and other_piece_color != piece_color:
                color_offset = 8 - 8 * piece_color
                self.bit_position[0, -1 - color_offset - move[0][1]] = 1
        elif move[0][1] > 0:
            other_piece = self.short_board.short_array[move[0][1] - 1, move[0][0]]
            other_piece_index = short_piece_to_index_dict[other_piece]
            other_piece_color = color_bit_dict[other_piece]
            if other_piece_index == 1 and other_piece_color != piece_color:
                color_offset = 8 - 8 * piece_color
                self.bit_position[0, -1 - color_offset - move[0][1]] = 1

    def check_can_castle(self, move, piece_color, piece_index):
        if piece_index == 6:
            if piece_color:
                self.bit_position[0, -4] = 0
                self.bit_position[0, -5] = 0
            else:
                self.bit_position[0, -2] = 0
                self.bit_position[0, -3] = 0
        if piece_index == 4:
            if piece_color and move[1][0] == board_size - 1:
                if move[1][1] == board_size - 1:
                    self.bit_position[0, -4] = 0
                if move[1][1] == 0:
                    self.bit_position[0, -5] = 0
            if not piece_color and move[1][0] == 0:
                if move[1][1] == board_size - 1:
                    self.bit_position[0, -2] = 0
                if move[1][1] == 0:
                    self.bit_position[0, -3] = 0

    def check_did_castle(self, move, state):
        if len(move) == 4:
            if state % 2 == 0:
                self.bit_position[0, -2] = 0
                self.bit_position[0, -3] = 0
            else:
                self.bit_position[0, -4] = 0
                self.bit_position[0, -5] = 0

    def change_turn(self, state):
        if state % 2 == 0:
            self.bit_position[0, -1] = 1
        else:
            self.bit_position[0, -1] = 0
