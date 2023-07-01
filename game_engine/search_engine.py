import numpy as np
import random

from game_engine.evaluator import Evaluator
from move_generation.converters import get_turn
from move_generation.move_generator import MoveGenerator
from move_generation.short_board import ShortBoard


class GameEngine:
    def __init__(self, repository, eval_net, evaluator_type, iterations=1, game_length_limit=250, save_freq=15,
                 training=True, study_start=True, draw_cap=0.4):
        self.evaluator = None
        self.board = None
        self.move_generator = None
        self.iterations = iterations
        self.evaluator_type = evaluator_type
        self.eval_net = eval_net
        self.repository = repository
        self.game_length_limit = game_length_limit
        self.save_freq = save_freq
        self.training = training
        self.study_start = study_start
        self.draw_cap = draw_cap
        self.games_tot = 0
        self.draws_tot = 0

    def _make_move(self):
        selected_move_index = self._get_move(self.move_generator.move_array)
        selected_move = self.move_generator.move_array[selected_move_index]
        self.evaluator.make_move(selected_move)
        self.move_generator.make_move(selected_move_index)

    def play(self):
        n = 0
        while self.games_tot < self.iterations:
            board = ShortBoard()
            self.move_generator = MoveGenerator(board)
            self.evaluator = self.evaluator_type(self.eval_net, board)
            k = 0
            game = {'positions': [], 'result': 0}
            while k < self.game_length_limit:
                self._make_move()
                # print(self.move_generator.short_board, f'move number {k}')
                num = random.randint(0, self.save_freq)
                if num == self.save_freq:
                    game['positions'] += (self.evaluator.bit_position.tolist())
                k += 1

                if not self.move_generator.move_array:
                    game['result'] = self.get_result()
                    if game['result']:
                        self._save_game(game)
                    else:
                        if self.games_tot * self.draw_cap > self.draws_tot:
                            self._save_game(game)
                            self.draws_tot += 1
                    break

                if self.check_draw_formal():
                    if self.games_tot * self.draw_cap > self.draws_tot:
                        self._save_game(game)
                        self.draws_tot += 1
                    break
            n += 1
            if n % 10 == 0:
                print(n)

    def _save_game(self, game):
        if not self.study_start:
            end_const = len(game['positions']) // 3 + 1
            game['positions'] = game['positions'][-end_const:]
        if len(game['positions']) > 10:
            game['positions'] = random.choices(game['positions'], k=10)
        self.repository.save_game(game)
        self.games_tot += 1

    def get_result(self):
        if self.move_generator.black_king.checking_pieces:
            return 1
        if self.move_generator.white_king.checking_pieces:
            return -1
        return 0

    def _get_move(self, move_array):
        move_values = self.evaluator.evaluate(move_array)
        refactored_values = self.process_move_values(move_values)
        return np.argmax(refactored_values) if not self.training else self._get_training_move(refactored_values)

    def process_move_values(self, move_values):
        turn = get_turn(self.move_generator.short_board.state)
        convert_factor = 1 - 2 * turn
        refactored_values = list(map((lambda v: v * convert_factor), move_values))
        min_val = min(refactored_values)
        max_val = max(refactored_values)
        # conf_const = self._get_conf_const(refactored_values)
        # refactored_values = list(map((lambda v: v - min_val), refactored_values))
        i = 0
        for val in refactored_values:
            span = max_val - val
            refactored_values[i] = pow(1-pow((span * 0.5), 0.5), 8) * (abs((max_val + val) / 2) + 0.2)
            i += 1
        total = sum(refactored_values)
        re_scale_factor = 100 / total
        return list(map((lambda v: v * re_scale_factor), refactored_values))

    def _get_training_move(self, move_values):
        # if len(self.move_generator.previous_moves_stack) > 50 and random.uniform(0, 1) > 0.5:
        #     return np.argmax(move_values)
        # if len(self.move_generator.previous_moves_stack) > 10 and random.uniform(0, 1) > 0.5:
        #     return np.argmax(move_values)
        # move_values = [pow(m, 3) * 1000 + 0.05 for m in move_values]
        total = sum(move_values)
        random_num = random.uniform(0, total)
        total = 0
        for index, v in enumerate(move_values):
            total += v
            if total >= random_num:
                return index
        print('total: ', total, ' random num: ', random_num)

    def check_draw(self):
        if self.check_draw_formal():
            return True

        number_of_pieces = len(self.move_generator.piece_array)
        indexes = [2, 3]
        if number_of_pieces == 4:
            other_pieces = [p for p in self.move_generator.piece_array if p != self.move_generator.white_king and
                            p != self.move_generator.black_king]
            p1 = other_pieces[0]
            p2 = other_pieces[1]
            if p1.piece_index in indexes and p2.piece_index in indexes:
                if p1.color_bit != p2.color_bit:
                    return True
                if p1.piece_index != p2.piece_index:
                    return False
                if (abs(p1.i - p2.i) + abs(p1.j - p2.j)) % 2 == 0:
                    return True
        return False

    def check_draw_formal(self):
        number_of_pieces = len(self.move_generator.piece_array)
        if number_of_pieces < 3:
            return True
        indexes = [2, 3]
        if number_of_pieces == 3:
            third_piece = [p for p in self.move_generator.piece_array if p != self.move_generator.white_king and
                           p != self.move_generator.black_king][0]
            if third_piece.piece_index in indexes:
                return True
        return False

    def _get_conf_const(self, move_values):
        span = max(move_values) - min(move_values)
        if span > 1:
            return 0
        d_from_draw = max(abs(min(move_values)), abs(max(move_values)))
        return pow(1-span, 8) * 0.3 * d_from_draw
