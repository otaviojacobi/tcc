from collections import defaultdict
import numpy as np
import random

class PredictionModel:
    def __init__(self, options):
        self.options = options
        self.p_table = defaultdict(self._init_p_table)
        self.v_table = defaultdict(float)

    def forward(self, s):
        return self.p_table[s], self.v_table[s]

    #TODO: check for tabular update for pi and z (book ?)
    def observe(self, s, pi, z):
        alpha = 0.02

        self.p_table[s] = (1 - alpha) * self.p_table[s] + alpha * pi
        self.v_table[s] = (1 - alpha) * self.v_table[s] + alpha * z


    #TODO: is initing same prob a good idea ?
    def _init_p_table(self):
        return np.ones(len(self.options)) / len(self.options)
        #return np.random.dirichlet(np.ones(len(self.options)) * 0.25, size=1)[0]

