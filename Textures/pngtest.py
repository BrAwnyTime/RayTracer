import time
import tables
import numpy as np

'''---------------------------------------------------------'''
'''                       Setup                             '''
'''---------------------------------------------------------'''

start = time.time()

h5Tex = tables.open_file(filename="Textures/textures.h5", mode='r')
earth = h5Tex.getNode(h5Tex.root, name="earth")

'''---------------------------------------------------------'''
'''              Example of reading a pixel                 '''
'''---------------------------------------------------------'''

t_height = earth.shape[0]
t_width = earth.shape[1]

x = 20000
y = 10795

trans_x = 3 * x

print("getting a sample pixels values")
print(earth[y, trans_x:trans_x + 3] / 255.0)

#print elapsed time
cur_time = time.time()
elapsed = (cur_time - start)
print(str(elapsed) + "s")
