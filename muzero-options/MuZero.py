from DynModel import DynModel
from PredictionModel import PredictionModel
from RepresentationModel import RepresentationModel
from mcts.MCTS import MCTS

from numpy.random import choice
import pickle
import numpy as np

from tqdm import tqdm
from copy import deepcopy

class MuZero:
    def __init__(self, env, options):
        self.options = options
        self.env = env
        self.g = DynModel()
        self.f = PredictionModel(options)
        self.h = RepresentationModel()

    def learn(self, epochs, simulations=100, verbose=False, alpha=0.01):

        returns = []
        argmax_returns = []


        for epoch in tqdm(range(epochs)):
            done = False
            rewards = []
            observe_buffer = []
            s_next = self.env.reset()
            steps = 0
            undiscounted_return = 0

            while True:
                s0 = s_next

                mcts = MCTS(s0, self.f, self.g, self.options)
                pi = mcts.run_sim(simulations)

                #print(s0, pi)
                #mcts.info()

                opt = choice(self.options, 1, p=pi)[0]

                counter = 0
                gamma = 0.99
                inner_rewards = []
                while True:
                    action, should_finish = opt.get_action(self.env)

                    if action == -1:
                        break

                    check_s, r, done = self.env.step(action)
                    #discounted_reward += (gamma ** counter) * r
                    inner_rewards.append(r)
                    undiscounted_return += r
                    counter += 1
                    steps += 1
                    s_next = check_s

                    if should_finish:
                        break


                rewards.append(deepcopy(inner_rewards))

                #s_next = self.h.forward(self.env)

                observe_buffer.append([s0, opt, s_next, pi])

                if verbose and steps % 10000 == 1:
                    print(f'[{epoch}/{epochs}] [{steps} steps] [state {self.env.cur_x, self.env.cur_y}] [goal {self.env.goal_x, self.env.goal_y}] [h_dist {abs(self.env.cur_x - self.env.goal_x) + abs(self.env.cur_y - self.env.goal_y)}]')

                if done:
                    break

            returns.append(undiscounted_return)

            #returns.append(sum(rewards))
            #print('total returns', returns)
            # adds Z

            assert len(observe_buffer) == len(rewards)

            #print('Updating Z ...')
            for idx in range(len(observe_buffer)):
                Z = 0
                gamma = 0.99
                power = 0

                for i, r_list in enumerate(rewards[idx:]):
                    for r in r_list:
                        Z += (gamma ** power) * r
                        power += 1
                
                observe_buffer[idx].append(deepcopy(rewards[idx]))
                observe_buffer[idx].append(Z)
            #print('Finished calculating Z')

            #print('Training...')
            for sample in observe_buffer:
                #print(sample)
                s0, opt, s1, pi, rs, z = sample
                self.g.observe(s0, opt, s1, rs)
                self.f.observe(s0, pi, z, alpha=alpha)

            #print('Finished training...')
            #argmax_returns.append(self.play_arg_max_no_sim())

        return returns, argmax_returns

    def play_arg_max_no_sim(self):

        total_return = 0
        done = False
        s_next = self.env.reset()
        while not done:
            s0 = s_next

            p, v = self.f.forward(s0, [])
            opt_idx = np.argmax(p)
            opt = self.options[opt_idx]
            
            while True:
                action, should_break = opt.get_action(self.env)

                if action == -1 or done:
                    break

                s_next, r, done = self.env.step(action)
                total_return += r

                if should_break:
                    break

        return total_return

    def play(self, env, simulations):

        total_return = 0
        done = False
        while not done:
            s0 = self.h.forward(env)

            mcts = MCTS(s0, self.f, self.g, self.options)
            pi = mcts.run_sim(simulations)

            #opt_idex = np.argmax(pi)
            #action = self.options[opt_idex].action #for simplicity for now

            opt = np.random.choice(self.options, 1, p=pi)[0]
            
            while True:
                action, should_break = opt.get_action(env) #for simplicity for now

                if action == -1 or done:
                    break

                s, r, done = env.step(action)
                total_return += r

                if should_break:
                    break

        return total_return

    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump({'g': self.g, 'f': self.f, 'h': self.h}, f)

    def load(self, path):
        with open(path, 'rb') as f:
            content = pickle.load(f)
            self.f, self.g, self.h = content['f'], content['g'], content['h']

