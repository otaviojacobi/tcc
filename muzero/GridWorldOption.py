class GridWorldOption:
    def __init__(self, action):
        self.action = action
        self.executed = False
        self.opt_id = self.action

    def __hash__(self):
        return self.action

    def __eq__(self, other):
        return self.action == other.action

    def __repr__(self):
        return str(self.action)

    def is_valid(self, env):
        return True

    # CAUTION ! this function returns -1 when the option finishes !
    def get_action(self, env):
        if not self.executed:
            self.executed = True
            return self.action
        self.executed = False
        return -1

