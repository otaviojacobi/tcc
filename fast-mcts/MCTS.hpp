#pragma once

#include <cstdint>
#include <iostream>
#include <cmath>
#include <tuple>

#include <torch/torch.h>

#include "Game.hpp"

class Node;

class Edge {
public:
    Edge(double prior, Node *parentNode, Node *childNode);
    Node* getParent() const;
    Node* getChild() const;
    void update(double value);
    double getCount() const;
    double getActionValue() const;
    double ucb(double c) const;

private:
    double _prior;            // P(s, a)
    double _valueSum;         // W(s, a)
    double _actionValue;      // Q(s, a) = W(s, a) / N(s, a)
    uint16_t _count;          // N(s, a)

    Node* _parentNode;
    Node* _childNode;
};

class Node {
public:
    Node(Game *board);
    double getTotalCount() const;
    bool isExpanded() const;
    bool isLeaf() const;
    
    void setParentEdge(Edge *newParentEdge);
    Edge* getParentEdge() const;

    std::unordered_map<int8_t, Edge*>* getChildEdges();

    void incrementCounter();

    Node* getHighestUCBChild() const;

    double expand();
    void backprop(double value);

    std::tuple<torch::Tensor, torch::Tensor, double> getStatePiZ(double T) const;


private:
    Game* _board;
    Edge* _parentEdge;
    std::unordered_map<int8_t, Edge*> _childEdges;

    std::vector<int8_t> _moves;


    bool _isLeaf;
    bool _isExpanded;

    uint16_t _edgeCountSum;          // Minor optimization for UCB calculation

    torch::Tensor _state;
    torch::Tensor _statePriors;
    double _stateValue;

    void evaluate_p_v();
};


class MCTS {
public:
    MCTS(Game *board);
    std::tuple<torch::Tensor, torch::Tensor, double> run(uint16_t simulations, double T);
    void setNewHead(int8_t move);

private:
    Node* _root;
    Node *search();
};