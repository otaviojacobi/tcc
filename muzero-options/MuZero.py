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

                inner_rewards = []
                while True:
                    action, should_finish = opt.get_action(self.env)

                    if action == -1:
                        break

                    s_next, r, done = self.env.step(action)
                    inner_rewards.append(r)
                    undiscounted_return += r
                    steps += 1

                    if should_finish:
                        break


                rewards.append(deepcopy(inner_rewards))
                observe_buffer.append([s0, opt, s_next, pi])

                if verbose and steps % 10000 == 1:
                    print(f'[{epoch}/{epochs}] [{steps} steps] [state {self.env.cur_x, self.env.cur_y}] [goal {self.env.goal_x, self.env.goal_y}] [h_dist {abs(self.env.cur_x - self.env.goal_x) + abs(self.env.cur_y - self.env.goal_y)}]')

                if done:
                    break

            returns.append(undiscounted_return)
            assert len(observe_buffer) == len(rewards)
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

            for sample in observe_buffer:
                s0, opt, s1, pi, rs, z = sample
                self.g.observe(s0, opt, s1, rs)
                self.f.observe(s0, pi, z, alpha=alpha)

        return returns

    def play_simple(self, env, ms_time_budget=40):


        total_return = 0
        done = False
        all_sims = []
        options = []
        s_next = env.reset()
        states = [s_next]
        while not done:
            s0 = s_next

            mcts = MCTS(s0, self.f, self.g, self.options)
            pi, sims = mcts.run_time(ms_time_budget)

            all_sims.append(sims)

            opt = np.random.choice(self.options, 1, p=pi)[0]

            options.append(opt)
            
            while True:
                action, should_break = opt.get_action(env)

                if action == -1 or done:
                    break

                s_next, r, done = env.step(action)
                states.append(s_next)
                total_return += r

                if should_break:
                    break

        return total_return, all_sims, options, states


    def play_lookahead(self, env, ms_time_budget=40):

        total_return = 0
        done = False
        all_sims = []
        options = []
        s_next = env.reset()
        states = [s_next]

        prefetched = False
        while not done:
            s0 = s_next

            if not prefetched or s0 != next_predicted_state:
                mcts = MCTS(s0, self.f, self.g, self.options)
            pi, sims = mcts.run_time(ms_time_budget)

            all_sims.append(sims)

            prefetched = False

            opt = np.random.choice(self.options, 1, p=pi)[0]

            options.append(opt)

            next_predicted_state, _ = self.g.forward(s0, opt)

            step_counter = 0
            while True:
                action, should_break = opt.get_action(env)

                if action == -1 or done:
                    break

                s_next, r, done = env.step(action)

                states.append(s_next)
                total_return += r

                # prefetching
                if step_counter > 0:
                    if prefetched:
                        mcts.run_time(ms_time_budget-3)
                    else:
                        prefetched = True
                        mcts = MCTS(next_predicted_state, self.f, self.g, self.options)
                        mcts.run_time(ms_time_budget-4)

                if should_break:
                    break

                step_counter += 1

            if s_next != next_predicted_state:
                print('model failure')

        return total_return, all_sims, options, states

    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump({'g': self.g, 'f': self.f, 'h': self.h}, f)

    def load(self, path):
        with open(path, 'rb') as f:
            content = pickle.load(f)
            self.f, self.g, self.h = content['f'], content['g'], content['h']

