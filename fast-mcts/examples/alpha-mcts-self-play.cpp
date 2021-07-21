#include <torch/torch.h>
#include <iostream>
#include <chrono>
#include <vector>

#include <cstdlib>

#include "AlphaNet.hpp"
#include "Othello.hpp"
#include "MCTS.hpp"
#include "ReplayBuffer.hpp"

#define FEATURES 3
#define AMT_RESIDUAL_BLOCKS 9
#define ACTION_SPACE 64
#define BATCH_SIZE 128
#define LEARNING_RATE 2e-4
#define L2_TERM 1e-4
#define TOTAL_TRAINING_ITERATIONS 50

void runSimulations(std::shared_ptr<AlphaNet> net, std::shared_ptr<ReplayBuffer> buffer, uint64_t iterations) {

    std::vector<int8_t> possibleMoves;

    torch::Tensor pi;
    int8_t action;
    int8_t move;

    for(uint64_t simulationIteration = 0; simulationIteration < iterations; simulationIteration++) {
        Game *env = new Othello();
        MCTS *mcts = new MCTS(env, net);
        while(true) {
            possibleMoves = env->moves();

            if(possibleMoves.empty()) break;

            auto SPiZ = mcts->run(5, 1.0);
            pi = std::get<1>(SPiZ);

            buffer->push(std::make_shared<SPiZTuple>(SPiZ));

            action = torch::multinomial(pi, 1).item<int8_t>();
            move = env->actionToMove(action);

            env->play(move);

            mcts->setNewHead(move);
        }

        std::printf(
        "[SIMULATOR][%2ld/%2ld]\n",
        simulationIteration,
        iterations);

        delete mcts;
        delete env;
    }
}

torch::Tensor alpha_loss(torch::Tensor p, torch::Tensor v, torch::Tensor pi, torch::Tensor z) {
    auto valueError = (z - v).pow(2);
    auto logSoftMaxP = F::log_softmax(p, F::LogSoftmaxFuncOptions(-1));
    auto policyError = (pi * logSoftMaxP).sum(1);
    return (valueError - policyError).mean();
}

void runTraining(std::shared_ptr<AlphaNet> net, std::shared_ptr<ReplayBuffer> buffer, torch::Device trainingDevice, uint64_t totalIterations) {
    net->to(trainingDevice);
    torch::optim::Adam optimizer(net->parameters(), torch::optim::AdamOptions(LEARNING_RATE).weight_decay(L2_TERM));

    for(uint64_t trainingIteration = 0; trainingIteration < totalIterations; trainingIteration++) {

        // TODO, sample directly from device
        auto SPiZ = buffer->sample(BATCH_SIZE);

        auto S = std::get<0>(SPiZ);
        auto Pi = std::get<1>(SPiZ);
        auto Z = std::get<2>(SPiZ);

        S=S.to(trainingDevice);
        Pi=Pi.to(trainingDevice);
        Z=Z.to(trainingDevice);

        auto PV = net->forward(S);

        auto P = std::get<0>(PV);
        auto V = std::get<1>(PV);

        P=P.to(trainingDevice);
        V=V.to(trainingDevice);

        auto loss = alpha_loss(P, V, Pi, Z);

        optimizer.zero_grad();
        loss.backward();
        optimizer.step();

        std::printf(
        "[TRAINER][%2ld/%2ld] loss: %.4f\n",
        trainingIteration,
        totalIterations,
        loss.item<float>());
    }
}

int main() {

    auto inferenceNet = std::make_shared<AlphaNet>(FEATURES, AMT_RESIDUAL_BLOCKS, ACTION_SPACE);
    auto trainingNet = std::make_shared<AlphaNet>(FEATURES, AMT_RESIDUAL_BLOCKS, ACTION_SPACE);

    auto buffer = std::make_shared<ReplayBuffer>(100000);

    torch::Device trainingDevice(torch::kCUDA);

    torch::Device cpuDevice(torch::kCPU);


    for(uint32_t epoch = 0; epoch < 10; epoch++) {
        runSimulations(inferenceNet, buffer, 10);
        runTraining(trainingNet, buffer, trainingDevice, 50);

        trainingNet->to(cpuDevice);

        torch::save(trainingNet, "tmp.pt");
        torch::load(inferenceNet, "tmp.pt");
    }
}
