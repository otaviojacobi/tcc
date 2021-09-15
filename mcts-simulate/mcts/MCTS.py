from .utils import Node

import numpy as np

class MCTS:

    def __init__(self, env, options, c = 2):
        self.root = Node(env.copy(), options)
        self.root.expand()

        self.options = options

        self.c = c

        self.min_q = np.inf
        self.max_q = -np.inf

    def run_sim(self, sims):
        for sim in range(sims):
            edge, option, rewards = self.search()
            node, rs = edge.expand(option, self.options)

            rewards.append(rs)

            value = node.simulate()

            min_q, max_q = node.backup(value, rewards)


            if min_q < self.min_q:
                self.min_q = min_q

            if max_q > self.max_q:
                self.max_q = max_q

        pi = []
        for option in self.options:
            if option in self.root.child_edges:
                pi.append(self.root.child_edges[option].N)
            else:
                pi.append(0)

        #TODO: should we use this or logits ?
        #print(pi)
        return np.array(pi) / sum(pi)

    def search(self):

        cur_node = self.root
        rewards = []
        while cur_node.expanded and not cur_node.is_leaf:
            option = cur_node.get_highest_ucb_option(self.c, self.min_q, self.max_q)

            if cur_node.child_edges[option].child_node == None:
                return cur_node.child_edges[option], option, rewards

            rewards.append(cur_node.child_edges[option].rewards)

            cur_node = cur_node.child_edges[option].child_node

    def info(self):
        self.root.info(self.c, self.min_q, self.max_q)

