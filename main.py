import time

import numpy as np
import cProfile
import re

from data_access.db_connection import Repository
from game_engine.eval_net import EvalNet
from game_engine.search_engine import GameEngine


def main_program():
    epochs = 1000
    repository = Repository(f"gameCollection0", f"modelCollection0")
    for epoch in range(epochs):
        game_collection = f"gameCollection{epoch}"
        model_collection = f"modelCollection{epoch}"
        net = EvalNet() if epoch == 0 else repository.get_model()
        repository = Repository(game_collection, model_collection)
        game_engine = GameEngine(repository, net, 250, 150)
        game_engine.play()
        train(net, repository)
        repository.save_model(net)



start = time.time()
main_program()
end = time.time()
print('total run time: ', end - start)
# cProfile.run('re.compile(main_program())', sort='tottime')
