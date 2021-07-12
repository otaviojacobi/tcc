import argparse
from trainer import train

gym_envs = [
  'Breakout-v4',
  'PongNoFrameskip-v4'
]

parser = argparse.ArgumentParser(description='Train DQN.')

parser.add_argument('--env', choices=gym_envs, default='PongNoFrameskip-v4', help='The gym environment to run')
parser.add_argument('--memory_size', type=int, default=int(40000), help='Replay Buffer size')
parser.add_argument('--batch_size', type=int, default=32, help='Batch Size')
parser.add_argument('--gamma', type=float, default=0.99, help='Q-learning gamma')
parser.add_argument('--target_update', type=int, default=1000, help='Double Q-Learning target update every x updates')
parser.add_argument('--lr', type=float, default=1e-4, help='Neural Net Optimizer learning rate')
parser.add_argument('--episodes', type=int, default=5000, help='The amount of episodes which the agent will train on')
parser.add_argument('--stack_frames', type=int, default=4, help='How many frames to stack for the state') #TODO: not fixed on net archtiecture
parser.add_argument('--save_every', type=int, default=500, help='Save policy/target nn weights every x episode')

args = vars(parser.parse_args())

train(**args)
