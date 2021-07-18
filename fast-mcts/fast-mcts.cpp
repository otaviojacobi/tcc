#include <torch/torch.h>
#include <iostream>
#include <chrono>

#include "MCTS.hpp"

int main() {

  Node *n = new Node();
  Node *n2 = new Node();

  Edge e = Edge(3.2, n, n2);

  std::cout << e.ucb(2) << std::endl;
}



