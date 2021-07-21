#include "ReplayBuffer.hpp"
#include<bits/stdc++.h>

using std::mt19937_64;
using std::random_device;
using std::uniform_int_distribution;
using std::vector;
using std::cout;
using std::cerr;
using std::endl;
using std::out_of_range;

// We'll use this class to generate random numbers
class RandomIterator
{
    public:
        /* Constructor for RandomIterator class.
         * Parameters:
         *     - amount => Amount of numbers to generate
         *     - min    => Minimum number in range to generate
         *     - max    => Maximum number in range to generate
         *
         * The constructor also instanstiates the variable gen
         * with a new random_device.
         */
        RandomIterator(const unsigned long long &amount, const unsigned long long &min, const unsigned long long &max): gen((random_device())())

        {
            floor = min;
            num_left = amount;
            last_k = min;
            n = max;
        }

        // Return a bool to determine if there are any numbers left to generate
        const bool has_next(void)
        {
            return num_left > 0;
        }

        // Generate the next random number
        const unsigned long long next(void)
        {
            if (num_left > 0)
            {
                // Partition the range of numbers to generate from
                unsigned long long range_size = (n - last_k) / num_left;
                
                // Initialize random generator
                uniform_int_distribution<unsigned long long> rnd(floor, range_size);

                // Generate random number
                unsigned long long r = rnd(gen) + last_k + 1;

                // Set last_k to r so that r is not generated again
                last_k = r;
                num_left--;
                return r;
            }
            else
            {
                throw out_of_range("Exceeded amount of random numbers to generate.");
            }
        }
    private:
            unsigned long long floor;
            unsigned long long n;
            unsigned long long last_k;
            unsigned long long num_left;
            mt19937_64         gen;

};

ReplayBuffer::ReplayBuffer(uint64_t maxlen) : memory(maxlen), _maxlen(maxlen) {}

ReplayBuffer::~ReplayBuffer() {}

void ReplayBuffer::push(std::shared_ptr<SPiZTuple> element) {
    _curlen = std::min(_curlen+1, _maxlen);
    memory.push_back(element);
}

std::tuple<torch::Tensor, torch::Tensor, torch::Tensor> ReplayBuffer::sample(long size) {

    RandomIterator iterator(size, 0, _curlen-1);


    torch::Tensor S = torch::zeros({size, 3, 8, 8});
    torch::Tensor PI = torch::zeros({size, 64});
    torch::Tensor Z = torch::zeros({64});


    long counter = 0;
    while(iterator.has_next())
    {   
        unsigned long long idx = iterator.next() - 1;
        auto s = std::get<0>(*memory[idx]);
        auto pi = std::get<1>(*memory[idx]);
        auto z = std::get<2>(*memory[idx]);

        S[counter] = s[0];
        PI[counter] = pi;
        Z[counter] = z;

        counter++;
    }

    return std::make_tuple(S, PI, Z);
}
