#pragma once

#include <cstdint>
#include <iostream>
#include <cmath>
#include <tuple>
#include <stack>
#include <map>

#include <torch/torch.h>

#include "Game.hpp"
#include "AlphaNet.hpp"

#define SIMULATED_MCTS 0
#define ALPHA_MCTS     1

#define SPiZTuple std::tuple<torch::Tensor, torch::Tensor, double>

class Node;

class Edge {
public:
    Edge(double prior, Node *parentNode, Node *childNode);
    void clear();
    Node* getParent() const;
    Node* getChild() const;
    void update(double value);
    double getCount() const;
    double getActionValue() const;
    double ucb(double c) const;
    void info() const;

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
    Node(Game *board, std::shared_ptr<AlphaNet> net);


    ~Node();
    double getTotalCount() const;
    bool isExpanded() const;
    bool isLeaf() const;
    
    void setParentEdge(Edge *newParentEdge);
    Edge* getParentEdge() const;

    std::map<int8_t, Edge*>* getChildEdges();

    void incrementCounter();

    Node* getHighestUCBChild() const;

    double expand();
    void backprop(double value);

    std::tuple<torch::Tensor, torch::Tensor> getStatePi(double T) const;
    int8_t getMostVisitedChild() const;

    void info() const;

    Game* getBoard() const;

    uint8_t getExecutionType() const;

private:
    Game* _board;
    Edge* _parentEdge;
    std::map<int8_t, Edge*> _childEdges;

    std::vector<int8_t> _moves;

    bool _isLeaf;
    bool _isExpanded;

    uint16_t _edgeCountSum;

    torch::Tensor _state;
    torch::Tensor _statePriors;
    double _stateValue;

    uint8_t _executionType;

    std::shared_ptr<AlphaNet>_net;

    void evaluatePV();
    double runRandomSimulation();

    double evaluateBySimulations();
    double evaluateByNeuralNet();
};


class MCTS {
public:
    MCTS(Game *board);
    MCTS(Game *board, std::shared_ptr<AlphaNet> net);

    ~MCTS();

    std::tuple<torch::Tensor, torch::Tensor> run(uint16_t simulations, double T);
    int8_t run(uint16_t simulations);

    void setNewHead(int8_t move);

private:
    Node* _root;
    Node* search();

    std::shared_ptr<AlphaNet> _net;
};