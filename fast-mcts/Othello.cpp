#include <cstdint>
#include <vector>
#include <torch/torch.h>

#include "Othello.hpp"

#include <iostream>

Othello::Othello() {}

Othello::~Othello() {}

void Othello::play(int8_t move) {

    this->_board[move] = this->_player;
    this->_empties.erase(move);

    for(int8_t i = 0; i < 8; i++) {
        this->flip(move, _OTHELLO_DIRECTIONS[i]);
    }

    this->_player *= -1;
}

std::vector<int8_t> Othello::moves(void) const {
    std::vector<int8_t> moves;


    for (auto move: this->_empties) {
        if(this->hasBracket(move)) {
            moves.push_back(move);
        }
    }
    

    return moves;
}

// Black wins on score > 0, White wins on score < 0, Draw on score == 0
int8_t Othello::score(void) {
    int8_t diff = 0;

    for(int8_t i = 0; i < 100; i++) {
        if(this->_board[i] == BLACK) diff++;
        else if (this->_board[i] == WHITE) diff--;
    }

    return diff;
}

torch::Tensor Othello::state(void) const {

    torch::Tensor gameState = torch::zeros({3, 8, 8});
    int8_t array_index;

    for(int8_t i = 0; i < 8; i++) {
        for(int8_t j = 0; j < 8; j++) {
            array_index = ((i + 1) * 10) + j + 1;

            if (this->_board[array_index] == BLACK) gameState[0][i][j] = 1;
            else if (this->_board[array_index] == WHITE) gameState[1][i][j] = 1;
        }
    }

    if (this->_player == BLACK) gameState[2] = 1;

    return gameState;
}

void Othello::render(void) const {
    

    for (int8_t i = 0; i < 8; i++) {
        for(int8_t j = 0; j < 8; j++) {
            int8_t array_index = ((i + 1) * 10) + j + 1;
            if (this->_board[array_index] == BLACK) {
                std::cout << "o ";
            } else if (this->_board[array_index] == WHITE) {
                std::cout << "X ";
            } else if (this->_board[array_index] == EMPTY) {
                std::cout << ". ";
            }
        }
        std::cout << std::endl;
    }
}

/* PRIVATE STUFF */
void Othello::flip(int8_t move, int8_t direction) {
    int8_t bracket = this->findBracket(move, direction);

    if(bracket == -1) return;

    int8_t square = move + direction;

    while (square != bracket) {
        this->_board[square] = this->_player;
        square += direction;
    }
}

int8_t Othello::findBracket(int8_t square, int8_t direction) const {
    int8_t bracket = square + direction;

    if (this->_board[bracket] == this->_player) return -1;

    int8_t op = -1 * this->_player;

    while (this->_board[bracket] == op) bracket += direction;

    if (this->_board[bracket] == OUTER || this->_board[bracket] == EMPTY) return -1;

    return bracket;
}

bool Othello::hasBracket(int8_t move) const {
    for(int8_t i = 0; i < 8; i++) {
        if (this->findBracket(move, _OTHELLO_DIRECTIONS[i]) != -1) return true;
    }
    return false;
}
