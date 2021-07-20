#include "AlphaNet.hpp"

ConvolutionalBlock::ConvolutionalBlock(int64_t features) :
    conv(register_module("conv", nn::Conv2d(nn::Conv2dOptions(features, CONVOLUTIONAL_FILTERS, 3).padding(1)))),
    bn(register_module("bn", nn::BatchNorm2d(nn::BatchNorm2d(CONVOLUTIONAL_FILTERS))))
    {}

Tensor ConvolutionalBlock::forward(Tensor x) {
    return F::relu(bn(conv(x)));
}


ResidualBlock::ResidualBlock(int64_t amountBlocks) : blocks() {
    this->_amountBlocks = amountBlocks;
    for(int64_t i = 0; i < this->_amountBlocks; i++) {
        blocks->push_back(nn::Conv2d(nn::Conv2dOptions(CONVOLUTIONAL_FILTERS, CONVOLUTIONAL_FILTERS, 3).padding(1)));
        blocks->push_back(nn::BatchNorm2d(nn::BatchNorm2d(CONVOLUTIONAL_FILTERS)));
        blocks->push_back(nn::ReLU(nn::ReLUOptions().inplace(true)));
        blocks->push_back(nn::Conv2d(nn::Conv2dOptions(CONVOLUTIONAL_FILTERS, CONVOLUTIONAL_FILTERS, 3).padding(1)));
        blocks->push_back(nn::BatchNorm2d(nn::BatchNorm2d(CONVOLUTIONAL_FILTERS)));
    }
    register_module("blocks", blocks);
}
Tensor ResidualBlock::forward(Tensor x) {

    auto out = x.clone();

    for(int64_t i = 0; i < this->_amountBlocks ; i++) {
        out = blocks[i*5]->as<nn::Conv2d>()->forward(out);
        out = blocks[(i*5) + 1]->as<nn::BatchNorm2d>()->forward(out);
        out = blocks[(i*5) + 2]->as<nn::ReLU>()->forward(out);
        out = blocks[(i*5) + 3]->as<nn::Conv2d>()->forward(out);
        out = blocks[(i*5) + 4]->as<nn::BatchNorm2d>()->forward(out);

        out.add_(x);
        out = F::relu(out, F::ReLUFuncOptions().inplace(true));
    }
    return out;
}

/*
AlphaNet::AlphaNet(){}
Tensor AlphaNet::forward(Tensor x) {
    return x;
}
*/