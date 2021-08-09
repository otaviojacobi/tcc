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
#define TOTAL_GAMES 5000

#define REPLAY_BUFFER_SIZE 300000
#define BATCH_SIZE 512
#define LEARNING_RATE 2e-3
#define L2_TERM 1e-4
#define BATCHES_FOR_UPDATE 1000
#define TOTAL_TRAINING_UPDATES 300

#define MCTS_SIMS_THREADS 8

torch::Device trainingDevice(torch::kCUDA);

void runSimulations(std::shared_ptr<LockedNet> net, std::shared_ptr<ReplayBuffer> buffer, int threadId) {

    std::vector<int8_t> possibleMoves;
    std::tuple<torch::Tensor, torch::Tensor> SPiForRun[62];

    torch::Tensor pi;
    int8_t action;
    int8_t move;

    std::chrono::steady_clock::time_point begin;
    std::chrono::steady_clock::time_point end;
    std::chrono::steady_clock::time_point buf;



    std::tuple<torch::Tensor, torch::Tensor> SPi;

    for(uint64_t simulationIteration = 0; simulationIteration < TOTAL_GAMES; simulationIteration++) {

        begin = std::chrono::steady_clock::now();
        Game *env = new Othello();
        MCTS *mcts = new MCTS(env, net);

        uint64_t counter = 0;
        double totalBf = 0.0;
        double T = 1.0;
        while(true) {
            possibleMoves = env->moves();

            if(possibleMoves.empty()) break;

            SPi = mcts->run(MCTS_RUN_AMT, T);

            SPiForRun[counter] = SPi;

            pi = std::get<1>(SPi);

            action = torch::multinomial(pi, 1).item<int8_t>();
            move = env->actionToMove(action);

            env->play(move);
            mcts->setNewHead(move);

            counter++;

            if(counter > 16) {
                T = 0.1;
            }
        }

        end = std::chrono::steady_clock::now();

        double winner = env->score() > 0.0 ? BLACK : WHITE;
        double curPlayer = BLACK; //Othello starts at black

        for(uint64_t i = 0; i < counter; i++) {

            auto S = std::get<0>(SPiForRun[i]).detach().clone();
            auto Pi = std::get<1>(SPiForRun[i]).detach().clone();
            auto Z = winner == curPlayer ? 1.0 : -1.0;

            auto SPiZ = std::make_tuple(S, Pi, Z);
            buffer->push(std::make_shared<SPiZTuple>(SPiZ));
            curPlayer = -1 * curPlayer; // TODO: make game interface provide a oponnent() function or somethhing
        }

        buf = std::chrono::steady_clock::now();

        std::printf(
        "[SIMULATOR %d][%2ld/%2ld] new %2ld over(%2ld) sim_time[%lf s] buf_time[%lf s] avg_forward_time[%lf]\n",
        threadId,
        simulationIteration,
        TOTAL_GAMES,
        counter,
        buffer->getCurSize(),
        std::chrono::duration_cast<std::chrono::milliseconds>(end - begin).count() / 1000.0,
        std::chrono::duration_cast<std::chrono::milliseconds>(buf - end).count() / 1000.0,
        mcts->avgForwardTime()
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

void runTraining(
    std::shared_ptr<LockedNet> trainingNet,
    std::shared_ptr<LockedNet> *simulationNets,
    std::shared_ptr<ReplayBuffer> buffer,
    torch::Device trainingDevice,
    torch::Device simulationDevice) {

    while(BATCH_SIZE > buffer->getCurSize()) {
        std::cout << "[TRAINER] Batchsize[" << BATCH_SIZE << "] is bigger then current buffer size[" << buffer->getCurSize() << "], run more simulations" << std::endl;
        std::this_thread::sleep_for(std::chrono::seconds(10));
    }

    std::cout << "The replay buffer size is " << buffer->getCurSize() << std::endl;

    torch::optim::Adam optimizer(trainingNet->net->parameters(), torch::optim::AdamOptions(LEARNING_RATE).weight_decay(L2_TERM));

    for(uint64_t updateIteration = 0; updateIteration < TOTAL_TRAINING_UPDATES; updateIteration++) {
        trainingNet->to(trainingDevice);
        double totalLossOnUpdate = 0.0;
        for(uint64_t trainingIteration = 0; trainingIteration < BATCHES_FOR_UPDATE; trainingIteration++) {

            // TODO, sample directly from device
            auto SPiZ = buffer->sample(BATCH_SIZE);

            auto S = std::get<0>(SPiZ);
            auto Pi = std::get<1>(SPiZ);
            auto Z = std::get<2>(SPiZ);

            S=S.to(trainingDevice);
            Pi=Pi.to(trainingDevice);
            Z=Z.to(trainingDevice);

            auto PV = trainingNet->forward(S);

            auto P = std::get<0>(PV);
            auto V = std::get<1>(PV);

            P=P.to(trainingDevice);
            V=V.to(trainingDevice);

            auto loss = alpha_loss(P, V, Pi, Z);

            optimizer.zero_grad();
            loss.backward();
            optimizer.step();

            totalLossOnUpdate += loss.item<float>();

            /*
            if(updateIteration >= 0 && updateIteration <= 5 && trainingIteration % 10 == 0) {

                std::printf(
                "[TRAINER] instant loss: %.4f\n",
                loss.item<float>()
                );
            }
            */
        }

        std::printf(
        "[TRAINER][%2ld/%2ld] loss: %.4f\n",
        updateIteration,
        TOTAL_TRAINING_UPDATES,
        totalLossOnUpdate/BATCHES_FOR_UPDATE
        );

        trainingNet->lock();
        trainingNet->to(simulationDevice);
        torch::save(trainingNet, "tmp.pt");
        trainingNet->unlock();

        for(int i = 0; i < MCTS_SIMS_THREADS; i++) {
            simulationNets[i]->lock();
            torch::load(simulationNets[i], "tmp.pt");
            simulationNets[i]->eval();
            simulationNets[i]->unlock();
        }
    }
}


int main() {

    auto buffer = std::make_shared<ReplayBuffer>(REPLAY_BUFFER_SIZE);

    torch::Device simulationDevice(torch::kCPU);

    std::shared_ptr<LockedNet> simulationNets[MCTS_SIMS_THREADS];
    std::thread simulationThreads[MCTS_SIMS_THREADS];

    for(int i = 0; i < MCTS_SIMS_THREADS; i++) {
        simulationNets[i] = std::make_shared<LockedNet>(FEATURES, AMT_RESIDUAL_BLOCKS, ACTION_SPACE);
        simulationNets[i]->eval();
        simulationThreads[i] = std::thread(runSimulations, simulationNets[i], buffer, i);
    }


    auto trainingNet = std::make_shared<LockedNet>(FEATURES, AMT_RESIDUAL_BLOCKS, ACTION_SPACE);
    std::thread trainingThread(runTraining, trainingNet, simulationNets, buffer, trainingDevice, simulationDevice);


    for(int i = 0; i < MCTS_SIMS_THREADS; i++) {
        simulationThreads[i].join();
    }

    trainingThread.join();

    torch::save(trainingNet, "last.pt");


}
