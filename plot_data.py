#!/bin/python3
import matplotlib.pyplot as plt
import numpy as np
import re

with open('testing/output.txt') as f:
	txt = f.read()

fs = re.findall(r'color = \((\d+), (\d+), (\d+)\)', txt)
rgb_array = [[int(m[0]), int(m[1]), int(m[2])] for m in fs]

img = np.array(rgb_array, dtype=int).reshape((1, len(rgb_array), 3))
plt.imshow(img, extent=[0, len(rgb_array), 0, 1], aspect='auto')
plt.show()
