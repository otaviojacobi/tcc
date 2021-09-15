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
            s_prev, o, edge, rewards = self.search()

            #print('will expand option', o)

            #print(s_prev, o, edge, rewards)

            s, rs = self.dyn_model.forward(s_prev, o)
            edge.R[(s_prev, o)] = rs
            edge.S[(s_prev, o)] = s

            #print(s_prev, s)

            rewards.append(rs)
            new_node, vl = edge.expand(s, self.pred_model, self.dyn_model, self.options)

            #print('rewards', rewards)
            #print('vl', vl)

            min_q, max_q = new_node.backup(vl, rewards)

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
            option = cur_node.get_highest_ucb_option(self.c1, self.c2, self.min_q, self.max_q)
            if cur_node.child_edges[option].child_node == None:
                return cur_node.s, option, cur_node.child_edges[option], rewards
            else:
                rs = cur_node.child_edges[option].R[(cur_node.s, option)]
                rewards.append(rs)

            cur_node = cur_node.child_edges[option].child_node

    def info(self):
        self.root.info(self.c1, self.c2, self.min_q, self.max_q)


    def run_time(self, time_limit):
        pass