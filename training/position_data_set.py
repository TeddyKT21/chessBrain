import torch
from torch.utils.data import Dataset


class PosDataSet(Dataset):
    def __init__(self, positions, results):
        self.positions = positions
        self.results = results

    def __len__(self):
        return len(self.results)

    def __getitem__(self, idx):
        return torch.tensor(self.positions[idx]), torch.tensor(self.results[idx])
