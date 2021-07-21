#include "MCTS.hpp"
#include "Othello.hpp"

auto dummy = AlphaNet(1,1,1);

Node::Node(Game *board) {
    this->_board = board;
    this->_parentEdge = NULL;
    this->_isExpanded = false;
    this->_moves = board->moves();
    this->_isLeaf = this->_moves.empty(); 
    this->_edgeCountSum = 0;
    this->_executionType = SIMULATED_MCTS;
}

Node::Node(Game *board, std::shared_ptr<AlphaNet> net) : _net(net) {
    this->_board = board;
    this->_parentEdge = NULL;
    this->_isExpanded = false;
    this->_moves = board->moves();
    this->_isLeaf = this->_moves.empty(); 
    this->_edgeCountSum = 0;
    this->_executionType = ALPHA_MCTS;
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
    if(this->_executionType == ALPHA_MCTS) {
        return this->evaluateByNeuralNet();
    } else if (this->_executionType == SIMULATED_MCTS) {
        return this->evaluateBySimulations();
    }
    //std::cout << "Tried to expand node with invalid execution type " << this->_executionType << std::endl;
    exit(EXIT_FAILURE);
}
void Node::backprop(double value){
    Edge* curEdge = this->_parentEdge;

    while (curEdge != NULL) {

        if(this->_executionType == ALPHA_MCTS) {
            value = -1 * value;
        } else if(this->_executionType == SIMULATED_MCTS) {
            value = value == 1.0 ? 0.0 : 1.0;
        }
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

void Node::evaluatePV(void) {
    this->_state = this->_board->state();

    //TODO: with no autograd, evaluate neural net
    torch::NoGradGuard no_grad;
    auto pv = this->_net->forward(this->_state);

    this->_statePriors = pv.first[0];
    this->_stateValue = pv.second.item<double>();
}

double Node::evaluateBySimulations() {
    double won = this->runRandomSimulation();

    Game *board;
    Node *newNode;
    Edge *newEdge;

    for (auto& move : this->_moves) {

        board = this->_board->copy();
        board->play(move);

        newNode = new Node(board);
        newEdge = new Edge(0, this, newNode);

        newNode->setParentEdge(newEdge);

        this->_childEdges[move] = newEdge;
    }
    this->_edgeCountSum += 1;
    this->_isExpanded = true;

    return won;
}

double Node::runRandomSimulation() {
    Game *simulationBoard = this->_board->copy();
    auto moves = this->_moves;
    int8_t move;


    //std::cout << "will start random sim" << std::endl;
    while(!moves.empty()) {
        move = moves[rand() % moves.size()];
        simulationBoard->play(move);
        moves = simulationBoard->moves();
    }

    auto score = simulationBoard->score();
    auto player = this->_board->player();

    delete simulationBoard;

    //std::cout << "finished random sim " << (int)score << std::endl;

    // TOOD: remove black and white
    // Black won
    if(score > 0) {
        if(player == BLACK) {
            return 1.0;
        } else {
            return 0.0;
        }
    // White won
    } else {
        if(player == WHITE) {
            return 1.0;
        } else {
            return 0.0;
        }
    }
}

double Node::evaluateByNeuralNet() {
    this->evaluatePV();

    Game *board;
    Node *newNode;
    Edge *newEdge;

    int8_t action;

    for (auto& move : this->_moves) {

        board = this->_board->copy();
        board->play(move);

        action = board->moveToAction(move);
        newNode = new Node(board, this->_net);
        newEdge = new Edge(this->_statePriors[action].item<double>(), this, newNode);

        newNode->setParentEdge(newEdge);

        this->_childEdges[move] = newEdge;
    }
    this->_edgeCountSum += 1;
    this->_isExpanded = true;

    return this->_stateValue;
}

int8_t Node::getMostVisitedChild() const {
    uint8_t mostVisitedMove;
    uint8_t higherCount = 0;

    //std::cout << "I am here" << std::endl; 
    for(auto &edge : this->_childEdges) {
        auto count = edge.second->getCount();
        if(count > higherCount) {
            mostVisitedMove = edge.first;
            higherCount = count;
        }
    }
    //std::cout << "I am there " << (int) mostVisitedMove << std::endl; 

    return mostVisitedMove;
}

void Node::info() const {
    //std::cout << "will display " << this->_childEdges.size() << std::endl;
    for(auto &edge : this->_childEdges) {
        std::cout << (int)edge.first << std::endl;
        edge.second->info();
    }
}

Game* Node::getBoard() const {
    return this->_board;
}

uint8_t Node::getExecutionType() const {
    return this->_executionType;
}
