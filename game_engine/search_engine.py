import numpy as np
import random

from game_engine.evaluator import Evaluator
from move_generation.converters import get_turn
from move_generation.move_generator import MoveGenerator
from move_generation.short_board import ShortBoard


class GameEngine:
    def __init__(self, repository, eval_net, iterations=1, game_length_limit=250, save_freq=15, training=True, study_start=True):
        self.board = None
        self.move_generator = None
        self.iterations = iterations
        self.evaluator = None
        self.eval_net = eval_net
        self.repository = repository
        self.game_length_limit = game_length_limit
        self.save_freq = save_freq
        self.training = training
        self.study_start = study_start

    def _make_move(self):
        selected_move_index = self._get_move(self.move_generator.move_array)
        selected_move = self.move_generator.move_array[selected_move_index]
        self.evaluator.make_move(selected_move)
        self.move_generator.make_move(selected_move_index)

    def play(self):
        for n in range(self.iterations):
            board = ShortBoard()
            self.move_generator = MoveGenerator(board)
            self.evaluator = Evaluator(self.eval_net, board)
            k = 0
            game = {'positions': [], 'result': 0}
            while k < self.game_length_limit:
                self._make_move()
                # print(self.move_generator.short_board, f'move number {k}')
                if not self.move_generator.move_array:
                    game['result'] = self.get_result()
                if len(self.move_generator.piece_array) < 3:
                    break
                num = random.randint(0, self.save_freq)
                if num == self.save_freq:
                    game['positions'] += (self.evaluator.bit_position.tolist())
                k += 1
                if not self.move_generator.move_array:
                    if game['result']:
                        game['positions'] += (self.evaluator.bit_position.tolist())
                        if not self.study_start:
                            end_const = len(game['positions']) // 3 + 1
                            game['positions'] = game['positions'][-end_const:]
                        self.repository.save_game(game)
                    break
            if n % 10 == 0:
                print(n)

    def get_result(self):
        if self.move_generator.black_king.checking_pieces:
            return -1
        if self.move_generator.white_king.checking_pieces:
            return 1
        return 0

    def _get_move(self, move_array):
        move_values = np.zeros(len(move_array), float)
        for i in range(len(move_array)):
            result = self.evaluator.evaluate(move_array[i])
            move_values[i] = result

        turn = get_turn(self.move_generator.short_board.state)
        convert_factor = 1 - 2 * turn
        refactored_values = list(map((lambda v: (v * convert_factor)), move_values))
        min_val = min(refactored_values)
        refactored_values = list(map((lambda v: (v - min_val + 0.0005)), refactored_values))
        return np.argmax(refactored_values) if not self.training else self._get_training_move(refactored_values)

    def _get_training_move(self, move_values):
        total = sum(move_values)
        random_num = random.uniform(0, total)
        total = 0
        for index, v in enumerate(move_values):
            total += v
            if total >= random_num:
                return index
        print('total: ', total, ' random num: ', random_num)
