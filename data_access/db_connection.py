from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017')
db = client.ChessBrainDb


def save_game(game):
    db.games.insert_one(game)


def get_games():
    return db.games.find()
