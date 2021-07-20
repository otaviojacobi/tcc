#pragma once

#include <cstdint>
#include <vector>
#include <torch/torch.h>

class Game
{
public:
    virtual ~Game() {};

    /* Play a valid move in the keyboard. Behaviour if move is not valid depends on implementation */
    virtual void                play(int8_t move)                 = 0;

    /* Returns a vector containing all possible moves*/
    virtual std::vector<int8_t> moves()                     const = 0;

    /* Returns a game score. It can be anything depending on the game itself */ 
    virtual int8_t              score()                           = 0;

    /* Returns a tensor containing the game tensor representation */
    virtual torch::Tensor       state()                     const = 0;

    /* Renders the game */
    virtual void                render()                    const = 0;

    /* DEEPCOPY the game state */
    virtual Game*               copy()                            = 0;

    /* If necessary converts the move identifier to an action in the space of [0~possible moves] */
    virtual int8_t              moveToAction(int8_t move)   const = 0;

    /* If necessary converts  an action in the space of [0~possible moves] to the move identifier */
    virtual int8_t              actionToMove(int8_t action) const = 0;

    /* Gets an id for the current player */
    virtual int8_t              player()                    const = 0;

};
