class DynModel:
    def __init__(self):
        self.model_table = {}

    def forward(self, s, o):
        # returns s', r

        if (s, o) not in self.model_table:
            return (s, -1)
        
        return self.model_table[(s, o)]

    # In this paper, the dynamics function is represented deterministically;
    # the extension to stochastic transitions is left for future work.
    def observe(self, s, o, next_s, r):
        if not (s, o) in self.model_table.keys():
            self.model_table[(s,o)] = (next_s, r)
        else:
            if self.model_table[(s,o)] != (next_s, r):
                print('DynModel stochastic observation:', (s,o), self.model_table[(s,o)], (next_s, r))
