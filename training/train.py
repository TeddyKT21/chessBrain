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



    last_len = 0
    games = repository_arr[-1].get_games()
    for game in games:
        last_len += len(game['positions'])

    val_len = min((last_len // 4), 2000) if last_len < 25000 else min((last_len // 10), 5000)

    return PosDataSet(positions_arr[:-val_len], results_arr[:-val_len]), \
           PosDataSet(positions_arr[-val_len:], results_arr[-val_len:])


def train(net, repository_arr, initial_stop_count=8, min_buffer=1.01):
    net.train()
    train_losses = []
    eval_losses = []
    stop_count = initial_stop_count

    criterion = nn.MSELoss()
    optimizer = optim.SGD(net.parameters(), lr=0.003, momentum=0.6)
    # optimizer = optim.Adam(net.parameters(), lr=0.003)
    train_data, val_data = get_data_sets(repository_arr)
    test_loader = DataLoader(val_data, batch_size=len(val_data))

    min_val_loss = 4
    batch_size = min(len(train_data) // 50, 50)
    for epoch in range(120):
        if not stop_count:
            print('early stop because of steady error streak')
            break

        info_string = f'epoch {epoch}: '
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

        avg = sum(epoch_losses) / len(epoch_losses)
        train_losses.append(avg)
        info_string += f'train_error: {avg}, '

        for inputs, labels in test_loader:
            net.eval()
            outputs = net(inputs)
            loss = criterion(outputs, labels.view(-1, 1).float())
            info_string += f'val_error: {loss.item()}'

            if (loss.item() * min_buffer) < min_val_loss:
                stop_count = initial_stop_count - 1
                min_val_loss = min(min_val_loss, loss.item())
            else:
                stop_count = stop_count - 1

            eval_losses.append(loss.item())
            net.train()

        print(info_string)
        separation_len = initial_stop_count // 2 + 1
        if len(eval_losses) > separation_len:
            force_stop = True
            for i in range(len(eval_losses) - 1, len(eval_losses) - separation_len, -1):
                if eval_losses[i] - eval_losses[i - 1] < min_buffer:
                    force_stop = False
            if force_stop:
                print('early stop because of error increase')
                break

    losses.append(train_losses[-1])
    test_losses.append(eval_losses[-1])
    print('train losses: ', train_losses)
    print('test losses: ', eval_losses)
    net.eval()
