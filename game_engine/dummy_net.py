import random


class DummyNet:
    def predict(self, bit_position):
        return random.uniform(-1, 1)

    def forward(self, data):
        return random.uniform(-1, 1)
