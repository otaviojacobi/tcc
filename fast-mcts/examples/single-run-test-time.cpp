#include <torch/torch.h>
#include "ReplayBuffer.hpp"
#include "MCTS.hpp"
#include "Othello.hpp"

int main() {
    std::vector<int8_t> possibleMoves;

    torch::Tensor pi;
    int8_t action;
    int8_t move;

    auto net = std::make_shared<AlphaNet>(3, 9, 64);
    std::tuple<torch::Tensor, torch::Tensor> SPi;


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
    }

    std::chrono::steady_clock::time_point end = std::chrono::steady_clock::now();

    std::cout << "Time difference = " << std::chrono::duration_cast<std::chrono::milliseconds>(end - begin).count()/1000.0 << "[s]" << std::endl;

    delete mcts;
    delete env;
}