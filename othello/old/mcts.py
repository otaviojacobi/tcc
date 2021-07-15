from othello_numba import BLACK, Othello, WHITE
import numpy as np
from random import choice


class Node:
    def __init__(self, board, parent=None):
        self.state = board

        self.won = 0.
        self.visits = 0.
        self.parent = parent

        self.children = {move: None for move in board.legal_moves()}

    def is_fully_expanded(self):
        return not None in self.children.values()

    def is_leaf(self):
        return len(self.children.keys()) == 0

    def ucb(self, c=2):
        return (self.won / self.visits) + c * np.sqrt(2 * np.log(self.parent.visits)/self.visits)

class MCTS:
    def __init__(self, board):
        self.root = Node(board.copy())

    def run(self, simulations):
        for _ in range(simulations):
            node_to_expand = self.search()
            new_expanded_node = self.expand(node_to_expand)
            current_player_won = self.simulate(new_expanded_node)
            self.backprop(new_expanded_node, current_player_won)

        prob_winning = -1
        max_action = None
        for action, node in self.root.children.items():
            if node.won/node.visits > prob_winning:
                prob_winning = node.won/node.visits
                max_action = action

        print(prob_winning)
        return max_action


    def search(self):
        cur_node = self.root

        while cur_node.is_fully_expanded() and not cur_node.is_leaf():
            cur_node = self.get_highest_ucb_child(cur_node)
        
        return cur_node

    def get_highest_ucb_child(self, node):
        hi = -np.inf
        best_child = None
        for child_node in node.children.values():
            ucb = child_node.ucb()
            if ucb > hi:
                hi = ucb
                best_child = child_node

        return best_child

    def expand(self, node):

        if node.is_leaf():
            return node

        action = choice([a for a, n in node.children.items() if n is None])

        new_board = node.state.copy()
        new_board.play(action)

        new_node = Node(new_board, parent=node)

        node.children[action] = new_node

        return new_node

    def simulate(self, node):
        board_copy = node.state.copy()

        legal_moves = board_copy.legal_moves()
        while len(legal_moves) != 0:
            a = choice(legal_moves)
            board_copy.play(a)

            legal_moves = board_copy.legal_moves()

        score = board_copy.score()

        # black wins
        if score > 0.:
            if node.state.player == BLACK:
                return True
            else:
                return False
        # white wins
        else:
            if node.state.player == WHITE:
                return True
            else:
                return False

    def backprop(self, node, won):

        while node is not None:
            node.visits += 1

            if not won:
                node.won += 1

            won = not won
            node = node.parent

# o = Othello.new()
# counter = 0
# while True:

#     # black turn
#     moves = o.legal_moves()
#     if len(moves) == 0:
#         break

#     move = choice(moves)
#     o.play(move)

#     # white turn
#     moves = o.legal_moves()
#     if len(moves) == 0:
#         break

#     m = MCTS(o)
#     a = m.run(100)
#     o.play(a)


# print(o.score())