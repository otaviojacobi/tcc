#include "MCTS.hpp"

Node::Node(Game *board) {
    this->_board = board;
    this->_parentEdge = nullptr;

    this->_isExpanded = false;

    this->_moves = board->moves();

    this->_isLeaf = this->_moves.empty(); 

    this->_edgeCountSum = 0;
}

Node::~Node() {
    delete this->_board;

}

double Node::getTotalCount() const {
    return this->_edgeCountSum;
}

bool Node::isExpanded() const {
    return this->_isExpanded;
}

bool Node::isLeaf() const {
    return this->_isLeaf;
}

void Node::setParentEdge(Edge *newParentEdge) {
    this->_parentEdge = newParentEdge;
}

Edge* Node::getParentEdge() const {
    return this->_parentEdge;
}

std::map<int8_t, Edge*>* Node::getChildEdges() {
    return &this->_childEdges;
}

void Node::incrementCounter() {
    this->_edgeCountSum++;
}

// TODO: maybe we can avoid this loop by using a heap
// Everytime we backprop in the tree each edge traversed updates its ucb value and updates the heap
// So we always keep track of the maximum ucb in first position and this funcion goes from O(n) -> O(1)
Node* Node::getHighestUCBChild() const {
    double highest = -1000.0;
    double ucb = -1000.0;
    Edge* edge;
    Edge* best_edge;

    for (auto& it: this->_childEdges) {

        edge = it.second;
        ucb = edge->ucb(2);

        if (ucb > highest) {
            highest = ucb;
            best_edge = edge;
        }
    }

    return best_edge->getChild();
}

double Node::expand() {

    this->evaluate_p_v();

    Game *board;
    Node *newNode;
    Edge *newEdge;

    int8_t action;

    for (auto& move : this->_moves) {

        board = this->_board->copy();
        board->play(move);

        action = board->moveToAction(move);
        newNode = new Node(board);
        newEdge = new Edge(this->_statePriors[action].item<double>(), this, newNode);

        newNode->setParentEdge(newEdge);

        this->_childEdges[move] = newEdge;
    }

    this->_isExpanded = true;

    return this->_stateValue;
}
void Node::backprop(double value){
    Edge* curEdge = this->_parentEdge;

    while (curEdge != nullptr) {
        value = -1 * value;
        curEdge->update(value);
        curEdge = curEdge->getParent()->getParentEdge();
    }
}

std::tuple<torch::Tensor, torch::Tensor, double> Node::getStatePiZ(double T) const {

    double temperature = 1/T;
    double z = 0;
    double prob;
    double totalProb = 0.0;

    int8_t action;

    torch::Tensor pi = torch::zeros({64});

    for (auto &move : this->_moves) {
        prob = pow(this->_childEdges.at(move)->getCount(), temperature);
        totalProb += prob;

        action = this->_board->moveToAction(move);
        pi[action] = prob;
        z += prob * this->_childEdges.at(move)->getActionValue();
    }

    pi.div_(totalProb);
    z = z / totalProb;

    if(z > 0)
    z = z >= 0 ? 1.0 : -1.0;

    return std::make_tuple(this->_state, pi, z);
}

void Node::evaluate_p_v(void) {
    this->_state = this->_board->state();

    //TODO: with no autograd, evaluate neural net
    torch::Tensor p = torch::ones({64, 1});
    torch::Tensor v = torch::randn({1,1});

    this->_statePriors = p;
    this->_stateValue = v.item<double>();
}