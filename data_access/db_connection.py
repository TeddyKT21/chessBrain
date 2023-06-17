import json
import os

import numpy as np
import torch
from pymongo import MongoClient

from game_engine.eval_net import EvalNet

client = MongoClient('mongodb://localhost:27017')
db = client.ChessBrainDb
model_save_location = 'evalNet.pt'


class Repository:
    def __init__(self, game_collection):
        if game_collection in db.list_collection_names():
            db[game_collection].drop()
        self.game_collection = game_collection

    def save_game(self, game):
        db[self.game_collection].insert_one(game)

    def get_games(self):
        return db[self.game_collection].find()

    def save_model(self, model):
        torch.save(model.state_dict(), model_save_location)

    def get_model(self):
        model = EvalNet()
        if os.path.exists(model_save_location):
            model.load_state_dict(torch.load(model_save_location))
        model.eval()
        # model.printModel()
        return model
