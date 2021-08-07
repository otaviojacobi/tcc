#include "AlphaNet.hpp"

ConvolutionalBlock::ConvolutionalBlock(int64_t features) :
    conv(register_module("conv", nn::Conv2d(nn::Conv2dOptions(features, CONVOLUTIONAL_FILTERS, 3).padding(1)))),
    bn(register_module("bn", nn::BatchNorm2d(nn::BatchNorm2dOptions(CONVOLUTIONAL_FILTERS))))
    {}

Tensor ConvolutionalBlock::forward(Tensor x) {
    return F::relu(bn(conv(x)));
}


ResidualBlock::ResidualBlock(int64_t amountBlocks) : blocks() {
    this->_amountBlocks = amountBlocks;
    for(int64_t i = 0; i < this->_amountBlocks; i++) {
        blocks->push_back(nn::Conv2d(nn::Conv2dOptions(CONVOLUTIONAL_FILTERS, CONVOLUTIONAL_FILTERS, 3).padding(1)));
        blocks->push_back(nn::BatchNorm2d(nn::BatchNorm2dOptions(CONVOLUTIONAL_FILTERS)));
        blocks->push_back(nn::ReLU(nn::ReLUOptions().inplace(true)));
        blocks->push_back(nn::Conv2d(nn::Conv2dOptions(CONVOLUTIONAL_FILTERS, CONVOLUTIONAL_FILTERS, 3).padding(1)));
        blocks->push_back(nn::BatchNorm2d(nn::BatchNorm2dOptions(CONVOLUTIONAL_FILTERS)));
    }
    register_module("blocks", blocks);
}
Tensor ResidualBlock::forward(Tensor x) {

    auto out = x.clone();
    out = out.to(x.device());

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

PolicyHead::PolicyHead(int64_t actionSpace) :
    conv(register_module("conv", nn::Conv2d(nn::Conv2dOptions(CONVOLUTIONAL_FILTERS, 2, 1)))),
    bn(register_module("bn", nn::BatchNorm2d(nn::BatchNorm2dOptions(2)))),
    fc(register_module("fc", nn::Linear(2 * actionSpace, actionSpace)))

{
    this->_actionSpace = actionSpace;
}
Tensor PolicyHead::forward(Tensor x)
{
    x = F::relu(bn(conv(x)), F::ReLUFuncOptions().inplace(true));
    x = x.view({-1, 2 * this->_actionSpace});

    return F::softmax(fc(x), F::SoftmaxFuncOptions(1));
}

ValueHead::ValueHead(int64_t actionSpace) :
    conv(register_module("conv", nn::Conv2d(nn::Conv2dOptions(CONVOLUTIONAL_FILTERS, 2, 1)))),
    bn(register_module("bn", nn::BatchNorm2d(nn::BatchNorm2dOptions(2)))),
    fc1(register_module("fc1", nn::Linear(2 * actionSpace, 256))),
    fc2(register_module("fc2", nn::Linear(256, 1)))
{
    this->_actionSpace = actionSpace;
}
Tensor ValueHead::forward(Tensor x) {
    x = F::relu(bn(conv(x)), F::ReLUFuncOptions());
    x = x.view({-1, 2 * this->_actionSpace});
    x = F::relu(fc1(x), F::ReLUFuncOptions().inplace(true));
    return torch::tanh(fc2(x));
}

AlphaNet::AlphaNet(int64_t inputFeatures, int64_t residualBlocks, int64_t actionSpace) :
    convBlock(register_module<ConvolutionalBlock>("convBlock", std::make_shared<ConvolutionalBlock>(inputFeatures))),
    residualBlock(register_module<ResidualBlock>("residualBlock", std::make_shared<ResidualBlock>(residualBlocks))),
    policyHead(register_module<PolicyHead>("policyHead", std::make_shared<PolicyHead>(actionSpace))),
    valueHead(register_module<ValueHead>("valueHead", std::make_shared<ValueHead>(actionSpace)))
{

}
std::pair<Tensor, Tensor> AlphaNet::forward(Tensor x) {
    x = residualBlock->forward(convBlock->forward(x));
    
    Tensor p = policyHead->forward(x);
    Tensor v = valueHead->forward(x);

    return std::make_pair(p, v);
}


LockedNet::LockedNet(int64_t inputFeatures, int64_t residualBlocks, int64_t actionSpace) : 
    net(register_module<AlphaNet>("alphanet", std::make_shared<AlphaNet>(inputFeatures, residualBlocks, actionSpace)))
{}

std::pair<Tensor, Tensor> LockedNet::forward(torch::Tensor x) {
    _netPass.lock();
    auto out = net->forward(x);
    _netPass.unlock();
    return out;
}

void LockedNet::lock() {
    _netPass.lock();
}

void LockedNet::unlock() {
    _netPass.unlock();
}