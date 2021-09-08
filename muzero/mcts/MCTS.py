from .utils import Node

import numpy as np

class MCTS:

    def __init__(self, s0, pred_model, dyn_model, options, c1=1.25, c2=19652):
        self.root = Node(s0, pred_model, dyn_model, options)
        self.root.expand()

        self.pred_model = pred_model
        self.dyn_model = dyn_model
        self.options = options

        self.c1 = c1
        self.c2 = c2

        self.min_q = np.inf
        self.max_q = -np.inf

    def run_sim(self, sims):
        for sim in range(sims):
            s_prev, o, edge, l, rewards = self.search()

            s, r = self.dyn_model.forward(s_prev, o)
            edge.R[(s_prev, o)] = r
            edge.S[(s_prev, o)] = s

            rewards.append(r)

            new_node, vl = edge.expand(s, self.pred_model, self.dyn_model, self.options)

            min_q, max_q = new_node.backup(l, vl, rewards)

            if min_q < self.min_q:
                self.min_q = min_q

            if max_q > self.max_q:
                self.max_q = max_q

        pi = []
        for option in self.options:
            pi.append(self.root.child_edges[option].N)

        #TODO: should we use this or logits ?
        return np.array(pi) / sum(pi)

    def search(self):

        cur_node = self.root
        l = 0
        rewards = []

        while cur_node.expanded and not cur_node.is_leaf:
            l += 1
            option = cur_node.get_highest_ucb_option(self.c1, self.c2, self.min_q, self.max_q)
            if cur_node.child_edges[option].child_node == None:
                return cur_node.s, option, cur_node.child_edges[option], l, rewards
            else:
                r = cur_node.child_edges[option].R[(cur_node.s, option)]
                rewards.append(r)

            cur_node = cur_node.child_edges[option].child_node

    def info(self):
        self.root.info(self.c1, self.c2, self.min_q, self.max_q)


    def run_time(self, time_limit):
        pass