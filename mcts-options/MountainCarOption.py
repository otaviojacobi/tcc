class MountainCarOption:
    def __init__(self, action, repeat=1):
        self.action = action
        self.executed = False
        self.opt_id = (action, repeat)
        self.repeat = repeat
        self.counter = 0

    def __hash__(self):
      return hash((self.action, self.repeat))

    def __eq__(self, other):
      return self.action == other.action and self.repeat == other.repeat

    def __repr__(self):
        return str((self.action, self.repeat))

    def is_valid_option(self, env):
        return True

    # CAUTION ! this function returns -1 when the option finishes !
    def get_action(self, env):
        if self.counter < self.repeat:
            self.counter += 1
            return self.action
        
        self.counter = 0
        return -1

