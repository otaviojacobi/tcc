from DynModel import DynModel
from PredictionModel import PredictionModel
from RepresentationModel import RepresentationModel
from mcts.MCTS import MCTS

from numpy.random import choice
import pickle
from copy import deepcopy

from tqdm import tqdm

import ray

ray.init()

class MuZero:
    def __init__(self, options, Env, *envargs):
        self.options = options
        self.g = DynModel()
        self.f = PredictionModel(options)
        self.h = RepresentationModel()

        self.Env = Env
        self.envargs = envargs

    @ray.remote
    def run_game(env, f, g, h, options, simulations):
        done = False
        rewards = []
        observe_buffer = []
        steps = 0

        while True:
            s0 = h.forward(env)

            mcts = MCTS(s0, f, g, options)
            pi = mcts.run_sim(simulations)

            opt = choice(options, 1, p=pi)[0]
            action = opt.action #for simplicity for now

            s, r, done = env.step(action)
            rewards.append(r)

            s_next = h.forward(env)

            observe_buffer.append([s0, opt, s_next, r, pi])

            steps += 1
            if steps % 10000 == 1:
                print(f'[{steps} steps] [state {env.cur_x, env.cur_y}] [goal {env.goal_x, env.goal_y}] [h_dist {abs(env.cur_x - env.goal_x) + abs(env.cur_y - env.goal_y)}]')

            if done:
                break

        #print('total returns', returns)
        # adds Z
        print('Updating Z ...')
        for idx in range(len(observe_buffer)):
            Z = 0
            gamma = 0.99
            # TODO: remove this for 20k smaller returns
            for pow, r in enumerate(rewards[idx:idx+20000]):
                Z += (gamma ** pow) * r
            observe_buffer[idx].append(Z)
        print('Finished calculating Z')

        return observe_buffer, sum(rewards)

    def learn(self, epochs, batch_size, simulations=100):

        returns = []
        for epoch in range(epochs):#tqdm(range(epochs)):

            results = [self.run_game.remote(self.Env(*self.envargs), deepcopy(self.f), deepcopy(self.g), deepcopy(self.h), deepcopy(self.options), simulations) for _ in range(batch_size)]
            results = ray.get(results)

            for result in results:
                observe_buffer, full_return = result

                returns.append(full_return)
                print('Training...')
                for sample in observe_buffer:
                    s0, opt, s1, r, pi, z = sample
                    self.g.observe(s0, opt, s1, r)
                    self.f.observe(s0, pi, z)
                print('Finished training...')


        return returns

    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump({'g': self.g, 'f': self.f, 'h': self.h}, f)

    def load(self, path):
        with open(path, 'rb') as f:
            content = pickle.load(f)
            self.f, self.g, self.h = content['f'], content['g'], content['h']

