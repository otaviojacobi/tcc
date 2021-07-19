#include "MCTS.hpp"

Edge::Edge(double prior, Node *parentNode, Node *childNode) {
    this->_prior = prior;
    this->_valueSum = 0;
    this->_actionValue = 0;
    this->_count = 0;

    this->_parentNode = parentNode;
    this->_childNode = childNode;
}

void Edge::clear() {

    std::stack<Node*> theStack;

    Node* curNode = this->_parentNode;
    Node* tmpNode;


    while(curNode != NULL || !theStack.empty()) {
        if(curNode != NULL) {
            theStack.push(curNode);

            if(curNode->getChildEdges()->empty()) {
                curNode = NULL;
            } else {
                curNode = curNode->getChildEdges()->begin()->second->getChild();
            }

            continue;
        }
        tmpNode = theStack.pop();

        auto parentEdges = tmpNode->getParentEdge()->getParent()->getChildEdges();
        parentEdges->erase(parentEdges->begin());

        delete tmpNode->getParentEdge();
        delete tmpNode;

    }

}

Node* Edge::getParent() const {
    return this->_parentNode;
}

Node* Edge::getChild() const {
    return this->_childNode;
}

void Edge::update(double value) {
    this->_count++;
    this->_valueSum += value;

    this->_parentNode->incrementCounter();

    this->_actionValue = this->_valueSum / this->_count;
}

double Edge::getCount() const {
    return this->_count;
}

double Edge::getActionValue() const {
    return this->_actionValue;
}

double Edge::ucb(double cpuct) const {
    double totalCount = this->_parentNode->getTotalCount();
    double explorationTerm = (this->_prior * sqrt(totalCount)) / (1 + this->_count); // U(s, a)
    return this->_actionValue + cpuct * explorationTerm;
}
