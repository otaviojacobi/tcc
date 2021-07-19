#include <torch/torch.h>
#include <iostream>
#include <chrono>
#include <vector>

#include <cstdlib>


#include "Othello.hpp"
#include "MCTS.hpp"


int main() {

    Game *othello = new Othello();
    MCTS *mcts = new MCTS(othello);

    std::vector<int8_t> moves;

    torch::Tensor pi;
    int8_t action;
    int8_t move;

    std::chrono::steady_clock::time_point begin = std::chrono::steady_clock::now();
    while(true) {

        moves = othello->moves();

        if(moves.empty()) break;

        auto sPiZ = mcts->run(200, 1.0);
        pi = std::get<1>(sPiZ);

        action = torch::multinomial(pi, 1).item<int8_t>();
        move = othello->actionToMove(action);

        othello->play(move);

        mcts->setNewHead(move);
    }
    std::chrono::steady_clock::time_point end = std::chrono::steady_clock::now();

    std::cout << "Time difference = " << std::chrono::duration_cast<std::chrono::milliseconds>(end - begin).count()/1000.0 << "[s]" << std::endl;


}



