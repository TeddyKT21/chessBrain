from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017')
db = client.ChessBrainDb


class Repository:
    def __init__(self, game_collection, model_collection):
        self.game_collection = game_collection
        self.model_collection = model_collection

    def save_game(self, game):
        db[self.game_collection].insert_one(game)

    def get_games(self):
        return db[self.game_collection].find()

    def save_model(self, model):
        db[self.model_collection].insert_one(model)

    def get_model(self):
        return db[self.model_collection].find()[0]
