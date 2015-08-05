import numpy as np
import time
import tables
import sys

'''---------------------------------------------------------'''
'''                 Setup PyTables Files                    '''
'''---------------------------------------------------------'''

scale = 2
originalName = "earthScaled8"
scaledName = "earthScaled16"

h5tex = tables.open_file("/home/brad/rayTracer/Textures/textures.h5", mode = 'a', title = "HDF5 Texture File")

og = h5tex.getNode(h5tex.root, name=originalName)


texWidth = og.shape[1] / 3
texHeight = og.shape[0]

scaledWidth = texWidth/scale
scaledHeight = texHeight/scale

scaled = np.zeros((scaledHeight, scaledWidth * 3))

str_time = time.time()
curPercent = 0
lastPercent = 0

for y in range(0, scaledHeight):
    for x in range(0, scaledWidth):
        scaledValue = np.zeros(3)

        t_y = y * scale
        t_x = x * scale

        curPercent = np.floor((((y*scaledWidth)+(x+1))/float(scaledWidth*scaledHeight))*1000) / 10.0
        if (curPercent > lastPercent):
            lastPercent = curPercent
            cur_sec = time.time() - str_time
            sys.stdout.write("\rScale Texture %.1f%% [%ds]" % (curPercent, cur_sec))
            sys.stdout.flush()

        for iy in range(0, scale):
            for ix in range(0, scale):
                scaledValue += og[t_y + iy, (3 * (t_x + ix)):(3 * (t_x + ix)) + 3]

        scaledValue = scaledValue / float(scale**2)

        scaled[y, (3 * x):(3 * x) + 3] = scaledValue

earthsmall = h5tex.create_array(h5tex.root, scaledName, scaled, "Scaled texture map of the Earth's surface")

h5tex.close()
