#pragma once

#include <cstdint>
#include <iostream>
#include <cmath>

// Just so we compiler is happy and we can have circular dependencies
class Node;

class Edge {

private:
    double _prior;            // P(s, a)
    double _valueSum;         // W(s, a)
    double _actionValue;      // Q(s, a) = W(s, a) / N(s, a)
    uint16_t _count;          // N(s, a)

    Node* _parentNode;
    Node* _childNode;

public:
    Edge(double prior, Node *parentNode, Node *childNode);

    Node* getParent(void) const;
    Node* getChild(void) const;

    void update(double value);

    double getCount(void) const;
    double getActionValue(void) const;

    double ucb(double c) const;

};

class Node {

public:
    Node();
    double getTotalCount() const;
};


class MCTS {};