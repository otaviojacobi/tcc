from helpers import preprocess_image
import gym

from PIL import Image
import numpy as np

import random

from time import sleep

env = gym.make('PongNoFrameskip-v4')
#env = gym.make('Breakout-v0')


o = env.reset()

done = False
for k in range(50):
    o, _, done, _ = env.step(random.randrange(env.action_space.n))
    #env.render()
    #sleep(0.01)



k = preprocess_image(o)

img = k.detach().cpu().numpy()


a=Image.fromarray(np.uint8(255. * img[0, :, :]))

print(a)

a.save('out.png')