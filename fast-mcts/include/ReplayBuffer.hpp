#pragma once

#include <cmath>
#include <torch/torch.h>
#include <boost/circular_buffer.hpp>

#include "MCTS.hpp"


class ReplayBuffer {
public:
    ReplayBuffer(uint64_t maxlen);
    ~ReplayBuffer();

    void push(std::shared_ptr<SPiZTuple> element);
    std::tuple<torch::Tensor, torch::Tensor, torch::Tensor> sample(long size);

    uint64_t getCurSize();

private:
    boost::circular_buffer<std::shared_ptr<SPiZTuple>> memory;
    uint64_t _maxlen;
    uint64_t _curlen;

};