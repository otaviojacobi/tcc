#include <torch/torch.h>
#include <iostream>
#include <chrono>
#include <vector>

#include <cstdlib>

#include "AlphaNet.hpp"

int main() {

    auto convBlock = std::make_shared<ConvolutionalBlock>(3);
    auto resLayer = std::make_shared<ResidualBlock>(9);

    auto x = torch::ones({1, 3, 8, 8});
    auto y = convBlock->forward(x);
    auto z = resLayer->forward(y);

    std::cout << z << std::endl;
}
