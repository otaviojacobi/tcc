import numpy as np
from random import shuffle
import itertools

class Node:
    def __init__(self, s, pred_model, dyn_model, options=[]):
        self.s = s
        self.pred_model = pred_model
        self.dyn_model = dyn_model

        self.parent_edge = None
        self.all_options = options
        self.valid_options = {o for o in options if o.is_valid(s)}
        self.edge_count_sum = 0
        self.is_leaf = len(self.valid_options) == 0
        self.child_edges = {}
        self.expanded = False

    def get_highest_ucb_option(self, c1, c2, min_q, max_q):

        max_ucb = -np.inf
        best_option = None

        executed = False
        opts = list(self.child_edges.items())
        shuffle(opts)
        for option, edge in opts:
            executed = True
            edge_ucb = edge.ucb(c1, c2, min_q, max_q)
            if edge_ucb >= max_ucb:
                max_ucb = edge_ucb
                best_option = option

        if not executed:
            print('Node returned None best_option: empty child_edges')

        return best_option

    def expand(self):
        self.expanded = True

        #TODO: carefull about order
        #print('expand s', self.s)
        p, v = self.pred_model.forward(self.s)

        for idx, option in enumerate(self.all_options):
            if option in self.valid_options:
                self.child_edges[option] = Edge(p[idx], self, None)

        return v

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

        #print('k', k)

        return min_q, max_q

    def info(self, c1, c2, min_q, max_q):
        print('Expanded: ', self.expanded)
        print('Leaf: ', self.is_leaf)
        print('hidden state', self.s)

        for option, edge in self.child_edges.items():
            print('Option', option)
            edge.info(c1, c2, min_q, max_q)
            #if edge.child_node is not None:
                #edge.child_node.info(c1, c2, min_q, max_q)



class Edge:
    def __init__(self, prior, parent_node, child_node):

        self.N = 0
        self.Q = 0.0

        self.N_real = 0

        self.P = prior
        self.R = {}
        self.S = {}

        self.parent_node = parent_node
        self.child_node = child_node

    def ucb(self, c1, c2, min_q, max_q, verbose=False):

        if min_q != np.inf and max_q != -np.inf and max_q - min_q != 0:
            normalized_Q = (self.Q - min_q) / (max_q - min_q)
        else:
            normalized_Q = self.Q

        N_sum = self.parent_node.edge_count_sum

        uct_exploration = np.sqrt(N_sum) / (1 + self.N)
        prior_regulation = c1 + np.log((N_sum + c2 + 1)/c2)

        if verbose:
            print('Q\'(s, o): ', normalized_Q)
            print('UCT exploration: ', uct_exploration)
            print('Prior regulation: ', prior_regulation)


        return normalized_Q + (self.P * uct_exploration * prior_regulation)

    def expand(self, state, pred_model, dyn_model, options):
        self.child_node = Node(state, pred_model, dyn_model, options)
        self.child_node.parent_edge = self
        v = self.child_node.expand()

        return self.child_node, v

    def update(self, k, l, vl, rewards, depth):
        gamma = 0.99
        G_k = 0

        #print(l, k)
        for t in range(l-k):
            G_k += (gamma ** t) * rewards[k+t]
            #print('k+t', (gamma ** t) * rewards[k+t])


        #print('disc vl', (gamma ** (l-k)) *vl)
        G_k += (gamma ** (l-k)) * vl


        G_k = round(G_k, 10)

        # print('rs', rewards)
        # print('vl', vl)
        # print('G_k', G_k)


        self.Q = ((self.N_real * self.Q) + G_k) / (self.N_real + 1)

        # if self.N == 0:
        #     self.Q = G_k
        # else:
        #     self.Q = max(self.Q, G_k)

        self.N_real += depth

        self.N = self.N + 1
        self.parent_node.edge_count_sum += 1


        # self.N = self.N + step
        # self.parent_node.edge_count_sum += step

        # self.Q = self.Q + ((G_k -self.Q) / (self.N))


        return self.Q


    def info(self, c1, c2, min_q, max_q):

        print('N(s, o)', self.N)
        print('Q(s, o)', self.Q)
        print('P(s, o)', self.P)
        print('U(s, o)', self.ucb(c1, c2, min_q, max_q, verbose=True))

        #print('R(s, o)', self.R)
        #print('S(s, o)', self.S)




