import tensorflow as tf
from tensorflow import keras
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout

import torch
import torch.nn as nn
import torch.nn.functional as F


class EvalNet(nn.Module):
    def __init__(self):
        super(EvalNet, self).__init__()
        self._layers = [nn.Linear(789, 400, dtype=torch.float32),
                        nn.Linear(400, 80, dtype=torch.float32),
                        nn.Linear(80, 50, dtype=torch.float32),
                        nn.Linear(50, 30, dtype=torch.float32),
                        nn.Linear(30, 15, dtype=torch.float32),
                        nn.Linear(15, 1, dtype=torch.float32)]

    def predict(self, data):
        res = torch.from_numpy(data)
        for layer in self._layers:
            res = F.sigmoid(layer(res))
        return res


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
