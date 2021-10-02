# class DynModel:
#     def __init__(self):
#         self.model_table = {}

#     def forward(self, s, o):
#         # returns s', r

#         if (s, o) not in self.model_table:
#             return (s, -1)
        
#         next_s, r, _, _ = self.model_table[(s, o)]
#         return (next_s, r)

#     # In this paper, the dynamics function is represented deterministically;
#     # the extension to stochastic transitions is left for future work.
#     def observe(self, s, o, next_s, r):
#         if not (s, o) in self.model_table.keys():
#             self.model_table[(s,o)] = (next_s, r, 1, r)
#         else:
#             if self.model_table[(s,o)][0] != next_s:
#                 print('DynModel stochastic observation:', (s,o), self.model_table[(s,o)], (next_s, r))
            
#             _, _, prev_count, prev_sum = self.model_table[(s,o)]
#             new_sum = prev_sum + r
#             new_count = prev_count + 1
#             new_r = new_sum / new_count

#             self.model_table[(s,o)] = (next_s, new_r, new_count, new_sum)

import random
class DynModel:
    def __init__(self):
        self.model_table = {}

    def forward(self, s, o):
        # returns s', r

        if (s, o) not in self.model_table:
            #TODO: change -1.0 value -> 0.0
            return (s, random.randint(1, 10) * [-1.0])

        return self.model_table[(s, o)]

    # In this paper, the dynamics function is represented deterministically;
    # the extension to stochastic transitions is left for future work.
    def observe(self, s, o, next_s, rs):
        if not (s, o) in self.model_table.keys():
            self.model_table[(s,o)] = (next_s, rs)
        else:
            if self.model_table[(s,o)] != (next_s, rs):
                print('DynModel stochastic observation:', (s,o), self.model_table[(s,o)], (next_s, rs))
