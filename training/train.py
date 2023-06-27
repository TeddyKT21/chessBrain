from torch import nn, optim
from torch.utils.data import DataLoader

from training.position_data_set import PosDataSet
from torch.utils.data import random_split

losses = []
test_losses = []


def get_data_sets(repository_arr):
    positions_arr = []
    results_arr = []
    for i in range(len(repository_arr)):
        games = repository_arr[i].get_games()
        for game in games:
            positions = game['positions']
            positions_arr += positions
            for position in positions:
                results_arr.append(game['result'])
    val_len = 0
    if len(repository_arr) == 1:
        val_len = min((len(positions_arr) // 4), 1000)
    else:
        last_len = 0
        games = repository_arr[-1].get_games()
        for game in games:
            last_len += len(game['positions'])

        val_len = min((last_len // 4), 1000)
        positions_arr = positions_arr[:-(last_len - val_len)]
        results_arr = results_arr[:-(last_len - val_len)]

    return PosDataSet(positions_arr[:-val_len], results_arr[:-val_len]), \
           PosDataSet(positions_arr[-val_len:], results_arr[-val_len:])


def train(net, repository_arr):
    net.train()
    train_losses = []
    eval_losses = []

    criterion = nn.MSELoss()
    optimizer = optim.Adam(net.parameters(), lr=0.0005)
    train_data, val_data = get_data_sets(repository_arr)
    test_loader = DataLoader(val_data, batch_size=len(val_data))

    min_val_loss = 4
    stop_count = 10
    batch_size = min(len(train_data) // 50, 50)
    for epoch in range(120):
        if not stop_count:
            break
        train_loader = DataLoader(train_data, batch_size=batch_size, shuffle=True)
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
            net.eval()
            outputs = net(inputs)
            loss = criterion(outputs, labels.view(-1, 1).float())
            stop_count = 10 if loss.item() < min_val_loss else stop_count - 1
            min_val_loss = min(min_val_loss, loss.item())
            eval_losses.append(loss.item())
            net.train()

    losses.append(train_losses[-1])
    test_losses.append(eval_losses[-1])
    print('train losses: ', train_losses)
    print('test losses: ', eval_losses)
    net.eval()
