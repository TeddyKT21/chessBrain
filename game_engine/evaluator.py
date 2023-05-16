import math

import numpy as np
import torch

from move_generation.converters import get_turn
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
    for i in range(math.floor(math.log(state % 32, 2))):
        bit_position[0, -1 - i] = (state // math.pow(2, i)) % 2


class Evaluator:
    def __init__(self, eval_net, short_board):
        self.eval_net = eval_net
        self.short_board = short_board
        self.bit_position = generate_bit_position(short_board)

    def evaluate(self,  move):
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

    def make_move(self, move):
        self.update_position(move)



