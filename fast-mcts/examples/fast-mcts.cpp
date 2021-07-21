#include <torch/torch.h>
#include <iostream>
#include <chrono>
#include <vector>

#include <cstdlib>

#include "AlphaNet.hpp"
#include "Othello.hpp"
#include "MCTS.hpp"


int main() {

    auto features = 3;
    auto amtResidualBlocks = 9;
    auto actionSpace = 64;


    auto net = AlphaNet(features, amtResidualBlocks, actionSpace);
    
    Game *othello = new Othello();
    MCTS *mcts = new MCTS(othello, net);

    auto out = mcts->run(100, 1.0);

    std::cout << "s" << std::endl;
    std::cout << std::get<0>(out) << std::endl;
    std::cout << "pi" << std::endl;
    std::cout << std::get<1>(out) << std::endl;
    std::cout << "z" << std::endl;
    std::cout << std::get<2>(out) << std::endl;



    delete othello;
    delete mcts;    
}
