#include <torch/torch.h>
#include "ReplayBuffer.hpp"
#include "MCTS.hpp"

int main() {

    auto buffer = std::make_shared<ReplayBuffer>(16);

    for(int i = 0; i < 12; i++) {
        auto tuple = std::make_tuple(torch::ones({1,3,8,8}) * i, torch::ones({64}) * i, 0.7);
        buffer->push(std::make_shared<SPiZTuple>(tuple));
    }

    auto out = buffer->sample(4);

    std::cout << std::get<0>(out)[0] << std::endl;

}
