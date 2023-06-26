from torch import nn, optim
from torch.utils.data import DataLoader

from training.position_data_set import PosDataSet
from torch.utils.data import random_split

losses = []
test_losses = []

def get_data_set(repository_arr):
    positions_arr = []
    results_arr = []
    for i in range(len(repository_arr)):
        games = repository_arr[i].get_games()
        for game in games:
            positions = game['positions']
            positions_arr += positions
            for position in positions:
                results_arr.append(game['result'])
    return PosDataSet(positions_arr, results_arr)


def train(net, repository_arr):
    net.train()
    train_losses = []
    eval_losses = []

    criterion = nn.MSELoss()
    optimizer = optim.Adam(net.parameters(), lr=0.001)
    data_set = get_data_set(repository_arr)
    val_size = 100 if len(data_set) < 1000 else 500
    if len(data_set) < 100:
        return
    train_data, val_data = random_split(data_set, [len(data_set) - val_size, val_size])
    test_loader = DataLoader(val_data, batch_size=val_size, shuffle=True)

    for epoch in range(50):
        train_loader = DataLoader(train_data, batch_size=50, shuffle=True)
        epoch_losses = []

        for batch in train_loader:
            inputs, labels = batch
            optimizer.zero_grad()
            outputs = net(inputs)
            loss = criterion(outputs, labels.view(-1, 1).float())
            epoch_losses.append(loss.item())
            loss.backward()
            optimizer.step()

        train_losses.append(sum(epoch_losses) / len(epoch_losses))

        for inputs, labels in test_loader:
            outputs = net(inputs)
            loss = criterion(outputs, labels.view(-1, 1).float())
            eval_losses.append(loss.item())

    losses.append(train_losses[-1])
    test_losses.append(eval_losses[-1])
    print('train losses: ', train_losses)
    print('test losses: ', eval_losses)
    net.eval()
