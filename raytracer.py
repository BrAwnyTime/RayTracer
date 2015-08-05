import tables
import numpy as np
import math
import png
import sys
import time

sys.path.insert(0, '/home/brad/rayTracer/Objects')
from object import Sphere, Plane, Cylinder, Cube

str_time = time.time()
cur_sec = 0

'''---------------------------------------------------------'''
'''                     Setup Image                         '''
'''---------------------------------------------------------'''

width = 480
height = 300
s_num = 3
s_size = height/s_num
channels = 3
num_colours = 256
num_steps = 4

'''---------------------------------------------------------'''
'''                     Create Scene                        '''
'''---------------------------------------------------------'''

glblAmb = np.array([0.2, 0.2, 0.2])

l1 = np.array([[4.271, 16.705, -17.204],[0.1, 0.1, 0.1],[1.0, 1.0, 1.0],[1.0, 1.0, 1.0]])

lights = np.array([l1])

s1 = Sphere(np.array([ 9.50,-1.00, 19.00]), \
        np.array([[0.70, 0.70, 0.70],[0.10, 0.50, 0.80],[1.00, 1.00, 1.00]]), \
        50.0, 0.03, "earthScaled16", 256,\
        4.0, np.array([2, 1, -3]), np.array([0,3,1]))
s2 = Sphere(np.array([-2.25,-3.50, 11.50]), \
        np.array([[0.10, 0.10, 0.10],[0.60, 0.06, 0.00],[1.00, 1.00, 1.00]]), \
        30.0, 0.15, None, None, \
        1.5, None, None)
s3 = Sphere(np.array([-3.75, 0.00, 30.0]), \
        np.array([[0.20, 0.20, 0.20],[0.00, 0.50, 0.00],[0.00, 0.00, 0.00]]), \
       20.0, 0.25, None, None,  \
       5.0, None, None)
s4 = Sphere(np.array([-7.14, 5.89, 15.64]), \
        np.array([[0.20, 0.20, 0.20],[0.00, 0.00, 0.00],[1.00, 1.00, 1.00]]), \
        100.0, 1.0, None, None, \
        3.0, None, None)
p1 = Plane(np.array([0.0,-5.0,10.0]), \
        np.array([[0.20, 0.20, 0.20],[0.90, 0.90, 0.90],[0.00, 0.00, 0.00]]), \
        10.0, 0.1, "checkerboard", 256,  \
        np.array([0.0,1.0,0.0]), np.array([1.0,0.0,0.0]), 1.0)
c1 = Cylinder(np.array([ 0.0, -5.0, 10.0]), \
        np.array([[0.70, 0.70, 0.70],[0.65, 0.65, 0.65],[1.00, 1.00, 1.00]]), \
        50.0, 0.03, None, None, \
        np.array([0.0, 1.0, 0.0]), 0.75, 9.0)
cu1 = Cube(np.array([-8.0, -1.0, 16.5]), \
        np.array([[0.2,0.2,0.2],[1.0,1.0,0.0],[0.0,0.0,0.0]]), \
        5.0, 0.15, None, None, \
        np.array([1.0,8.0,-1.0]), np.array([1.0,0.0,-1.0]), 4)
cu2 = Cube(np.array([4.0, -1.53589838486225, 3.3]), \
        np.array([[1.0,1.0,1.0],[0.5,0.5,0.5],[0.0,0.0,0.0]]), \
        10.0, 0.04, None, None, \
        np.array([1.0,1.0,-1.0]), np.array([2.5,0.0,-1.0]), 2)
#cu1 = Cube(np.array([0.0, 0.0, 10.0]), \
#        np.array([[1.0,1.0,1.0],[0.5,0.5,0.5],[0.0,0.0,0.0]]), \
#        10.0, 0.04, None, None, \
#        np.array([0.0,1.0,0.0]), np.array([0.0,0.0,-1.0]), 2)

scene = np.array([s1, s2, s3, s4, p1, c1, cu1, cu2])

bg_colour = np.array([0.7, 0.7, 1.0])

'''---------------------------------------------------------'''
'''                     Setup Image Plane                   '''
'''---------------------------------------------------------'''

eye = np.array([0.0,0.0,-30.0])
lookatp = np.array([0.0,0.0,0.0])
ipd = 5
up = np.array([0,1,0])
ipwidth = 3.2
ipheight = 2.0

pixel_width = ipwidth/float(width)

lookat = lookatp-eye
lookat = lookat/np.linalg.norm(lookat)

ipx = np.cross(up, lookat)
ipx = ipx/np.linalg.norm(ipx)

ipy = np.cross(lookat, ipx)
ipy = ipy/np.linalg.norm(ipy)

ipo = ipd*(lookat) + eye

'''---------------------------------------------------------'''
'''                 Setup PyTables Files                    '''
'''---------------------------------------------------------'''

atom = tables.UInt8Atom()
p_atom = tables.Float64Atom()
rt = tables.open_file("rt.h5", "w")
image = rt.create_earray(rt.root, 'image', atom, (0, width*channels))
imagep = rt.create_earray(rt.root, 'image_plane', p_atom, (0, width, 3))

'''---------------------------------------------------------'''
'''                   Build Image Plane                     '''
'''---------------------------------------------------------'''

lastPercent = 0
curPercent = 0

