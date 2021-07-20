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

    Node* curNode = this->_childNode;
    Node* tmpNode;

    std::map<int8_t, Edge*>* parentEdges;


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
        tmpNode = theStack.top();
        theStack.pop();

        if (tmpNode->getParentEdge() != NULL) {
            

            parentEdges = tmpNode->getParentEdge()->getParent()->getChildEdges();
            parentEdges->erase(parentEdges->begin());

            delete tmpNode->getParentEdge();
        }

        delete tmpNode;

        while(!theStack.empty() && theStack.top()->getChildEdges()->empty()) {


            tmpNode = theStack.top();
            theStack.pop();

            if (tmpNode->getParentEdge() != NULL) {
                parentEdges = tmpNode->getParentEdge()->getParent()->getChildEdges();
                parentEdges->erase(parentEdges->begin());

                delete tmpNode->getParentEdge();
            }
            delete tmpNode;
        }

        if(!theStack.empty()) {

            curNode = theStack.top();
            theStack.pop();
        }
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

    //double explorationTerm = (this->_prior * sqrt(totalCount)) / (1 + this->_count); // U(s, a)
    double explorationTerm = sqrt(2 * log(totalCount)/(1+this->_count));
    return this->_actionValue + cpuct * explorationTerm;
}

void Edge::info() const {
    std::cout << "P(s, a)" << this->_prior << std::endl;
    std::cout << "Q(s, a)" << this->_actionValue << std::endl; 
    std::cout << "N(s, a)" << this->_count << std::endl; 
    std::cout << "W(s, a)" << this->_valueSum << std::endl; 
    std::cout << "UCB" << this->ucb(10) << std::endl; 

}