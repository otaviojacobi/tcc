import matplotlib.pyplot as plt

no_opt = [-145.2, -125.08, -155.16, -112.24, -97.26, -102.76, -94.2, -90.58, -73.82, -72.94, -71.72, -66.78, -64.92, -65.48, -65.28, -62.66, -57.44, -61.86, -61.02, -54.84, -54.94, -53.26, -58.8, -48.14, -46.44, -46.36, -50.98, -46.28, -50.96, -44.6, -45.52, -42.06, -44.4, -43.12, -43.22, -43.28, -40.26, -39.64, -39.6, -40.24]
random_opt = [-239.4, -264.74, -251.8, -208.98, -165.38, -179.14, -198.84, -152.04, -170.2, -139.34, -149.52, -143.54, -141.1, -144.46, -138.42, -132.3, -124.66, -117.42, -114.02, -125.32, -116.48, -111.16, -94.44, -103.74, -94.9, -106.04, -92.58, -90.14, -94.44, -100.08, -84.78, -99.88, -85.02, -82.74, -85.62, -84.22, -91.54, -80.16, -71.52, -83.7]
door_opt = [-207.12, -211.84, -218.26, -162.82, -124.36, -152.76, -134.62, -118.82, -99.5, -109.38, -101.44, -98.66, -92.6, -91.3, -90.56, -91.9, -80.4, -83.66, -81.38, -79.56, -69.88, -77.82, -72.56, -79.04, -70.74, -69.22, -71.74, -64.84, -58.62, -64.0, -62.94, -61.7, -64.7, -59.36, -62.52, -60.62, -61.24, -56.08, -56.3, -57.44]


plt.title('MCTS with options')

plt.ylabel('Average Reward')
plt.xlabel('MCTS Simulations')


plt.plot(list(range(10,50)), no_opt, label='primitive options')
plt.plot(list(range(10,50)), random_opt, label='random options')
plt.plot(list(range(10,50)), door_opt, label='dooor options')

plt.hlines(-21, 10,49, colors='red', label='optimal')

plt.legend()
#plt.show()

plt.savefig('test.png')