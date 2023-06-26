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


def get_repositories(epoch):
    repositories = []
    if epoch < 10:
        for i in range(epoch + 1):
            repositories.append(Repository(f"gameCollection{i}", False))
    else:
        for i in range(epoch - 10,epoch + 1):
            repositories.append(Repository(f"gameCollection{i}", False))
    return repositories


def main_program():
    for i in range(10):
        print(f"random epoc {i + 1}")
        repository = Repository(f"gameCollectionRandom{i}")
        game_engine = GameEngine(repository, DummyNet(), DummyEvaluator, 40000, 400, 20, False)
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

    epochs = 1000
    repository = Repository(f"gameCollection0")
    for epoch in range(20, epochs):
        print(f'starting epoc {epoch + 1}:')
        game_collection = f"gameCollection{epoch}"
        net = repository.get_model()
        repository = Repository(game_collection)
        game_engine = GameEngine(repository, net, Evaluator, 1000, 400, 8)

        start = time.time()
        game_engine.play()
        end = time.time()
        print('play stage completed after: ', end - start)

        start = time.time()
        repositories = get_repositories(epoch)
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
# cProfile.run('re.compile(main_program())', sort='tottime')
