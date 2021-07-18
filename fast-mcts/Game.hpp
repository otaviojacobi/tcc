#pragma once

#include <cstdint>
#include <vector>
#include <torch/torch.h>

class Game
{
public:
    virtual void                play(int8_t move)  = 0;
    virtual std::vector<int8_t>   moves(void)  const = 0;
    virtual int8_t              score(void)        = 0;
    virtual torch::Tensor       state(void)  const = 0;
    virtual void                render(void) const = 0;
};
