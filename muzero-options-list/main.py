from random import choice
from time import sleep

from GridWorld import GridWorld

with open('./easy.txt') as f:
    g = GridWorld(f.read())

done = False

while not done:
    _, _, done = g.step(choice([0,1,2,3]))
    g.render()
    sleep(0.01)