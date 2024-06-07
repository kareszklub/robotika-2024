#!/bin/python3
import matplotlib.pyplot as plt
import numpy as np
import csv

rgb_array = []
dist_array = []

with open('testing/output.txt', newline='') as f:
	reader = csv.reader(f.readlines(), delimiter=';', quoting=csv.QUOTE_NONE)

	for l in reader:
		if len(l) != 3:
			continue
		# print(f'{l=}')

		m = l[1].split(',')
		rgb_array.append([int(m[0][1:]), int(m[1]), int(m[2][:-1])])
		
		dist_array.append(float(l[2]) if l[2] != 'None' else 0)

	print('done parsing')

if len(rgb_array) == 0:
	exit(-1)


plt.figure()
plt.title('Robot data')

plt.subplot(211, title='rgb sensor')
img = np.array(rgb_array, dtype=int).reshape((1, len(rgb_array), 3))
plt.plot(img, extent=[0, len(rgb_array), 0, 1], aspect='auto')

plt.subplot(212, title='ultra sensor')
plt.plot(dist_array)
plt.show()
