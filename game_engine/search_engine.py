import numpy as np

from move_generation.move_generator import MoveGenerator


class GameEngine:
    def __init__(self, evaluator, repository, short_board=None, iterations=1, game_length_limit=250):
        self.initial_board = short_board
        self.move_generator = MoveGenerator(short_board)
        self.iterations = iterations
        self.evaluator = evaluator
        self.repository = repository
        self.game_length_limit = game_length_limit

    def _make_move(self):
        selected_move_index = self.get_move(self.move_generator.move_array)
        selected_move = self.move_generator.move_array[selected_move_index]
        self.evaluator.make_move(selected_move)
        self.move_generator.make_move(selected_move_index)

    def play(self):
        results = []
        for n in range(self.iterations):
            self.move_generator = MoveGenerator(self.initial_board)
            k = 0
            while k < self.game_length_limit:
                self._make_move()
                if not self.move_generator.move_array:
                    results.append(self.get_result())
                    break
                if len(self.move_generator.piece_array < 3):
                    break
                # if k % 20 == 0:
                #     self.repository.add(self.evaluator.bit_position)
                k += 1

    def get_result(self):
        if self.move_generator.black_king.checking_pieces:
            return -1
        if self.move_generator.white_king.checking_pieces:
            return 1
        return 0

    def get_move(self, move_array):
        move_values = np.zeros(len(move_array), np.float)
        for i in range(len(move_array)):
            move_values[i] = self.evaluator.evaluate(move_array[i])
        return np.argmax(move_values)
