import torch

from ReplayMemory import ReplayMemory
from NeuralNet import NeuralNet

from simulator import run_simulations
from trainer import run_train
from evaluator import run_evaluate

MEMORY_SIZE = 50000
LEARNING_RATE = 0.01
BATCH_SIZE = 2048
GAMMA = 0.99
L2_TERM = 1e-4

SIMULATIONS = 1
TRAINING_STEPS = 10
EVALUATION_STEPS = 10

memory = ReplayMemory(MEMORY_SIZE)

best_nn = NeuralNet("cpu")
current_nn = NeuralNet("cpu")

def simulate(sims, memory, best_nn):
    for sim in range(sims):

        if sim % 10 == 1:
            print(f'[SIMULATOR] Running simulation {sim}')

        run_simulations(memory, best_nn)

def train(training_steps, memory, current_nn, batch_size, gamma):
    optimizer = torch.optim.Adam(current_nn.nn.parameters(), lr=LEARNING_RATE, weight_decay=L2_TERM)

    for training_step in range(training_steps):
        run_train(current_nn, optimizer, memory, batch_size, gamma)

def evaluate(evaluation_steps, best_nn, current_nn):
    for evaluate_step in range(evaluation_steps):
        print(f'[EVALUATOR] Running evaluation {evaluate_step}')
        run_evaluate(best_nn, current_nn)

# TODO: implement the evaluate function
# TODO: Create a thread/ray-process for each of previous functions
# TODO: create a locker for passing throught the best network/update its weights
# TODO: run all of them in parallel
# TODO: check ray serialization protocol