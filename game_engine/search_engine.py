import numpy as np
import random

from game_engine.evaluator import Evaluator
from move_generation.move_generator import MoveGenerator
from move_generation.short_board import ShortBoard


class GameEngine:
    def __init__(self, repository, eval_net, iterations=1, game_length_limit=250, save_freq=15):
        self.board = None
        self.move_generator = None
        self.iterations = iterations
        self.evaluator = None
        self.eval_net = eval_net
        self.repository = repository
        self.game_length_limit = game_length_limit
        self.save_freq = save_freq

    def _make_move(self):
        selected_move_index = self.get_move(self.move_generator.move_array)
        selected_move = self.move_generator.move_array[selected_move_index]
        self.evaluator.make_move(selected_move)
        self.move_generator.make_move(selected_move_index)

    def play(self):
        for n in range(self.iterations):
            board = ShortBoard()
            self.move_generator = MoveGenerator(board)
            self.evaluator = Evaluator(self.eval_net, board)
            k = 0
            game = {'positions':[], 'result': 0}
            while k < self.game_length_limit:
                print(k)
                self._make_move()
                if not self.move_generator.move_array:
                    game['result'] = self.get_result()
                    break
                if len(self.move_generator.piece_array) < 3:
                    break
                num = random.randint(0, self.save_freq)
                if num == self.save_freq:
                    game['positions'].append(self.evaluator.bit_position.tolist())
                k += 1
            self.repository.save_game(game)

    def get_result(self):
        if self.move_generator.black_king.checking_pieces:
            return -1
        if self.move_generator.white_king.checking_pieces:
            return 1
        return 0

    def get_move(self, move_array):
        move_values = np.zeros(len(move_array), float)
        for i in range(len(move_array)):
            result = self.evaluator.evaluate(move_array[i])
            move_values[i] = result
        return np.argmax(move_values)
