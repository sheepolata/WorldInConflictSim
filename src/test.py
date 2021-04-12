import numpy as np

rng = np.random.default_rng(1995)

for i in range(10):
	print(rng.random())

l = [1, 2, 3,4 , 5, 6]
for i in range(10):
	print(rng.choice(l, 3, replace=False))
