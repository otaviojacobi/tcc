import matplotlib.pyplot as plt
SIM_RANGE = list(range(12, 52))
SMOOTH = 20
CPUTC = 20

out = [-66.6, -59.85, -68.4, -55.4, -47.3, -55.2, -51.75, -53.0, -44.8, -48.9, -45.7, -46.1, -47.45, -45.95, -42.9, -45.7, -39.95, -40.75, -42.4, -41.75, -39.15, -42.6, -43.6, -37.15, -36.7, -35.15, -37.1, -36.15, -38.0, -37.7, -34.75, -35.4, -35.2, -34.5, -33.95, -31.65, -32.15, -35.8, -34.1, -33.05]
out2 = [-29.05, -23.8, -27.65, -26.75, -24.8, -28.65, -24.35, -23.95, -23.5, -24.85, -23.25, -23.1, -24.25, -23.55, -23.05, -23.1, -22.8, -23.55, -23.7, -23.45, -24.2, -22.4, -23.4, -22.3, -23.3, -23.3, -22.4, -23.0, -23.1, -22.85, -22.7, -22.1, -23.5, -22.0, -22.1, -22.3, -22.1, -22.3, -22.3, -23.5]
out3 = [-27.9, -29.75, -32.0, -27.2, -29.45, -26.9, -28.95, -26.0, -27.0, -26.3, -26.55, -26.0, -26.6, -24.25, -25.4, -26.6, -23.35, -23.1, -25.3, -22.75, -22.5, -22.8, -22.3, -22.2, -22.45, -22.05, -24.0, -21.6, -22.7, -24.9, -21.85, -22.15, -22.9, -23.35, -23.25, -23.65, -23.2, -24.05, -25.15, -23.25]


plt.title('MCTS-O: Action on Env with Options')

plt.ylabel('Average Total Return')
plt.xlabel('MCTS simulations')

plt.plot(SIM_RANGE, out, label='primitive options')
plt.plot(SIM_RANGE, out2, label='random options')
plt.plot(SIM_RANGE, out3, label='dooor options')

plt.hlines(-20, SIM_RANGE[0], SIM_RANGE[-1], colors='red', label='optimal')

mini = min([min(out), min(out2), min(out3)])
plt.ylim((mini,0))

plt.legend()
#plt.show()

plt.savefig('test.png')