import numpy as np
import random

from game_engine.evaluator import Evaluator
from game_engine.move_tree import MoveTree
from move_generation.converters import get_turn, short_piece_to_index_dict
from move_generation.move_generator import MoveGenerator
from move_generation.short_board import ShortBoard


class GameEngine:
    def __init__(self, repository, eval_net, evaluator_type, iterations=1, game_length_limit=250, save_freq=15,
                 training=True, study_start=True, draw_cap=0.3, tree_size=10):
        self.evaluator = None
        self.board = None
        self.move_generator = None
        self.move_tree = None
        self.tree_size = tree_size
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
        selected_move = self.move_tree.move_array[selected_move_index]
        self.evaluator.make_move(selected_move)
        self.move_generator.make_move_non_index(selected_move)

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
                if self.games_tot % 150 == 0:
                    print(self.move_generator.short_board, f'move number {k}')
                num = random.randint(0, self.save_freq)
                if num == self.save_freq and self.move_generator.move_array:
                    game['positions'] += (self.evaluator.bit_position.tolist())
                k += 1

                if not self.move_generator.move_array:
                    game['result'] = self.get_result()
                    game['positions'] += (self.evaluator.bit_position.tolist())
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
        self.move_tree = MoveTree(move_array, move_values, get_turn(self.move_generator.short_board.state))
        self.search()
        refactored_values = self.process_move_values(self.move_tree.move_values)
        return np.argmax(refactored_values) if not self.training else self._get_training_move(refactored_values)

    def _create_node(self, parent_node, index):
        return MoveTree(self.move_generator.move_array,
                        self.evaluator.evaluate(self.move_generator.move_array),
                        get_turn(self.move_generator.short_board.state),
                        parent_node, index)

    def _rollback(self, d, best_move):
        self.move_generator.revert()
        self.evaluator.revert_position(best_move)
        return d - 1

    def _roll_forward(self, d, best_move):
        self.evaluator.make_move(best_move)
        self.move_generator.make_move_non_index(best_move)
        return d + 1

    def search(self):
        best_move_index = self.move_tree.get_best_index()
        best_move = self.move_tree.move_array[best_move_index]
        depth = 0
        parent_node = None
        new_node = self.move_tree
        i = 0

        while i < self.tree_size:
            if not self.move_generator.move_array:
                parent_node.move_values[new_node.index] = self.get_result()
                parent_node.propagate()
                depth = self._rollback(depth, best_move)
                new_node = parent_node
                best_move_index = new_node.get_best_index()
                if abs(parent_node.move_values[best_move_index]) == 1:
                    break
                parent_node = parent_node.parent
                continue
            if best_move_index == new_node.get_best_index():  # the best move stayed the same
                parent_node = new_node
                best_move_index = parent_node.get_best_index()
                best_move = parent_node.move_array[best_move_index]
                depth = self._roll_forward(depth, best_move)
                potential_new_node = [n for n in new_node.children_array if n.index == best_move_index]
                if not potential_new_node:
                    new_node = self._create_node(parent_node, best_move_index)
                    i += 1
                else:
                    parent_node = new_node
                    new_node = potential_new_node[0]
                    best_move_index = new_node.get_best_index()

            else:                                                # the best move is now a different one
                depth = self._rollback(depth, best_move)
                best_move_index = parent_node.get_best_index()
                best_move = parent_node.move_array[best_move_index]
                new_node = parent_node
                parent_node = parent_node.parent

        while depth:
            depth = self._rollback(depth, best_move)
            best_move_index = parent_node.get_best_index()
            best_move = parent_node.move_array[best_move_index]
            parent_node = parent_node.parent


    def process_move_values(self, move_values):
        turn = get_turn(self.move_generator.short_board.state)
        convert_factor = 1 - 2 * turn
        refactored_values = list(map((lambda v: v * convert_factor), move_values))
        min_val = min(refactored_values)
        max_val = max(refactored_values)
        i = 0
        for val in refactored_values:
            span = max_val - val
            refactored_values[i] = pow(1 - pow((span * 0.5), 0.5), 10)
            i += 1
        total = sum(refactored_values)
        re_scale_factor = 100 / total
        return list(map((lambda v: v * re_scale_factor), refactored_values))

    def _get_training_move(self, move_values):
        if max(move_values) >= 55:
            return np.argmax(move_values)
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
        if number_of_pieces <= 5 and \
                len(self.move_generator.revert_moves_stack) > 50 and not \
                [rm for rm in self.move_generator.revert_moves_stack[-50:] if
                 len(rm) > 2 or (rm[0][2] != 0 and rm[1][2] != 0) or short_piece_to_index_dict[rm[1][2]] == 1]:
            return True
        if number_of_pieces < 3:
            return True
        indexes = [2, 3]
        if number_of_pieces == 3:
            third_piece = [p for p in self.move_generator.piece_array if p != self.move_generator.white_king and
                           p != self.move_generator.black_king][0]
            if third_piece.piece_index in indexes:
                return True
        return False
