def get_data_set(repository):
    games = repository.get_games()
    positions_arr = []
    results_arr = []
    for game in games:
        positions = game['positions']
        positions_arr += game['positions']
        for position in positions:
            results_arr.append(game['result'])
    return {'positions': positions_arr, 'results': results_arr}


def train(net, repository):
    dat_set = get_data_set(repository)
    # add training logic here
