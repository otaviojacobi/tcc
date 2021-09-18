class RepresentationModel:
    def __init__(self):
        pass

    def forward(self, env):
        #returns h_s
        return (env.cur_x, env.cur_y)