#def get_prob_distro(states, actions):
hall = Hallway((1,1), [g1])
states = hall._states
actions = hall.primitive_options
probs = {state:{ action: {} for action in actions }  for state in states

for s in states:
    for o, d in zip(actions, ((-1,0), (1,0), (0,-1), (0,1))):
        next_state = (s[0] + d[0], s[1] + d[1])
         
        if next_state not in states:
            next_state = s

        probs[s][o] = {
            next_state: 2./3.
        }
         
        for a in ((-1,0), (1,0), (0,-1), (0,1)):
            if a == d:
                continue
         
            next_state = (s[0] + a[0], s[1] + a[1])
         
            if next_state not in states:
                next_state = s
            
            if next_state in probs[s][o].keys():
                probs[s][o][next_state] += 1./9.
            else:
                probs[s][o][next_state] = 1./9.
         

