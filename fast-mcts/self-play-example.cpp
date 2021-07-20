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

    srand(time(NULL));

    std::vector<int8_t> moves;

    torch::Tensor pi;
    int8_t move;    

    while(true) {
        moves = othello->moves();
        if(moves.empty()) break;
        move = mcts->run(200);
        othello->play(move);
        mcts->setNewHead(move);
    }

    auto score = othello->score();
    if(score == 0) {
        std::count << "DRAW ! " << (int)score  << std::endl;
    } else if(score > 0) {
        std::count << "BLACK WON ! " << (int)score  << std::endl;
    } else {
        std::count << "WHITE WON ! " << (int)score  << std::endl;
    }

    othello->render();


    delete othello;
    delete mcts;
}
