import math

import numpy as np
import torch

from game_engine.evaluator import generate_bit_position, Evaluator
from move_generation.converters import get_turn, short_piece_to_index_dict, color_bit_dict
from move_generation.short_board import board_size

piece_size = 12
pos0 = piece_size * board_size ** 2


class DummyEvaluator(Evaluator):
    def __init__(self, eval_net, short_board):
        super().__init__(eval_net, short_board)

    def evaluate(self, move_array):
        return np.random.uniform(low=-1, high=1, size=len(move_array))
