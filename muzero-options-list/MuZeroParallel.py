from DynModel import DynModel
from PredictionModel import PredictionModel
from RepresentationModel import RepresentationModel
from mcts.MCTS import MCTS
from ReplayBuffer import ReplayBuffer

import numpy as np
import pickle
from copy import deepcopy

import ray
from ray.util.queue import Queue
from filelock import FileLock

from time import sleep
import numpy as np

ray.init()

class MuZero:
    def __init__(self, options, Env, *envargs):
        self.options = options
        self.g = DynModel()
        self.f = PredictionModel(options)
        self.h = RepresentationModel()

        self.queue = Queue()

        self.Env = Env
        self.envargs = envargs

        print('Starting training by saving current weights')
        with FileLock("model.pickle.lock"):
            with open("model.pickle","wb") as thefile:
                pickle.dump({'g': self.g, 'f': self.f, 'h': self.h}, thefile)
        print('Finished saving weights weights')

    @ray.remote
    def run_game(queue, env, options, simulations, epoch, epochs):

        print(f'Running game {epoch}')

        with FileLock("model.pickle.lock"):
            with open("model.pickle","rb") as thefile:
                model = pickle.load(thefile)

        f, g, h = model['f'], model['g'], model['h']

        done = False
        rewards = []
        observe_buffer = []
        steps = 0

        np.random.seed(epoch)

        while True:
            s0 = h.forward(env)

            mcts = MCTS(s0, f, g, options)
            pi = mcts.run_sim(simulations)

            opt = np.random.choice(options, 1, p=pi)[0]
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
            for pow, r in enumerate(rewards[idx:idx+5000]):
                Z += (gamma ** pow) * r
            observe_buffer[idx].append(Z)
        print('Finished calculating Z')

        queue.put([tuple(o) for o in observe_buffer])

        if epoch == epochs-1:
            queue.put('done')

        return sum(rewards)

    @ray.remote
    def train(buffer, epochs):

        memory_buffer = ReplayBuffer(20000)

        with FileLock("model.pickle.lock"):
            with open("model.pickle","rb") as thefile:
                model = pickle.load(thefile)

        f, g, h = model['f'], model['g'], model['h']
        training_steps = 0

        start_countdown = False
        after_countdown_timesteps = 0
        while True:

            if start_countdown and after_countdown_timesteps > 3000:
                print('Shutdown finished !!!')
                break

            try:
                observe_buffer = buffer.get(block=False)
                if type(observe_buffer) is str:
                    if observe_buffer == 'done':
                        print('Shutdown started !!!')
                        start_countdown = True
                        continue
                #if observe_buffer 
                memory_buffer.push(observe_buffer)
            except Exception as e:
                pass
                #print('Empty buffer')
            #print('Training...')

            if len(memory_buffer) > 1000:
                samples = memory_buffer.sample(32)
                for sample in samples:
                    s0, opt, s1, r, pi, z = sample
                    g.observe(s0, opt, s1, r)
                    f.observe(s0, pi, z)
                #print('Finished training...')
                
                #print('Saving new model')
                if training_steps % 500 == 0:
                    with FileLock("model.pickle.lock"):
                        with open("model.pickle","wb") as thefile:
                            pickle.dump({'f': f, 'g': g, 'h': h}, thefile)
                #print('New model saved')
            else:
                sleep(1)

            training_steps += 1
            if start_countdown:
                after_countdown_timesteps += 1

    def learn(self, epochs, simulations=100):

        print('Started learning')
        train = self.train.remote(self.queue, epochs)
        print('Triggered remote train')

        sleep(1)

        print('Starting selfplay')
        results = [self.run_game.remote(self.queue, self.Env(*self.envargs), deepcopy(self.options), simulations, epoch, epochs) for epoch in range(epochs)]
        print('Triggered self plays')

        ray.get(train)
        returns = ray.get(results)

        with FileLock("model.pickle.lock"):
            with open("model.pickle","rb") as thefile:
                model = pickle.load(thefile)

        self.f, self.g, self.h = model['f'], model['g'], model['h']

        return returns

    def play(self, env, simulations):

        total_return = 0
        done = False
        while not done:
            s0 = self.h.forward(env)

            mcts = MCTS(s0, self.f, self.g, self.options)
            pi = mcts.run_sim(simulations)

            opt_idex = np.argmax(pi)
            action = self.options[opt_idex].action #for simplicity for now

            #opt = np.random.choice(self.options, 1, p=pi)[0]
            #action = opt.action #for simplicity for now

            s, r, done = env.step(action)

            #print(s)
            #print(total_return)
            total_return += r

        return total_return


    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump({'g': self.g, 'f': self.f, 'h': self.h}, f)

    def load(self, path):
        with open(path, 'rb') as f:
            content = pickle.load(f)
            self.f, self.g, self.h = content['f'], content['g'], content['h']

