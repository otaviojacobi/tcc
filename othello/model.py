import torch
import torch.nn as nn
import torch.nn.functional as F


CONVOLUTIONAL_FILTERS = 64

class ConvolutionalBlock(nn.Module):
    def __init__(self, features):
        super(ConvolutionalBlock, self).__init__()
        self.conv = nn.Conv2d(features, CONVOLUTIONAL_FILTERS, kernel_size=3, padding=1)
        self.bn = nn.BatchNorm2d(CONVOLUTIONAL_FILTERS)

    def forward(self, x):
        return F.relu(self.bn(self.conv(x)))


class ResidualLayer(nn.Module):
    def __init__(self):
        super(ResidualLayer, self).__init__()

        self.layers = nn.Sequential(
            nn.Conv2d(CONVOLUTIONAL_FILTERS, CONVOLUTIONAL_FILTERS, kernel_size=3, padding=1),
            nn.BatchNorm2d(CONVOLUTIONAL_FILTERS),
            nn.ReLU(),
            nn.Conv2d(CONVOLUTIONAL_FILTERS, CONVOLUTIONAL_FILTERS, kernel_size=3, padding=1),
            nn.BatchNorm2d(CONVOLUTIONAL_FILTERS),
        )

    def forward(self, x):
        return self.layers(x)


class ResidualBlock(nn.Module):

    def __init__(self, blocks):
        super(ResidualBlock, self).__init__()

        self.layers = nn.ModuleList([ResidualLayer() for _ in range(blocks)])

    def forward(self, x):

        ipt = x.clone().to(x.device)
        for layer in self.layers:
            x = layer(x)
            x.add_(ipt)
            x = F.relu(x)

        return x


class PolicyNN(nn.Module):

    def __init__(self, action_space):
        super(PolicyNN, self).__init__()

        self.action_space = action_space

        self.conv = nn.Conv2d(CONVOLUTIONAL_FILTERS, 2, 1)
        self.bn = nn.BatchNorm2d(2)
        self.fc = nn.Linear(2 * action_space, action_space)

    def forward(self, x):
        x = F.relu(self.bn(self.conv(x)))
        x = x.view(-1, 2 * self.action_space)

        # TODO: I added the softmax, is it correct ? who knows
        return torch.softmax(self.fc(x), dim=1)
        #return self.fc(x)


class ValueNN(nn.Module):

    def __init__(self, action_space):
        super(ValueNN, self).__init__()

        self.action_space = action_space

        self.conv = nn.Conv2d(CONVOLUTIONAL_FILTERS, 2, 1)
        self.bn = nn.BatchNorm2d(2)
        self.fc1 = nn.Linear(2 * action_space, 256)
        self.fc2 = nn.Linear(256, 1)


    def forward(self, x):
        x = F.relu(self.bn(self.conv(x)))
        x = x.view(-1, 2 * self.action_space)
        x = F.relu(self.fc1(x))
        return torch.tanh(self.fc2(x))


class AlphaNet(nn.Module):
    def __init__(self, features=3, residual_blocks=9, action_space=64):
        super(AlphaNet, self).__init__()

        self.convolutional_block = ConvolutionalBlock(features)
        self.residual_block = ResidualBlock(residual_blocks)
        self.policy_head = PolicyNN(action_space)
        self.value_head = ValueNN(action_space)

    def forward(self, x):
        x = self.convolutional_block(x)
        x = self.residual_block(x)
        p = self.policy_head(x)
        v = self.value_head(x)
        return p, v
