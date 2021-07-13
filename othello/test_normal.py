from random import choice
import time
from othello import Othello

black_wins = 0
white_wins = 0
draw = 0

start_time = time.time()

for k in range(1000):
    o = Othello()

    while True:
        moves = o.legal_moves()

        if len(moves) == 0:
            break

        move = choice(moves)

        o.play(move)

    score = o.score()
    if score > 0:
        black_wins += 1
    elif score < 0:
        white_wins +=1
    else:
        draw += 1

print("--- %s seconds ---" % (time.time() - start_time))
print(white_wins, black_wins, draw)
