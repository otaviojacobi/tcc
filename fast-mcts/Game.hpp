#pragma once

#include <cstdint>
#include <vector>
#include <torch/torch.h>

class Game
{
public:
    virtual void                play(int8_t move)                 = 0;
    virtual std::vector<int8_t> moves()                     const = 0;
    virtual int8_t              score()                           = 0;
    virtual torch::Tensor       state()                     const = 0;
    virtual void                render()                    const = 0;
    virtual Game*               copy()                            = 0;
    virtual int8_t              moveToAction(int8_t move)   const = 0;
    virtual int8_t              actionToMove(int8_t action) const = 0;

};
