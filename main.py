import time

import numpy as np
import cProfile
import re

from data_access.db_connection import Repository
from game_engine.dummy_evaluator import DummyEvaluator
from game_engine.dummy_net import DummyNet
from game_engine.evaluator import Evaluator
from game_engine.search_engine import GameEngine
from training.train import train, losses,test_losses


def get_repositories(epoch, count=1):
    repositories = []
    if epoch < count:
        for i in range(epoch + 1):
            repositories.append(Repository(f"gameCollection{i}", False))
    else:
        for i in range(epoch - count + 1, epoch + 1):
            repositories.append(Repository(f"gameCollection{i}", False))
    return repositories


def main_program():
    for i in range(0, 5):
        print(f"random epoc {i + 1}")
        repository = Repository(f"gameCollectionRandom{i}", False)
        game_engine = GameEngine(repository, DummyNet(), DummyEvaluator, 15000, 400, 10, False, tree_size=0)
        start = time.time()
        game_engine.play()
        end = time.time()
        print('random play stage completed after: ', end - start)
        print('-------------------------------------------------------------------------------------------------')

        net = repository.get_model()
        start = time.time()
        train(net, [repository])
        end = time.time()
        print('training (on random) stage completed after: ', end - start)
        repository.save_model(net)
        print('-------------------------------------------------------------------------------------------------')

    print('loss progression: ', losses)
    print('test loss progression: ', test_losses)
    print('-------------------------------------------------------------------------------------------------')

    epochs = 100
    repository = Repository(f"gameCollection0")
    for epoch in range(0, epochs):
        print(f'starting epoc {epoch + 1}:')
        game_collection = f"gameCollection{epoch}"
        net = repository.get_model()
        net.eval()
        repository = Repository(game_collection)
        tree_size = 0 if epoch < 0 else 12

        game_engine = GameEngine(repository, net, Evaluator, 1500, 500, 8, tree_size=tree_size)

        start = time.time()
        game_engine.play()
        end = time.time()
        print('play stage completed after: ', end - start)

        start = time.time()
        repositories = get_repositories(epoch, 1)
        train(net, repositories)
        end = time.time()
        print('training  stage completed after: ', end - start)

        repository.save_model(net)
        print('-------------------------------------------------------------------------------------------------')

    print('loss progression: ', losses)
    print('test loss progression: ', test_losses)
    print('-------------------------------------------------------------------------------------------------')


start = time.time()
main_program()
end = time.time()
print('total run time: ', end - start)
# cProfile.run('re.compile(main_program())', sort='cumtime')
