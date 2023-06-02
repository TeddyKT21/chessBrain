import time

import numpy as np
import cProfile
import re

from data_access.db_connection import Repository
from game_engine.eval_net import EvalNet
from game_engine.search_engine import GameEngine
from training.train import train


def main_program():
    epochs = 100
    repository = Repository(f"gameCollection0")
    for epoch in range(epochs):
        print(f'starting epoc {epoch + 1}:')
        game_collection = f"gameCollection{epoch}"
        model_collection = f"modelCollection{epoch}"
        net = EvalNet() if epoch == 0 else repository.get_model()
        repository = Repository(game_collection)
        game_engine = GameEngine(repository, net, 10, 400, 30)

        start = time.time()
        game_engine.play()
        end = time.time()
        print('play stage completed after: ', end - start)

        start = time.time()
        train(net, repository)
        end = time.time()
        print('training  stage completed after: ', end - start)
        train(net, repository)

        repository.save_model(net)
        print('-------------------------------------------------------------------------------------------------')



start = time.time()
main_program()
end = time.time()
print('total run time: ', end - start)
# cProfile.run('re.compile(main_program())', sort='tottime')
