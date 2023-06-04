import time

import numpy as np
import cProfile
import re

from data_access.db_connection import Repository
from game_engine.dummy_net import DummyNet
from game_engine.eval_net import EvalNet
from game_engine.search_engine import GameEngine
from training.train import train


def main_program():
    repository = Repository(f"gameCollectionRandom")
    game_engine = GameEngine(repository, DummyNet(), 100000, 400, 30, False)
    start = time.time()
    print(f'generating initial random games...')
    game_engine.play()
    end = time.time()
    print('randomplay stage completed after: ', end - start)
    print('-------------------------------------------------------------------------------------------------')
    net = repository.get_model()
    start = time.time()
    train(net, repository)
    end = time.time()
    print('training  stage completed after: ', end - start)
    repository.save_model(net)
    print('-------------------------------------------------------------------------------------------------')

    epochs = 100
    repository = Repository(f"gameCollection0")
    for epoch in range(epochs):
        print(f'starting epoc {epoch + 1}:')
        game_collection = f"gameCollection{epoch}"
        model_collection = f"modelCollection{epoch}"
        net = repository.get_model()
        repository = Repository(game_collection)
        game_engine = GameEngine(repository, net, 500, 400, 30)

        start = time.time()
        game_engine.play()
        end = time.time()
        print('play stage completed after: ', end - start)

        start = time.time()
        train(net, repository)
        end = time.time()
        print('training  stage completed after: ', end - start)

        repository.save_model(net)
        print('-------------------------------------------------------------------------------------------------')



start = time.time()
main_program()
end = time.time()
print('total run time: ', end - start)
# cProfile.run('re.compile(main_program())', sort='tottime')
