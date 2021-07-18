#include <cmath>

#include "MCTS.hpp"


Node::Node() {}

double Node::getTotalCount() const {
  return 1.2;
}

Edge::Edge(double prior, Node *parentNode, Node *childNode) {
    this->_prior = prior;
    this->_valueSum = 0;
    this->_actionValue = 0;
    this->_count = 0;

    this->_parentNode = parentNode;
    this->_childNode = childNode;
}

Node* Edge::getParent(void) const {
  return this->_parentNode;
}

Node* Edge::getChild(void) const {
  return this->_childNode;
}

void Edge::update(double value) {
  this->_count++;
  this->_valueSum += value;

  this->_actionValue = this->_valueSum / this->_count;
}

double Edge::getCount(void) const {
  return this->_count;
}

double Edge::getActionValue(void) const {
  return this->_actionValue;
}

double Edge::ucb(double cputc) const {
  double totalCount = this->_parentNode->getTotalCount();
  double explorationTerm = (this->_prior * sqrt(totalCount)) / (1 + this->_count); // U(s, a)
  return this->_actionValue + cputc * explorationTerm;
}