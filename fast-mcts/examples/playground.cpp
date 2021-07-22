#include <torch/torch.h>
#include "ReplayBuffer.hpp"
#include "MCTS.hpp"


torch::Tensor dir_tensor = torch::ones({64}) * 0.3;
int main() {

    auto prior = torch::ones({64});

    prior = 0.75 * prior + 0.25 * torch::_sample_dirichlet(dir_tensor);

    std::cout << prior << std::endl;

}
