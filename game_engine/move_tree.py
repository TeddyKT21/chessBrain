import numpy as np


class MoveTree:
    def __init__(self, move_array, move_values,turn ,parent=None, index=-1):
        self.parent = parent
        # descending nodes in the move tree
        self.children_array = []
        self.index = index
        self.parent_move = None
        self.move_array = move_array
        self.move_values = move_values
        self.turn = turn
        if parent:
            parent.children_array.append(self)
            self.propagate()

    def get_best_index(self):
        if not self.move_array:
            return None
        return np.argmin(self.move_values) if self.turn else np.argmax(self.move_values)

    def propagate(self):
        if not self.parent or not self.move_array:
            return
        best_move_index = self.get_best_index()
        self.parent.move_values[self.index] = self.move_values[best_move_index]
        self.parent.propagate()

