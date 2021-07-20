#pragma once

#include <cstdint>
#include <vector>

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
    int8_t player() const;

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

    int8_t _empties[100] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1,
                            1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1,
                            1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1,
                            0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1,
                            1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 1,
                            1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1,
                            1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0,
                            0, 0, 0, 0, 0, 0, 0, 0, 0};
    void flip(int8_t move, int8_t direction);
    int8_t findBracket(int8_t square, int8_t direction) const;
    bool hasBracket(int8_t move) const;

    void setBoard(int8_t *newBoard);
    void setPlayer(int8_t newPlayer);
    void setEmpties(int8_t *newEmpties);

};
