from torch import nn, optim
from torch.utils.data import DataLoader

from training.position_data_set import PosDataSet


def get_data_set(repository):
    games = repository.get_games()
    positions_arr = []
    results_arr = []
    for game in games:
        positions = game['positions']
        positions_arr += game['positions']
        for position in positions:
            results_arr.append(game['result'])
    return PosDataSet(positions_arr, results_arr)


def train(net, repository):
    criterion = nn.MSELoss()
    optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9)
    data_set = get_data_set(repository)
    if len(data_set) < 1:
        return
    dataloader = DataLoader(data_set,batch_size=len(data_set), shuffle=True)

    for inputs, labels in dataloader:
        optimizer.zero_grad()
        outputs = net(inputs)
        loss = criterion(outputs,  labels.view(-1, 1).float())
        loss.backward()
        optimizer.step()

