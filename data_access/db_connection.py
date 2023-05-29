import json

import numpy as np
import torch
from pymongo import MongoClient

from game_engine.eval_net import EvalNet

client = MongoClient('mongodb://localhost:27017')
db = client.ChessBrainDb
model_save_location = 'evalNet.pt'


class Repository:
    def __init__(self, game_collection, model_collection):
        self.game_collection = game_collection
        self.model_collection = model_collection

    def save_game(self, game):
        db[self.game_collection].insert_one(game)

    def get_games(self):
        return db[self.game_collection].find()

    def save_model(self, model):
        torch.save(model.state_dict(), model_save_location)
        # model_state_numpy = {key: value.numpy() for key, value in model.state_dict().items()}
        # model_state_serializable = {key: value.tolist() for key, value in model_state_numpy.items()}
        # model_json = json.dumps(model_state_serializable)
        # db[self.model_collection].insert_one({'model_state': model_json})

    def get_model(self):
        # document = db[self.model_collection].find_one()
        # model_json = document['model_state']
        # model_state_serializable = json.loads(model_json)
        # model_state_numpy = {key: np.array(value) for key, value in model_state_serializable.items()}
        # model_state = {key: torch.from_numpy(value) for key, value in model_state_numpy.items()}
        # model = EvalNet()
        # model.load_state_dict(model_state)
        # return model
        model = EvalNet()
        model.load_state_dict(torch.load(model_save_location))
        model.eval()
        return model
