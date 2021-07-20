#include "MCTS.hpp"

MCTS::MCTS(Game *board) {
    this->_root = new Node(board->copy());
}

MCTS::~MCTS() {

    auto edges = this->_root->getChildEdges();
    std::vector<int8_t> keys;
    keys.reserve(edges->size());

    for(auto &edge : *edges) {
        keys.push_back(edge.first);
    }

    for(auto &key : keys) {
        edges->at(key)->clear();
    }

    delete this->_root;
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

int8_t MCTS::run(uint16_t simulations) {
    Node* node;
    double value;

    for(uint16_t i = 0; i < simulations; i++) {
        node = this->search();
        value = node->expand();
        node->backprop(value);
        //this->_root->info();
    }

    return this->_root->getMostVisitedChild();
}

void MCTS::setNewHead(int8_t move) {

    auto edges = this->_root->getChildEdges();
    std::vector<int8_t> keys;
    keys.reserve(edges->size());
    Node *nextHead;

    bool hasNextHead = edges->contains(move);

    if(hasNextHead) {
        nextHead = edges->at(move)->getChild();;
        edges->erase(move);
    }

    for(auto &edge : *edges) {
        if(edge.first != move) {
            keys.push_back(edge.first);
        }
    }

    for(auto &key : keys) {
        edges->at(key)->clear();
        edges->erase(key);
    }
    if(hasNextHead) {
        this->_root = nextHead;
        delete nextHead->getParentEdge()->getParent();
        delete nextHead->getParentEdge();
        this->_root->setParentEdge(NULL);
    } else {
        auto newBoard = this->_root->getBoard()->copy();
        newBoard->play(move);
        nextHead = new Node(newBoard);
        delete this->_root;
        this->_root = nextHead;
    }

}

Node* MCTS::search(void) {
    Node* curNode = this->_root;

    while (curNode->isExpanded() && !curNode->isLeaf()) {
        curNode = curNode->getHighestUCBChild();
    }

    return curNode;
}
