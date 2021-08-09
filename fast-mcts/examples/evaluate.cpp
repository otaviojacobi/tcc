#include <torch/torch.h>
#include "ReplayBuffer.hpp"
#include "MCTS.hpp"
#include "Othello.hpp"

#include "AlphaNet.hpp"


int main() {

    srand(time(NULL));

    std::vector<int8_t> possibleMoves;

    torch::Tensor pi;
    int8_t action;
    int8_t move;

    auto net = std::make_shared<LockedNet>(3, 9, 64);
    std::tuple<torch::Tensor, torch::Tensor> SPi;

    torch::load(net, "tmp.pt");

    int blackWon = 0, whiteWon = 0;

    for(int i = 0; i < 100; i++) {
        std::chrono::steady_clock::time_point begin = std::chrono::steady_clock::now();
        Game *env = new Othello();
        MCTS *mcts = new MCTS(env, net);

        uint64_t counter = 0;
        while(true) {
            possibleMoves = env->moves();
            if(possibleMoves.empty()) break;

            SPi = mcts->run(100, 1.0);

            pi = std::get<1>(SPi);

            action = torch::multinomial(pi, 1).item<int8_t>();
            move = env->actionToMove(action);

            env->play(move);
            mcts->setNewHead(move);

            counter++;

            possibleMoves = env->moves();
            if(possibleMoves.empty()) break;

            move = possibleMoves[rand() % possibleMoves.size()];

            env->play(move);
            mcts->setNewHead(move);

            counter++;

        }

        if(env->score() > 0) {
            std::cout << "Winner is BLACK with " << (int) env->score() << std::endl;
            blackWon++;
        } else {
            std::cout << "Winner is WHITE with " << (int)env->score() << std::endl;
            whiteWon++;
        }

        delete mcts;
        delete env;
    }
    std::cout << "BLACK [" << blackWon << "] WHITE [" << whiteWon << "]" << std::endl;
}