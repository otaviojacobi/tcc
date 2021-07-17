# distutils: language = c++
# cython: language_level=3
from othello_cython import Othello, move_to_action

from libc.math cimport sqrt, log
from libc.stdlib cimport rand

from random import choices
import numpy as np

import torch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


cdef class Edge:
    cdef double prior
    cdef int count
    cdef double action_value
    cdef double value_sum

    cdef object child_node
    cdef object parent_node

    def __init__(self, double prior, object child_node, object parent_node):
        self.prior = prior
        self.count = 0
        self.action_value = 0
        self.value_sum = 0

        self.child_node = child_node
        self.parent_node = parent_node

    cpdef object get_parent_node(self):
        return self.parent_node

    cpdef object get_child_node(self):
        return self.child_node

    cpdef void update_edge_value(self, double value):
        self.count += 1
        self.value_sum += value

        self.action_value = self.value_sum / self.count

    cpdef object get_count(self):
        return self.count

    cpdef double get_action_value(self):
        return self.action_value

    cpdef double ucb(self, double c = 2):
        total_count = self.parent_node.get_total_count()
        return self.action_value + c * (self.prior * sqrt(total_count) / (1 + self.count))

    cpdef void free_all(self):
        cdef object root = self.child_node
        cdef list stack = list()
        cdef object node_to_dealloc

        while root != None or len(stack) > 0:
            if root != None:
                stack.append(root)

                if len(root.get_edges()) == 0:
                    root = None
                else:
                    next_key = sorted(root.get_edges().keys())[0]
                    root = root.get_edges()[next_key].get_child_node()

                continue

            node_to_dealloc = stack.pop()
            node_to_dealloc.delloc()
            if node_to_dealloc.get_parent_edge() != self:
                node_to_dealloc.free_parent()
            del node_to_dealloc

            while len(stack) > 0 and len(stack[-1].get_edges()) == 0:

                node_to_dealloc = stack.pop()
                node_to_dealloc.delloc()
                if node_to_dealloc.get_parent_edge() != self:
                    node_to_dealloc.free_parent()
                del node_to_dealloc


            
            if len(stack) > 0:
                root = stack.pop()

    def info(self):
        print('prior', self.prior)
        print('Q(s,a)', self.action_value)
        print('N(s,a)', self.count)
        print('UCB', self.ucb())

cdef class Node:
    cdef object state
    cdef object parent_edge
    cdef dict edges
    
    cdef bint is_leaf
    cdef bint is_expanded

    cdef object net

    def __init__(self, object board, object net):
        self.state = board
        self.parent_edge = None
        self.net = net

        self.edges = dict()

        self.is_expanded = False
        self.is_leaf = len(board.legal_moves()) == 0

    cpdef void delloc(self):
        if not self.parent_edge:
            return

        parent_node = self.parent_edge.get_parent_node()
        edges = parent_node.get_edges()
        edge_to_clear = sorted(edges.keys())[0]
        parent_node.clear_edge(edge_to_clear)


    cpdef void clear_edge(self, char edge_to_clear):
        del self.edges[edge_to_clear]

    cpdef bint get_is_expanded(self):
        return self.is_expanded

    cpdef bint get_is_leaf(self):
        return self.is_leaf

    cpdef void set_parent_edge(self, object edge):
        self.parent_edge = edge

    cpdef object get_parent_edge(self):
        return self.parent_edge

    cpdef dict get_edges(self):
        return self.edges

    cpdef void free_parent(self):
        pass
        #del self.parent_edge

    cpdef object get_highest_ucb_child(self):
        cdef double hi = -100.0

        cdef double ucb
        cdef object best_edge

        for edge in self.edges.values():
            ucb = edge.ucb()
            if ucb > hi:
                hi = ucb
                best_edge = edge

        return best_edge.get_child_node()

    #TODO: this can be optimizing by also adding total visits to the node 
    # so we don't have to loop for all the edges every time
    cpdef int get_total_count(self):
        cdef int total = 0
        for edge in self.edges.values():
            total += edge.get_count()
        return total

    def get_s_pi_z(self, double T):
        cdef list legal_moves = self.state.legal_moves()
        cdef list move_probs = list()
        cdef double total_prob = 0
        cdef double z = 0
        cdef double prob

        cdef double temperature = 1 / T

        cdef action

        for move in legal_moves:
            prob = self.edges[move].get_count() ** temperature
            total_prob += prob
            move_probs.append((move, prob))

        # TODO: assuming V(s) = Σ π(a) * Q(s, a) 
        pi = np.zeros(64)
        for (move, prob) in move_probs:
            action = move_to_action(move)
            pi[action] = prob/total_prob
            z += pi[action] * self.edges[move].get_action_value()

        if z >= 0:
            z = 1.0
        else:
            z = -1.0

        s = self.state.get_board_2d()

        return (s, pi, z)

    def get_p_v(self):
        board = self.state.get_board_2d()
        state_input = torch.from_numpy(board).unsqueeze(0).to(device, dtype=torch.float)

        p, v = self.net(state_input)

        return p.detach().cpu().numpy()[0], v.item()

    cpdef double expand(self, bint should_add_noise = False):

        p, v = self.get_p_v()

        if should_add_noise:
            p = 0.75 * p + 0.25 * (np.random.dirichlet([.03] * len(p)))

        legal_moves = self.state.legal_moves()

        for move in legal_moves:
            new_state = self.state.copy()
            new_state.play(move)

            new_node = Node(new_state, self.net)

            # Next lines do two way binding between new_node <-> edge <-> child_node
            #TODO: self.edges[moves].prior won't sum 1 bcs priors are distributed over non legal moves too... is this an issue ?
            new_edge = Edge(p[move_to_action(move)], new_node, self)
            new_node.set_parent_edge(new_edge)
            self.edges[move] = new_edge

        self.is_expanded = True

        return v

    cpdef void backprop(self, double value):
        cpdef object cur_edge = self.parent_edge
        while cur_edge is not None:
            value = -1 * value 
            cur_edge.update_edge_value(value)
            cur_edge = cur_edge.get_parent_node().get_parent_edge()

    def info(self):

        if len(self.edges) == 0:
            print('Node not expanded')

        for (move, edge) in self.edges.items():
            print('move:', move)
            edge.info()


cdef class MCTS:

    cdef object root

    def __init__(self, object board, object net):
        self.root = Node(board.copy(), net)

    def run(self, unsigned int simulations, double T):
        cdef object node
        cdef double value
        cdef bint current_player_won

        for sim in range(simulations):

            node = self.search()
            value = node.expand(sim==0)
            node.backprop(value)

        return self.root.get_s_pi_z(T)

    cpdef object search(self):
        cdef object cur_node = self.root

        while cur_node.get_is_expanded() and not cur_node.get_is_leaf():
            cur_node = cur_node.get_highest_ucb_child()
        
        return cur_node

    cpdef void set_new_head(self, char move):
        edge = self.root.get_edges()[move]

        for m in list(self.root.get_edges().keys()):
            if m != move:
                self.root.get_edges()[m].free_all()


        self.root = edge.get_child_node()
        del edge
    
    cpdef void info(self):
        self.root.info()



