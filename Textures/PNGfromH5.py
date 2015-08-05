import numpy as np
import tables
import png

'''---------------------------------------------------------'''
'''                 Setup PyTables Files                    '''
'''---------------------------------------------------------'''

name = "pattern"

h5tex = tables.open_file("/home/brad/rayTracer/Textures/textures.h5", mode = 'r', title = "HDF5 Texture File")

image = h5tex.getNode(h5tex.root, name=name)
width = image.shape[1] / 3
height = image.shape[0]

pngfile = open(name + ".png", 'wb')
pngWriter = png.Writer(width, height, greyscale=False, alpha=False, bitdepth=8)
pngWriter.write(pngfile, image[:])

h5tex.close()
