#pragma once

#include <cstdint>
#include <vector>
#include <unordered_set>

#include <torch/torch.h>

#include "Game.hpp"

#define OUTER -2
#define EMPTY 0

#define BLACK 1
#define WHITE -1

#define UP -10
#define DOWN 10
#define LEFT -1
#define RIGHT 1
#define UP_RIGHT -9
#define DOWN_RIGHT 11
#define DOWN_LEFT 9
#define UP_LEFT -11

const static int8_t _OTHELLO_DIRECTIONS[8] = {UP, DOWN, LEFT, RIGHT, UP_RIGHT, DOWN_RIGHT, DOWN_LEFT, UP_LEFT};

class Othello : public Game {

public:
    Othello();
    ~Othello();
    void play(int8_t move);
    std::vector<int8_t> moves(void) const;
    int8_t score(void);
    torch::Tensor state(void) const;
    void render(void) const;
    Game* copy();

    int8_t actionToMove(int8_t action) const;
    int8_t moveToAction(int8_t move) const;

private:
    int8_t _board[100] = { OUTER, OUTER, OUTER, OUTER, OUTER, OUTER, OUTER, OUTER, OUTER, OUTER, OUTER, EMPTY, EMPTY,
                        EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, OUTER, OUTER, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY,
                        EMPTY, EMPTY, EMPTY, OUTER, OUTER, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY,
                        OUTER, OUTER, EMPTY, EMPTY, EMPTY, WHITE, BLACK, EMPTY, EMPTY, EMPTY, OUTER, OUTER, EMPTY,
                        EMPTY, EMPTY, BLACK, WHITE, EMPTY, EMPTY, EMPTY, OUTER, OUTER, EMPTY, EMPTY, EMPTY, EMPTY,
                        EMPTY, EMPTY, EMPTY, EMPTY, OUTER, OUTER, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY,
                        EMPTY, OUTER, OUTER, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, OUTER, OUTER,
                        OUTER, OUTER, OUTER, OUTER, OUTER, OUTER, OUTER, OUTER, OUTER };
    int8_t _player= BLACK;

    std::unordered_set<int8_t> _empties = std::unordered_set<int8_t> ({11, 12, 13, 14, 15, 16, 17, 18,
                                                                         21, 22, 23, 24, 25, 26, 27, 28,
                                                                         31, 32, 33, 34, 35, 36, 37, 38,
                                                                         41, 42, 43,         46, 47, 48,
                                                                         51, 52, 53,         56, 57, 58,
                                                                         61, 62, 63, 64, 65, 66, 67, 68,
                                                                         71, 72, 73, 74, 75, 76, 77, 78,
                                                                         81, 82, 83, 84, 85, 86, 87, 88});
    void flip(int8_t move, int8_t direction);
    int8_t findBracket(int8_t square, int8_t direction) const;
    bool hasBracket(int8_t move) const;

    void setBoard(int8_t *newBoard);
    void setPlayer(int8_t newPlayer);
    void setEmpties(std::unordered_set<int8_t> &newEmpties);
};
