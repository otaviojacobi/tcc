/**
 * This is an example of a raw MCTS self-played game,
 * This MCTS do NOT use any Neural Net or function approximation for estimating the value of a node
 * Instead, it is the classic MCTS algorithm where at each node we run a random simulation and
 * see if the agent won or lost from the point onwards.
 * 
 * The main loop is propopsitaly left duplicated in order to check that if we decrease the amount of
 * simulations of one player, the other player will start to win more games.
 * 
 * Notice that because the MCTS class is constructed without a neural network(torch::Net)
 * it defaults to the original MCTS (no NN). And therefore run function should be invoked expecting
 * a single (move) value instead of the <S, pi, Z> tuple of alpha search.
*/

#include <iostream>
#include <vector>
#include <cstdlib>

#include "Othello.hpp"
#include "MCTS.hpp"

int main() {

    srand(time(NULL));

    Game *othello = new Othello();
    MCTS *mcts = new MCTS(othello);

    std::vector<int8_t> moves;
    int8_t move;

    while(true) {

        // Black turn
        moves = othello->moves();
        if(moves.empty()) break;
        move = mcts->run(200);
        othello->play(move);
        mcts->setNewHead(move);

        // White turn
        moves = othello->moves();
        if(moves.empty()) break;
        move = mcts->run(200);
        othello->play(move);
        mcts->setNewHead(move);
    }

    auto score = othello->score();
    if(score == 0) {
        std::cout << "DRAW ! " << (int)score  << std::endl;
    } else if(score > 0) {
        std::cout << "BLACK WON ! " << (int)score  << std::endl;
    } else {
        std::cout << "WHITE WON ! " << (int)score  << std::endl;
    }

    othello->render();

    delete othello;
    delete mcts;
}
