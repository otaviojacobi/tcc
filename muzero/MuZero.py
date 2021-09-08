from DynModel import DynModel
from PredictionModel import PredictionModel
from RepresentationModel import RepresentationModel
from mcts.MCTS import MCTS

from numpy.random import choice
import pickle

from tqdm import tqdm

class MuZero:
    def __init__(self, env, options):
        self.options = options
        self.env = env
        self.g = DynModel()
        self.f = PredictionModel(options)
        self.h = RepresentationModel()

    def learn(self, epochs, simulations=100):

        returns = []
        for epoch in range(epochs):#tqdm(range(epochs)):
            done = False
            rewards = []
            observe_buffer = []
            self.env.reset()
            steps = 0
            while True:
                s0 = self.h.forward(self.env)

                mcts = MCTS(s0, self.f, self.g, self.options)
                pi = mcts.run_sim(simulations)

                opt = choice(self.options, 1, p=pi)[0]
                action = opt.action #for simplicity for now

                s, r, done = self.env.step(action)
                rewards.append(r)

                s_next = self.h.forward(self.env)

                observe_buffer.append([s0, opt, s_next, r, pi])

                steps += 1
                if steps % 10000 == 1:
                    print(f'[{epoch}/{epochs}] [{steps} steps] [state {self.env.cur_x, self.env.cur_y}] [goal {self.env.goal_x, self.env.goal_y}] [h_dist {abs(self.env.cur_x - self.env.goal_x) + abs(self.env.cur_y - self.env.goal_y)}]')

                if done:
                    break

            returns.append(sum(rewards))
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

