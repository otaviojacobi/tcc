from othello_cython import Othello, move_to_action
from alpha_search import MCTS
from random import choices

def run_simulation(memory, nn, render=False):

    TEMPERATURE = 1.0

    env = Othello()
    m = MCTS(env, nn)
    counter = 0
    while True:

        if render:
            env.render()

        possible_moves = env.legal_moves()
        if len(possible_moves) == 0:
            break

        s, pi, z = m.run(200, TEMPERATURE)

        memory.push(s, pi, z)

        distr = [pi[move_to_action(move)] for move in possible_moves]
        a = choices(possible_moves, distr)[0]
        env.play(a)

        m.set_new_head(a)

        counter += 1
        if counter > 10:
            TEMPERATURE = 0.01