for s in range(s_num):
    sp_image = np.zeros((s_size, width, 3), dtype=np.float64)
    for y in range(0, s_size):
        for x in range(0,width):
            curPercent = math.floor((((s*s_size*width)+(y*width)+(x+1))/float(width*height))*100)
            if (curPercent > lastPercent):
                lastPercent = curPercent
                cur_sec = time.time() - str_time
                sys.stdout.write("\rBuild Plane %d%% [%ds]" % (curPercent, cur_sec))
                sys.stdout.flush()

            trans_y = s*s_size + y

            sp_image[y,x] = ipo + (ipx-ipy)*pixel_width/2.0 + ipwidth*ipx*(-0.5 + (x/float(width))) - ipheight*ipy*(-0.5 + (trans_y/float(height)))

    imagep.append(sp_image)

'''----------------------------------------------------------'''
'''                      Trace Scene                         '''
'''----------------------------------------------------------'''

def getReflec(obj, incident, hit):

    normal = obj.getNormal(hit)

    incident = incident/np.linalg.norm(incident)

    reflect = incident + (np.dot(normal, -1.0 * incident) * 2 * normal)
    reflect = reflect/np.linalg.norm(reflect)

    return reflect

def phongShading(obj, source, hit):

    result = np.zeros((3), dtype=np.float64)
    col = np.zeros((3,3), dtype=np.float64)

    toLight = lights[0,0] - hit
    toLight = toLight/np.linalg.norm(toLight)

    normal = obj.getNormal(hit)

    toSource = source - hit
    toSource = toSource/np.linalg.norm(toSource)

    incidentLight = hit - lights[0,0]
    incidentLight = incidentLight/np.linalg.norm(incidentLight)

    reflectLight = getReflec(obj, incidentLight, hit)

    '''AMBIENT'''
    for i in range(3):
        col[0,i] = glblAmb[i] * obj.col[0,i]

    '''DIFFUSE'''
    dotProd = np.dot(normal, toLight)
    if (dotProd < 0.0):
        dotProd = 0.0

    difColour = obj.col[1]

    if obj.tex != None:
        difColour = obj.getTextureColour(hit)

    for i in range(3):
        col[1,i] = difColour[i] * (dotProd * lights[0,2,i])

    '''SPECULAR'''
    dotProd = np.dot(reflectLight, toSource)
    if (dotProd < 0.0):
        dotProd = 0.0

    dotProd = dotProd**obj.sh

    for i in range(3):
        col[2,i] = obj.col[2,i] * (dotProd * lights[0,3,i])

    '''SHADOWS'''
    '''to implement'''

    for i in range(3):
        result[i] = col[0,i] + col[1,i] + col[2,i]

    return result

def getNearObj(source, ray):

    nearDist = None
    count = -1
    nearObj = -1
    hit = None

    for obj in scene:
        count += 1
        temp_hit = obj.intersect(source, ray)
        if not temp_hit is None:
            tempDist = np.linalg.norm(temp_hit - source)

            if (tempDist < nearDist or nearDist is None) and tempDist > 0.0:
                nearDist = tempDist
                nearObj = count
                hit = temp_hit

    if not hit is None:
        no = np.zeros((5), dtype=np.float64)
        no[0:3] = hit
        no[3] = nearObj
        no[4] = nearDist

        return no
    else:
        return None


def rayTrace(source, ray, step):

    result = np.zeros((3), dtype=np.float64)
    average = np.zeros((3), dtype=np.float64)

    '''GET NEAR OBJ'''
    hit = None
    nearObj = -1
    no = getNearObj(source, ray)

    if not no is None:
        hit = no[0:3]
        nearObj = no[3]

    if not hit is None:
        result = phongShading(scene[nearObj], source, hit)
        if (step <= num_steps) and (num_steps > 0) and scene[nearObj].refl > 0.0:
            reflec = getReflec(scene[nearObj], hit - source, hit)
            reflec = reflec/np.linalg.norm(reflec)
            '''APPLY REFLECTION FIX'''
            reflec_source = hit + reflec * 0.0000000001
            '''TESTING
            print("start")
            print(str(hit))
            print(str(reflec_source))
            print("end")
            '''
            reflec_result = rayTrace(reflec_source, reflec, step+1)

            result = result + scene[nearObj].refl * reflec_result

    else:
        result = bg_colour

    return result

sys.stdout.write("\n")

lastPercent = 0.0
curPercent = 0.0

for s in range(s_num):
    s_image = np.zeros((s_size, width * channels), dtype=np.uint8)
    for y in range(0, s_size):
        for x in range(0,width):
            curPercent = math.floor((((s*s_size*width)+(y*width)+(x+1))/float(width*height))*1000) / 10.0
            if (curPercent > lastPercent):
                lastPercent = curPercent
                cur_sec = time.time() - str_time
                sys.stdout.write("\rTrace Scene %.1f%% [%ds]" % (curPercent, cur_sec))
                sys.stdout.flush()

            trans_y = s*s_size + y
            trans_x = x*3

            lookat = imagep[trans_y, x] - eye
            lookat = lookat/np.linalg.norm(lookat)

            colour = rayTrace(eye, lookat, 0)
            colour = (num_colours - 1) * np.array(colour)

            for i in range(3):
                if colour[i] >= num_colours:
                    colour[i] = num_colours - 1

            s_image[y,trans_x:trans_x+3] = colour

    image.append(s_image)

'''-------------------------------------------------------'''
'''                   Write to PNG                        '''
'''-------------------------------------------------------'''

pngfile = open('rt.png', 'wb')
pngWriter = png.Writer(width, height, greyscale=False, alpha=False, bitdepth=8)
pngWriter.write(pngfile, image[:])

'''----------------------------------------------------------

print(ipo)
print(ipx)
print(ipy)
print(imagep[:])

'''

rt.close()
pngfile.close()

sys.stdout.write("\n")
sys.stdout.flush()
