#include "Othello.hpp"

Othello::Othello() {}

Othello::~Othello() {}

void Othello::play(int8_t move) {

    this->_board[move] = this->_player;
    this->_empties[move] = 0;

    for(int8_t i = 0; i < 8; i++) {
        this->flip(move, _OTHELLO_DIRECTIONS[i]);
    }

    this->_player *= -1;
}

std::vector<int8_t> Othello::moves() const {
    std::vector<int8_t> moves;

    for(int8_t i = 0; i < 100; i++) {
        if(this->_empties[i] == 1 && this->hasBracket(i)) {
            moves.push_back(i);
        }
    }

    return moves;
}

// Black wins on score > 0, White wins on score < 0, Draw on score == 0
int8_t Othello::score() {
    int8_t diff = 0;

    for(int8_t i = 0; i < 100; i++) {
        if(this->_board[i] == BLACK) diff++;
        else if (this->_board[i] == WHITE) diff--;
    }

    return diff;
}

torch::Tensor Othello::state() const {

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

void Othello::render() const {
    

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

Game* Othello::copy() {
    Othello* newGame = new Othello();

    newGame->setBoard(this->_board);
    newGame->setEmpties(this->_empties);
    newGame->setPlayer(this->_player);

    return (Game*) newGame;
}

int8_t Othello::player() const {
    return this->_player;
}

//TODO: double check if this is working 
int8_t Othello::moveToAction(int8_t move) const {
    return move - 11 - (2 * ((int8_t)move/10 - 1));
}

//TODO: double check if this is working 
int8_t Othello::actionToMove(int8_t action) const {
    return (10 *(int8_t)floor(action / 8)) + 11 + action % 8;
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

void Othello::setBoard(int8_t *newBoard) {
    memcpy(this->_board, newBoard, 100);
}

void Othello::setPlayer(int8_t newPlayer) {
    this->_player = newPlayer;
}

void Othello::setEmpties(int8_t *newEmpties) {
    memcpy(this->_empties, newEmpties, 100);
}
