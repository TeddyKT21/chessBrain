import tensorflow as tf
from tensorflow import keras
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout

import torch
import torch.nn as nn
import torch.nn.functional as F


def init_weights(m):
    if isinstance(m, nn.Linear):
        nn.init.xavier_uniform_(m.weight)  # Random initialization for weights
        nn.init.zeros_(m.bias)


class EvalNet(nn.Module):
    def __init__(self):
        super(EvalNet, self).__init__()
        self.dropout1 = nn.Dropout(p=0.4)
        self.layer1 = nn.Linear(789, 800, )
        self.layer2 = nn.Linear(800, 1000, )
        self.layer3 = nn.Linear(1000, 800, )
        # self.layer4 = nn.Linear(1000, 1000, )
        # self.layer5 = nn.Linear(1200, 800, )
        self.layer6 = nn.Linear(800, 600, )
        self.layer7 = nn.Linear(600, 400, )
        self.layer8 = nn.Linear(400, 300,)
        self.layer9 = nn.Linear(300, 1, )
        self.layers = [self.layer1,
                       self.layer2,
                       self.layer3,
                       # self.layer4,
                       # self.layer5,
                       self.layer6,
                       self.layer7,
                       self.layer8,
                       self.layer9]
        self.start_tanh = 7
        self.start_dropout = 1
        self.apply(init_weights)
        self.eval()

    @torch.no_grad()
    def predict(self, data):
        res = torch.from_numpy(data).to(self.layer1.weight.dtype)
        for layer in self.layers[:-self.start_tanh]:
            res = F.leaky_relu(layer(res))
        for layer in self.layers[-self.start_tanh:]:
            res = F.tanh(layer(res))
        return res

    def forward(self, data):
        for i, layer in self.layers[:-self.start_tanh]:
            data = F.leaky_relu(layer(data))
            if i >= self.start_dropout:
                data = self.dropout1(data)
        for i, layer in self.layers[-self.start_tanh:]:
            data = F.tanh(layer(data))
            if i >= self.start_dropout:
                data = self.dropout1(data)
        return data

    def printModel(self):
        for layer in self.layers:
            print('layer:')
            print('biases:')
            print(layer.bias)
            print('waights:')
            print(layer.weight)

# class Net(nn.Module):
#
#     def __init__(self):
#         super(Net, self).__init__()
#         # 1 input image channel, 6 output channels, 5x5 square convolution
#         # kernel
#         self.conv1 = nn.Conv2d(1, 6, 5)
#         self.conv2 = nn.Conv2d(6, 16, 5)
#         # an affine operation: y = Wx + b
#         self.fc1 = nn.Linear(16 * 5 * 5, 120)  # 5*5 from image dimension
#         self.fc2 = nn.Linear(120, 84)
#         self.fc3 = nn.Linear(84, 10)
#
#     def forward(self, x):
#         # Max pooling over a (2, 2) window
#         x = F.max_pool2d(F.relu(self.conv1(x)), (2, 2))
#         # If the size is a square, you can specify with a single number
#         x = F.max_pool2d(F.relu(self.conv2(x)), 2)
#         x = torch.flatten(x, 1)  # flatten all dimensions except the batch dimension
#         x = F.relu(self.fc1(x))
#         x = F.relu(self.fc2(x))
#         x = self.fc3(x)
#         return x
