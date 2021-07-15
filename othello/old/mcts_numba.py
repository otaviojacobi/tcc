from othello_numba import BLACK, WHITE, Othello
import numpy as np
from random import choice
from numba import int8, uint32, deferred_type, optional, typed, types
from numba.experimental import jitclass
import time

node_type = deferred_type()
children_kv_type = (types.int8, types.pyobject)
nspec = [
    ('won', uint32),
    ('visits', uint32),
    ('state', Othello.class_type.instance_type),
    ('parent', optional(node_type)),
    ('children', types.DictType(*children_kv_type)),
    ('unexpanded', types.ListType(types.int8)),
]
@jitclass(nspec)
class Node(object):
    def __init__(self, board, parent=None):
        self.state = board

        self.won = 0.
        self.visits = 0.
        self.parent = parent

        self.children = typed.Dict.empty(*children_kv_type)
        self.unexpanded = typed.List.empty_list(types.int8)

        for v in board.legal_moves():
            self.unexpanded.append(int8(v))

    def is_fully_expanded(self):
        return len(self.unexpanded) == 0

    def is_leaf(self):
        return self.state.finished()

    def ucb(self, c=2):
        return (self.won / self.visits) + c * np.sqrt(2 * np.log(self.parent.visits)/self.visits)

node_type.define(Node.class_type.instance_type)

o = Othello.new()
n = Node(o)

n.children[int8(3)] = Node(o)

# class MCTS:
#     def __init__(self, board):
#         self.root = Node(board.copy())

#     def run(self, simulations):
#         for _ in range(simulations):
#             node_to_expand = self.search()
#             new_expanded_node = self.expand(node_to_expand)
#             current_player_won = self.simulate(new_expanded_node)
#             self.backprop(new_expanded_node, current_player_won)

#         prob_winning = -1
#         max_action = None
#         for action, node in self.root.children.items():
#             if node.won/node.visits > prob_winning:
#                 prob_winning = node.won/node.visits
#                 max_action = action

#         return max_action


#     def search(self):
#         cur_node = self.root

#         while cur_node.is_fully_expanded() and not cur_node.is_leaf():
#             cur_node = self.get_highest_ucb_child(cur_node)
        
#         return cur_node

#     def get_highest_ucb_child(self, node):
#         hi = -np.inf
#         best_child = None
#         for child_node in node.children.values():
#             node_ucb = child_node.ucb()
#             if node_ucb > hi:
#                 hi = node_ucb
#                 best_child = child_node

#         return best_child

#     def expand(self, node):

#         if node.is_leaf():
#             return node

#         action = choice(node.unexpanded)
#         node.unexpanded.remove(action)

#         new_board = node.state.copy()
#         new_board.play(action)

#         new_node = Node(new_board, parent=node)

#         node.children[int8(action)] = new_node

#         return new_node

#     def simulate(self, node):
#         board_copy = node.state.copy()

#         legal_moves = board_copy.legal_moves()
#         while len(legal_moves) != 0:
#             a = choice(legal_moves)
#             board_copy.play(a)

#             legal_moves = board_copy.legal_moves()

#         score = board_copy.score()

#         # black wins
#         if score > 0.:
#             if node.state.player == BLACK:
#                 return True
#             else:
#                 return False
#         # white wins
#         else:
#             if node.state.player == WHITE:
#                 return True
#             else:
#                 return False

#     def backprop(self, node, won):

#         while node is not None:
#             node.visits += 1

#             if not won:
#                 node.won += 1

#             won = not won
#             node = node.parent

# #compile
# start_time = time.time()
# o = Othello.new()
# moves = o.legal_moves()
# move = choice(moves)
# o.play(move)
# m = MCTS(o)
# a = m.run(3)

# print('Compile time: ', time.time() - start_time)


# #search time
# start_time = time.time()
# m = MCTS(o)
# a = m.run(1000)
# print('Search time: ', time.time() - start_time)
