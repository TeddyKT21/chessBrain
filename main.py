import random
import time

import numpy as np
import cProfile
import re

from game_engine.eval_net import EvalNet
from game_engine.evaluator import Evaluator
from game_engine.search_engine import GameEngine
from move_generation.short_board import ShortBoard
from move_generation.move_generator import MoveGenerator


def main_program():
    game_engine = GameEngine(None, EvalNet(), 10, 150)
    game_engine.play()


start = time.time()
main_program()
end = time.time()
print('total run time: ', end - start)
# cProfile.run('re.compile(main_program())', sort='tottime')
