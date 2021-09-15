import numpy as np
from random import shuffle
import itertools

from random import choice

class Node:
    def __init__(self, env, options=[]):
        self.env = env

        self.parent_edge = None
        self.all_options = options
        self.valid_options = {o for o in options if o.is_valid(env.state())}
        self.edge_count_sum = 0
        self.is_leaf = len(self.valid_options) == 0
        self.child_edges = {}
        self.expanded = False

    def get_highest_ucb_option(self, c, min_q, max_q):

        max_ucb = -np.inf
        best_option = None

        executed = False
        opts = list(self.child_edges.items())
        shuffle(opts)
        for option, edge in opts:
            executed = True
            edge_ucb = edge.ucb(c, min_q, max_q)
            if edge_ucb >= max_ucb:
                max_ucb = edge_ucb
                best_option = option

        if not executed:
            print('Node returned None best_option: empty child_edges')

        return best_option

    def expand(self):
        self.expanded = True

        for option in self.valid_options:
            self.child_edges[option] = Edge(self, None)


    def simulate(self):
        env = self.env.copy()
        done = False
        gamma = 0.99
        i = 0
        disc_return = 0.0
        while not done:
            _, r, done = env.step(choice([0,1,2,3]))

            disc_return += (gamma ** i) * r
            i += 1

        return disc_return


    def backup(self, vl, rewards):
        flatten_rewards = list(itertools.chain(*rewards))

        l = len(flatten_rewards)
        k = l - len(rewards[-1])
        cur_edge = self.parent_edge

        min_q = np.inf
        max_q = -np.inf

        i = -1

        depth = 0

        while cur_edge != None:

            depth = len(rewards[i])
            new_q = cur_edge.update(k, l, vl, flatten_rewards, depth)

            if new_q > max_q:
                max_q = new_q

            if new_q < min_q:
                min_q = new_q

            cur_edge = cur_edge.parent_node.parent_edge
            
            if cur_edge != None:
                i -= 1
                k -= len(rewards[i])
            else:
                if k != 0:
                    print('deu ruim')


        return min_q, max_q

    def info(self, c, min_q, max_q):
        print('Expanded: ', self.expanded)
        print('Leaf: ', self.is_leaf)
        print('state', self.env.state())

        for option, edge in self.child_edges.items():
            print('Option', option)
            edge.info(c, min_q, max_q)
            #if edge.child_node is not None:
                #edge.child_node.info(c1, c2, min_q, max_q)



class Edge:
    def __init__(self, parent_node, child_node):

        self.N = 0
        self.Q = 0.0
        self.N_real = 0

        self.parent_node = parent_node
        self.child_node = child_node
        self.rewards = []

    def ucb(self, c, min_q, max_q, verbose=False):

        if self.N == 0:
            return np.inf

        if min_q != np.inf and max_q != -np.inf and max_q - min_q != 0:
            normalized_Q = (self.Q - min_q) / (max_q - min_q)
        else:
            normalized_Q = self.Q

        N_sum = self.parent_node.edge_count_sum

        if verbose:
            print('Q\'(s, o): ', normalized_Q)

        return normalized_Q + np.sqrt((c * np.log(N_sum))/self.N)


    def expand(self, option, options):

        env = self.parent_node.env.copy()
        rewards = []
        done = False
        while True:
            action, should_break = option.get_action(env)

            if action == -1 or done:
                break

            _, r, done = env.step(action)
            rewards.append(r)

            if should_break:
                break

        self.rewards = rewards

        self.child_node = Node(env, options)
        self.child_node.parent_edge = self
        self.child_node.expand()

        return self.child_node, rewards

    def update(self, k, l, vl, rewards, depth):
        gamma = 0.99
        G_k = 0

        for t in range(l-k):
            G_k += (gamma ** t) * rewards[k+t]

        G_k += (gamma ** (l-k)) * vl

        self.Q = ((self.N_real * self.Q) + G_k) / (self.N_real + 1)
        self.N_real += depth
        self.N = self.N + 1
        self.parent_node.edge_count_sum += 1

        return self.Q


    def info(self, c, min_q, max_q):

        print('N(s, o)', self.N)
        print('Q(s, o)', self.Q)
        print('U(s, o)', self.ucb(c, min_q, max_q, verbose=True))

        #print('R(s, o)', self.R)
        #print('S(s, o)', self.S)




