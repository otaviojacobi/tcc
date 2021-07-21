#include "ReplayBuffer.hpp"

ReplayBuffer::ReplayBuffer(uint64_t maxlen) : memory(maxlen){}

ReplayBuffer::~ReplayBuffer() {}

void ReplayBuffer::push(std::shared_ptr<SPiZTuple> element) {
    memory.push_back(element);
}

std::pair<torch::Tensor, torch::Tensor> ReplayBuffer::sample(uint64_t size) {}
