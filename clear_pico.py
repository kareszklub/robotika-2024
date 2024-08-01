import sys
import os

if sys.platform == 'rp2':
	for f in os.listdir('.'):
		os.remove(f)
else:
	print('NOT RUNNING ON PICO!!')
