import torch

from helpers import preprocess_image
import gym
from DQN import DQN

from time import sleep


def best_action(net, s):
    action = net(s).max(1)[0]
    return action

env = gym.make('PongNoFrameskip-v4')
action_space = env.action_space.n
net = DQN(action_space)
net.load_state_dict(torch.load('models/target_net_0.pth',  map_location=torch.device('cpu')))
net.eval()

o = env.reset()
s = preprocess_image(o)

done = False
while not done:

    a = best_action(net, s)

    o, r, done, _ = env.step(a)
    s = preprocess_image(o)

    env.render()
