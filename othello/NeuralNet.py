from model import AlphaNet
import torch

class NeuralNet:

    def __init__(self, device="cuda" if torch.cuda.is_available() else "cpu"):

        if device == "cuda":
            print('Neural net on ', torch.cuda.get_device_name(0))
        else:
            print('Neural net on cpu')

        self.device = torch.device(device)
        self.nn = AlphaNet().to(self.device)

    def forward(self, X):
        return self.nn(X)

    def get_device(self):
        return self.device
