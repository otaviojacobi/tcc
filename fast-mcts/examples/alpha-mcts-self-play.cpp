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

#define MCTS_RUN_AMT 100

#define REPLAY_BUFFER_SIZE 100000
#define BATCH_SIZE 2048
#define LEARNING_RATE 1e-4
#define L2_TERM 1e-4
#define TOTAL_TRAINING_ITERATIONS 50


void runSimulations(std::shared_ptr<AlphaNet> net, std::shared_ptr<ReplayBuffer> buffer, uint64_t iterations) {

    std::vector<int8_t> possibleMoves;
    std::tuple<torch::Tensor, torch::Tensor> SPiForRun[60];

    torch::Tensor pi;
    int8_t action;
    int8_t move;

    uint64_t totalTuplesAddedToBuffer = 0;

    std::chrono::steady_clock::time_point begin;
    std::chrono::steady_clock::time_point end;


    std::tuple<torch::Tensor, torch::Tensor> SPi;

    for(uint64_t simulationIteration = 0; simulationIteration < iterations; simulationIteration++) {

        begin = std::chrono::steady_clock::now();
        Game *env = new Othello();
        MCTS *mcts = new MCTS(env, net);

        uint64_t counter = 0;
        while(true) {
            possibleMoves = env->moves();

            if(possibleMoves.empty()) break;

            SPi = mcts->run(MCTS_RUN_AMT, 1.0);

            SPiForRun[counter] = SPi;

            pi = std::get<1>(SPi);

            action = torch::multinomial(pi, 1).item<int8_t>();
            move = env->actionToMove(action);

            env->play(move);
            mcts->setNewHead(move);

            counter++;
        }

        double winner = env->score() > 0.0 ? BLACK : WHITE;
        double curPlayer = BLACK; //Othello starts at black

        for(uint64_t i = 0; i < counter; i++) {

            auto S = std::get<0>(SPiForRun[i]);
            auto Pi = std::get<1>(SPiForRun[i]);
            auto Z = winner == curPlayer ? 1.0 : -1.0;

            auto SPiZ = std::make_tuple(S, Pi, Z);
            buffer->push(std::make_shared<SPiZTuple>(SPiZ));
            curPlayer = -1 * curPlayer; // TODO: make game interface provide a oponnent() function or somethhing
        }

        totalTuplesAddedToBuffer += counter;

        end = std::chrono::steady_clock::now();

        std::printf(
        "[SIMULATOR][%2ld/%2ld] new %2ld over(%2ld) sim_time[%lf s]\n",
        simulationIteration,
        iterations,
        counter,
        totalTuplesAddedToBuffer,
        std::chrono::duration_cast<std::chrono::milliseconds>(end - begin).count() / 1000.0
        );

        counter = 0;

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

    if(BATCH_SIZE > buffer->getCurSize()) {
        std::cout << "Batchsize is bigger then current buffer size, run more simulations" << std::endl;
    }

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

    auto buffer = std::make_shared<ReplayBuffer>(REPLAY_BUFFER_SIZE);

    torch::Device cpuDevice(torch::kCPU);
    torch::Device trainingDevice(torch::kCUDA);

    for(uint32_t epoch = 0; epoch < 200; epoch++) {
        runSimulations(inferenceNet, buffer, 20);
        runTraining(trainingNet, buffer, trainingDevice, 100);

        trainingNet->to(cpuDevice);

        torch::save(trainingNet, "tmp.pt");
        torch::load(inferenceNet, "tmp.pt");
    }
}
