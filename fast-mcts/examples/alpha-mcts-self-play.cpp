#include <torch/torch.h>
#include <iostream>
#include <chrono>
#include <vector>

#include <cstdlib>

#include "AlphaNet.hpp"
#include "Othello.hpp"
#include "MCTS.hpp"
#include "ReplayBuffer.hpp"


int main() {

    auto features = 3;
    auto amtResidualBlocks = 9;
    auto actionSpace = 64;

    auto net = std::make_shared<AlphaNet>(features, amtResidualBlocks, actionSpace);
    std::vector<int8_t> possibleMoves;

    torch::Tensor pi;
    int8_t action;
    int8_t move;

    auto buffer = std::make_shared<ReplayBuffer>(50000);

    std::chrono::steady_clock::time_point begin = std::chrono::steady_clock::now();
    Game *env = new Othello();
    MCTS *mcts = new MCTS(env, net);
    while(true) {
        possibleMoves = env->moves();

        if(possibleMoves.empty()) break;

        auto SPiZ = mcts->run(100, 1.0);
        pi = std::get<1>(SPiZ);

        buffer->push(std::make_shared<SPiZTuple>(SPiZ));

        action = torch::multinomial(pi, 1).item<int8_t>();
        move = env->actionToMove(action);

        env->play(move);

        mcts->setNewHead(move);
    }
    std::chrono::steady_clock::time_point end = std::chrono::steady_clock::now();

    std::cout << "Time difference = " << std::chrono::duration_cast<std::chrono::milliseconds>(end - begin).count()/1000.0 << "[s]" << std::endl;


    env->render();

    delete mcts;
    delete env;
}
