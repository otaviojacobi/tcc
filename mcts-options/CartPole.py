
import gym
from copy import deepcopy

class CartPole:

    def __init__(self, env=None):
        if env == None:
            self.env = gym.make('CartPole-v0')
            self.env.reset()
        else:
            self.env = env

        self.is_over = False

    def  step(self, action):
        s, r, done, _ = self.env.step(action)
        if done:
            self.is_over = True
        return s, r, done

    def reset(self):
      self.env.reset()

    def copy(self):
        env_copy = deepcopy(self.env)
        new_pole = CartPole(env_copy)
        new_pole.is_over = self.is_over

        return new_pole


    def is_leaf(self):
        return self.is_over

    def finished(self):
        return self.is_over

    def legal_moves(self):
        return [0, 1]



