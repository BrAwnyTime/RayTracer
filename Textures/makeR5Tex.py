import png
import itertools
import numpy as np
import time
import tables

'''---------------------------------------------------------'''
'''                 read PNG and setup                      '''
'''---------------------------------------------------------'''

t = png.Reader(filename="pattern.png")
textureName = "pattern"

texture = t.read()

width = texture[0]
height = texture[1]

start = time.time()
print("Loading texture...")
print(str(width) + "x" + str(height))

#this produces a numpy array which is width * 3 by height
pixels = np.vstack(itertools.imap(np.uint8, texture[2]))

print(pixels.shape)

#print elapsed time
cur_time = time.time()
elapsed = (cur_time - start)
print(str(elapsed) + "s")

'''---------------------------------------------------------'''
'''                 Setup PyTables Files                    '''
'''---------------------------------------------------------'''

print("opening textures.h5")

h5tex = tables.open_file("textures.h5", mode = 'a', title = "HDF5 Texture File")

#print elapsed time
cur_time = time.time()
elapsed = (cur_time - start)
print(str(elapsed) + "s")

print("creating array to represent the texture")

earth = h5tex.create_array(h5tex.root, textureName, pixels)

cur_time = time.time()
elapsed = (cur_time - start)
print(str(elapsed) + "s")

