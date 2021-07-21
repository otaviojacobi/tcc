#pragma once

#include <torch/torch.h>
using namespace torch;
namespace F = torch::nn::functional;

#define CONVOLUTIONAL_FILTERS 64

struct ConvolutionalBlock : nn::Module {
    ConvolutionalBlock(int64_t features);
    Tensor forward(Tensor x);
    
    nn::Conv2d conv;
    nn::BatchNorm2d bn;
};

struct ResidualBlock : nn::Module {
    ResidualBlock(int64_t blocks);
    Tensor forward(Tensor x);

    nn::ModuleList blocks;
    int64_t _amountBlocks;
};


struct PolicyHead : nn::Module {
    PolicyHead(int64_t actionSpace);
    Tensor forward(Tensor x);

    nn::Conv2d conv;
    nn::BatchNorm2d bn;
    nn::Linear fc;
    int64_t _actionSpace;

};

struct ValueHead : nn::Module {
    ValueHead(int64_t actionSpace);
    Tensor forward(Tensor x);

    nn::Conv2d conv;
    nn::BatchNorm2d bn;
    nn::Linear fc1;
    nn::Linear fc2;

    int64_t _actionSpace;

};


struct AlphaNet : nn::Module {
    AlphaNet(int64_t inputFeatures, int64_t residualBlocks, int64_t actionSpace);
    std::pair<Tensor, Tensor> forward(Tensor x);

    std::shared_ptr<ConvolutionalBlock> convBlock;
    std::shared_ptr<ResidualBlock> residualBlock;
    std::shared_ptr<PolicyHead> policyHead;
    std::shared_ptr<ValueHead> valueHead;
};
