
#include <torch/torch.h>
using namespace torch;
namespace F = torch::nn::functional;

#define CONVOLUTIONAL_FILTERS 64

struct ConvolutionalBlock : nn::Module {
public:
    ConvolutionalBlock(int64_t features);
    Tensor forward(Tensor x);
    
    nn::Conv2d conv;
    nn::BatchNorm2d bn;
 
};

class ResidualBlock : nn::Module {
public:
    ResidualBlock(int64_t blocks);
    Tensor forward(Tensor x);

    nn::ModuleList blocks;
    int64_t _amountBlocks;

};

/*
class AlphaNet : nn::Module {
public:
    AlphaNet();
    Tensor forward(Tensor x);
};
*/