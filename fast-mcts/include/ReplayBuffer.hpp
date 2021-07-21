#pragma once

#include "MCTS.hpp"
#include <torch/torch.h>

#include <boost/circular_buffer.hpp>

class ReplayBuffer {
public:
    ReplayBuffer(uint64_t maxlen);
    ~ReplayBuffer();

    void push(std::shared_ptr<SPiZTuple> element);
    std::pair<torch::Tensor, torch::Tensor> sample(uint64_t size);

    boost::circular_buffer<std::shared_ptr<SPiZTuple>> memory;
};