#include "MCTS.hpp"
#include "Othello.hpp"

uint64_t totalForwards = 0;
double totalTime = 0.0;

torch::Tensor dirichlet_tensor = torch::ones({64}) * 0.3;
Node::Node(Game *board) {
    this->_board = board;
    this->_parentEdge = NULL;
    this->_isExpanded = false;
    this->_moves = board->moves();
    this->_isLeaf = this->_moves.empty(); 
    this->_edgeCountSum = 0;
    this->_executionType = SIMULATED_MCTS;
}

Node::Node(Game *board, std::shared_ptr<LockedNet> net) : _net(net) {
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

double Node::expand(bool shouldAddNoise) {
    if(this->_executionType == ALPHA_MCTS) {
        return this->evaluateByNeuralNet(shouldAddNoise);
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

std::tuple<torch::Tensor, torch::Tensor> Node::getStatePi(double T) const {

    double temperature = 1/T;
    double prob;
    double totalProb = 0.0;

    int8_t action;

    torch::Tensor pi = torch::zeros({64}).detach();

    for (auto &move : this->_moves) {
        prob = pow(this->_childEdges.at(move)->getCount(), temperature);
        totalProb += prob;

        action = this->_board->moveToAction(move);
        pi[action] = prob;
    }

    pi.div_(totalProb);

    return std::make_tuple(this->_state, pi);
}

void Node::evaluatePV(void) {

    //TODO: with no autograd, evaluate neural net
    torch::NoGradGuard no_grad;

    this->_state = this->_board->state().detach().requires_grad_(false);;

    std::chrono::steady_clock::time_point begin = std::chrono::steady_clock::now();;
    auto pv = this->_net->forward(this->_state);
    std::chrono::steady_clock::time_point end = std::chrono::steady_clock::now();;

    totalTime +=  std::chrono::duration_cast<std::chrono::milliseconds>(end - begin).count() / 1000.0;
    totalForwards++;
    
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

double Node::evaluateByNeuralNet(bool shouldAddNoise) {
    this->evaluatePV();

    Game *board;
    Node *newNode;
    Edge *newEdge;

    int8_t action;

    torch::Tensor prior = this->_statePriors;

    if(shouldAddNoise) {
        prior = 0.75 * prior + 0.25 * torch::_sample_dirichlet(dirichlet_tensor);
    }

    for (auto& move : this->_moves) {

        board = this->_board->copy();
        board->play(move);

        action = board->moveToAction(move);
        newNode = new Node(board, this->_net);
        newEdge = new Edge(prior[action].item<double>(), this, newNode);

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

    for(auto &edge : this->_childEdges) {
        auto count = edge.second->getCount();
        if(count > higherCount) {
            mostVisitedMove = edge.first;
            higherCount = count;
        }
    }

    return mostVisitedMove;
}

void Node::info() const {
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

double Node::totalBranches() const {
    if(this->_childEdges.size() == 0) {
        return 1.0;
    }

    double sum = 0;
    for(auto &edge: this->_childEdges) {
        sum += edge.second->getChild()->totalBranches();
    }

    return sum;
}

double Node::totalNodes() const {

    double sum = 1.0;
    for(auto &edge: this->_childEdges) {
        if(edge.second->getChild()->isExpanded()) {
            sum += edge.second->getChild()->totalNodes();
        }
    }
    return sum;
}

double Node::avgForwardTime() const {
    return totalTime/totalForwards;
}
