from collections import defaultdict
import numpy as np
import random

class PredictionModel:
    def __init__(self, options):
        self.options = options
        self.p_table = {}
        self.v_table = {}

    def forward(self, s):

        if s not in self.p_table:
            valid_options = {opt for opt in self.options if opt.is_valid(s)}

            basic_p = []
            for opt in self.options:
                if opt in valid_options:
                    basic_p.append(1.0)
                else:
                    basic_p.append(0.0)

            basic_p = np.array(basic_p)

            if s not in self.v_table:
                v_value = 0.0
            else:
                v_value = self.v_table[s]

            return basic_p / np.sum(basic_p), v_value

        return self.p_table[s], self.v_table[s]

    #TODO: check for tabular update for pi and z (book ?)
    def observe(self, s, pi, z, alpha=0.01):

        if s in self.p_table:
            p_table, v_table = self.p_table[s], self.v_table[s]
        else:
            valid_options = {opt for opt in self.options if opt.is_valid(s)}

            basic_p = []
            for opt in self.options:
                if opt in valid_options:
                    basic_p.append(1.0)
                else:
                    basic_p.append(0.0)

            basic_p = np.array(basic_p)
            p_table = basic_p / np.sum(basic_p)
            v_table = 0.0

        self.p_table[s] = (1 - alpha) * p_table + alpha * pi
        self.v_table[s] = (1 - alpha) * v_table + alpha * z
