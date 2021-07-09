import torch.nn as nn
import torch.nn.functional as F

class DQN(nn.Module):

    def __init__(self, action_space):
        super(DQN, self).__init__()
        self.conv1 = nn.Conv2d(4, 16, kernel_size=8, stride=4)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=4, stride=2)
        self.fc = nn.Linear(2592, 256) # 32 * 9 * 9
        self.head = nn.Linear(256, action_space)

    def forward(self, x):
        #x = x.to(device)
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = F.relu(self.fc(x.view(x.size(0), -1)))
        return self.head(x)
