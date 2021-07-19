#include "MCTS.hpp"

MCTS::MCTS(Game *board) {
    this->_root = new Node(board->copy());
}

std::tuple<torch::Tensor, torch::Tensor, double> MCTS::run(uint16_t simulations, double T) {

    Node* node;
    double value;

    for(uint16_t i = 0; i < simulations; i++) {

        node = this->search();
        value = node->expand();
        node->backprop(value);
    }

    return this->_root->getStatePiZ(T);
}


void MCTS::setNewHead(int8_t move) {
    this->_root = this->_root->getChildEdges()->at(move)->getChild();
}

Node* MCTS::search(void) {
    Node* curNode = this->_root;

    while (curNode->isExpanded() && !curNode->isLeaf()) {
        curNode = curNode->getHighestUCBChild();
    }

    return curNode;
}