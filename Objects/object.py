import numpy as np
import tables

class Obj(object):

  def __init__(self, ctr = np.array([0.0,0.0,0.0]), colour = np.array([[1.0,0.0,0.0],[0.0,1.0,0.0],[0.0,0.0,1.0]]), shine = 0.0, reflectance = 0.0, textureName = None, texNumCol = None):
    self.c = ctr
    self.col = colour
    self.sh = shine
    self.refl = reflectance
    self.tex = textureName
    self.tnc = texNumCol

  def __str__(self):
    return "Object: {\n\tc: " + str(self.c) \
        + "\n\tColour: {\n\t\tAmbient: " + str(self.col[0,:]) \
        + "\n\t\tDiffuse: " + str(self.col[1,:]) \
        + "\n\t\tSpecular: " + str(self.col[2,:]) \
        + "\n\t}\n\tShine: " + str(self.sh) \
        + "\n\tReflectance: " + str(self.refl) \
        + "\n\tTexture Name: " + str(self.tex) \
        + "\n\tTexture Num Colour: " + str(self.tnc) \
        + "\n}"

  def intersect(self, o, v):
    raise NotImplementedError

  def getNormal(self, hit):
    raise NotImplementedError

  def getTextureColour(self, hit):
    raise NotImplementedError

class Sphere(Obj):

  def __init__(self, ctr = np.array([0.0,0.0,0.0]), colour = np.array([[1.0,0.0,0.0],[0.0,1.0,0.0],[0.0,0.0,1.0]]), \
      shine = 0.0, reflectance = 0.0, textureName = None, texNumCol = None, \
      rad = 1.0, north = np.array([0.0,1.0,0.0]), west = np.array([-1.0,0.0,0.0])):
    super(Sphere, self).__init__(ctr, colour, shine, reflectance, textureName, texNumCol)
    self.r = rad
    if north == None:
      self.nor = None
    else:
      self.nor = north/np.linalg.norm(north)

    if west == None:
      self.wes = None
    else:
      temp = np.cross(self.nor, west)
      temp = temp/np.linalg.norm(temp)
      self.wes = np.cross(temp, self.nor)
      self.wes = self.wes/np.linalg.norm(self.wes)

  def __str__(self):
    return "Sphere: {\n\tr: " + str(self.r) + \
        "\n\tnorth: " + str(self.nor) + \
        "\n\twest: " + str(self.wes) + \
        "\n}\n" + super(Sphere, self).__str__()

  def intersect(self, o, v):

    v = v/np.linalg.norm(v)

    dist1 = dist2 = 0.0
    hit = None

    t = o - self.c

    disc = (np.dot(v, t)**2 - np.linalg.norm(t)**2 + self.r**2)

    if disc >= 0:
      dist1 = -1.0 * (np.dot(v, t)) + disc**0.5
      dist2 = -1.0 * (np.dot(v, t)) - disc**0.5

      if((dist1 > 0.0000001) and (dist1 <= dist2)):
        hit = o + v * dist1
      elif (dist2 > 0.0000001):
        hit = o + v * dist2

    return hit

  def getNormal(self, hit):
    if not hit is None:
      norm = hit - self.c
      norm = norm/np.linalg.norm(norm)
      return norm
    else:
      return None

  def getTextureColour(self, hit):

    if(self.tex == None):
      return None

    h5Tex = tables.open_file(filename="/home/brad/rayTracer/Textures/textures.h5", mode='r')
    tex = h5Tex.getNode(h5Tex.root, self.tex)

    t_height = tex.shape[0]
    t_width = tex.shape[1] / 3.0

    toHit = hit - self.c

    w = np.array([-1,0,0])
    n = np.array([0,1,0])
    t = np.array([0,0,1])

    changed = 0

    if np.dot(self.nor, n) != 1.0:
      w = np.cross(t, self.nor)
      t = np.cross(self.nor, w)
      n = self.nor
      changed = 1

    if np.dot(self.wes, w) != 1.0:
      t = np.cross(n, self.wes)
      n = np.cross(self.wes, t)
      w = self.wes
      changed = 1

    if changed == 1:
      w = w/np.linalg.norm(w)
      n = n/np.linalg.norm(n)
      t = t/np.linalg.norm(t)

    ww = np.dot(toHit, w)
    nn = np.dot(toHit, n)
    tt = np.dot(toHit, t)

    toHit = np.array([ww, nn, tt])

    phi = np.arccos(toHit[1]/self.r)
    theta = np.arctan2(toHit[2],toHit[0])

    if toHit[2] < 0:
      theta += 2.0 * np.pi

    temp = np.floor(phi/np.pi)
    phi -= temp * np.pi

    temp = np.floor(theta/(2.0 * np.pi))
    theta -= temp * 2.0 * np.pi

    t_x = (t_width - np.floor((theta/(2.0*np.pi)) * t_width)) - 1
    t_y = np.floor((phi/np.pi) * t_height) - 1

    if(t_x < 0):
      t_x = 0

    if(t_y < 0):
      t_y = 0

    texColour = tex[t_y, (3.0 * t_x) : (3.0 * t_x) + 3] / float(self.tnc - 1)

    h5Tex.close()

    return texColour

class Plane(Obj):

  def __init__(self, ctr = np.array([0.0,0.0,0.0]), colour = np.array([[1.0,0.0,0.0],[0.0,1.0,0.0],[0.0,0.0,1.0]]), \
      shine = 0.0, reflectance = 0.0, textureName = None, texNumCol = None, \
      normal = np.array([0.0,1.0,0.0]), texDirection = np.array([1.0,0.0,0.0]), texScale = 1.0):
    super(Plane, self).__init__(ctr, colour, shine, reflectance, textureName, texNumCol)
    self.n = normal
    self.texDir = texDirection/np.linalg.norm(texDirection)
    self.texS = texScale

  def __str__(self):
    return "Plane: {\n\tnormal: " + str(self.n) + \
        "\n\ttexture direction: " + str(self.texDir) + \
        "\n\ttexture scale: " + str(self.texS) + \
        "\n}\n" + super(Plane, self).__str__()

  def intersect(self, o, v):

    hit = None
    denom = np.dot(self.n, v)

    if denom != 0:
      dist = np.dot(self.n , (self.c - o))/denom
      if dist > 0.0000001:
        hit = o + v * dist

    return hit

  def getNormal(self, hit):
    if not hit is None:
      return self.n
    else:
      return None

  def getTextureColour(self, hit):

    if(self.tex == None):
      return None

    h5Tex = tables.open_file(filename="/home/brad/rayTracer/Textures/textures.h5", mode='r')
    tex = h5Tex.getNode(h5Tex.root, self.tex)

    t_height = tex.shape[0]
    t_width = tex.shape[1] / 3.0

    toHit = hit - self.c

    x = np.array([1.0,0.0,0.0])
    y = np.array([0.0,1.0,0.0])
    z = np.array([0.0,0.0,1.0])

    changed = 0

    if(np.dot(x, self.texDir) != 1.0):
      z = np.cross(y, self.texDir)
      y = np.cross(self.texDir, z)
      x = self.texDir
      changed = 1

    if(np.dot(y, self.n) != 1.0):
      x = np.cross(z, self.n)
      z = np.cross(self.n, x)
      y = self.n
      changed = 1

    if changed == 1:
      x = x/np.linalg.norm(x)
      y = y/np.linalg.norm(y)
      z = z/np.linalg.norm(z)

    t_x = np.dot(toHit, x)/self.texS
    t_y = np.dot(toHit, -z)/self.texS

    t_x = np.floor(np.mod(t_x, t_width))
    t_y = np.floor(np.mod(t_y, t_height))

    texColour = tex[t_y, (3.0 * t_x) : (3.0 * t_x) + 3] / float(self.tnc - 1)

    #print(str(texColour) + ": " + str(t_x) + "," + str(t_y))

    h5Tex.close()

    return texColour

class Cylinder(Obj):

  def __init__(self, ctr = np.array([0.0,0.0,0.0]), colour = np.array([[1.0,0.0,0.0],[0.0,1.0,0.0],[0.0,0.0,1.0]]), \
      shine = 0.0, reflectance = 0.0, textureName = None, texNumCol = None, \
      north = np.array([0.0,1.0,0.0]), radius = 0.25, height = 5.0):
    super(Cylinder, self).__init__(ctr, colour, shine, reflectance, textureName, texNumCol)
    self.no = north/np.linalg.norm(north)
    self.r = radius
    self.h = height

  def __str__(self):
    return "Cylinder: {\n\tNorth: " + str(self.no) \
        + "\n\tRadius: " + str(self.r) \
        + "\n\tHeight: " + str(self.h) \
        + "\n}\n" \
        + super(Cylinder, self).__str__()

  def intersect(self, o, v):

    t1 = np.cross(o, self.no)
    t2 = np.cross(v, self.no)
    t3 = np.cross(self.c, self.no)

    a = np.dot(t2, t2)
    b = 2.0 * np.dot(t2, t1) - 2.0 * np.dot(t2, t3)
    c = np.dot(t1, t1) - 2.0 * np.dot(t1, t3) + np.dot(t3, t3) - self.r**2.0

    disc = b**2.0 - 4.0 * a * c

    dist1 = dist2 = 0.0
    hit1 = hit2 = None
    hit = hith1 = hith2 = None

    if (disc >= 0):

      dist1 = (-b - disc**0.5)/(2.0 * a)
      dist2 = (-b + disc**0.5)/(2.0 * a)

      hit1 = o + v * dist1
      hit2 = o + v * dist2

      toHit = (hit1 - self.c)
      hitH1 = np.dot(self.no, toHit)
      toHit = (hit2 - self.c)
      hitH2 = np.dot(self.no, toHit)

      if ((dist1 > 0) and (dist1 <= dist2) and (hitH1 >= 0) and (hitH1 <= self.h)):
        hit = (o + v * dist1)
      elif ((hitH2 >= 0) and (hitH2 <= self.h) and (dist2 > 0)):
        hit = (o + v * dist2)

    return hit

  def getNormal(self, hit):

    toHit = (hit - self.c)
    hitH = np.dot(self.no, toHit)

    cAtHit = self.c + hitH * self.no

    return hit - cAtHit

class Cube(Obj):

  def __init__(self, ctr = np.array([0.0,0.0,0.0]), colour = np.array([[1.0,0.0,0.0],[0.0,1.0,0.0],[0.0,0.0,1.0]]), \
      shine = 0.0, reflectance = 0.0, textureName = None, texNumCol = None, \
      top = np.array([0.0,1.0,0.0]), front = np.array([0.0,1.0,0.0]), size = 5.0):
    super(Cube, self).__init__(ctr, colour, shine, reflectance, textureName, texNumCol)

    top = top/np.linalg.norm(top)

    right = np.cross(top, front)
    right = right/np.linalg.norm(right)

    front = np.cross(right, top)
    front = front/np.linalg.norm(front)

    self.norms = np.array([right, top, front, -right, -top, -front])

    self.s = size

  def __str__(self):
    return "Cube: {\n\tTop: " + str(self.norms[1]) \
        + "\n\tFront: " + str(self.norms[2]) \
        + "\n\tSize: " + str(self.s) \
        + "\n}\n" \
        + super(Cube, self).__str__()

  def intersect(self, o, v):

    dist = np.array([-1.0,-1.0,-1.0,-1.0,-1.0,-1.0])
    hit = np.zeros((6,3))

    for i in range(0,6):
      denom = np.dot(v, self.norms[i])

      centre = self.c + (self.s * self.norms[i])

      if denom != 0:

        dist[i] = np.dot(self.norms[i], (centre - o))/denom

        if dist[i] > 0.0000001:
          hit[i] = o + v * dist[i]

          x = self.norms[(i + 1) % 3]
          y = self.norms[(i + 2) % 3]

          toHit = hit[i] - centre
          xH = np.dot(x, toHit)
          yH = np.dot(y, toHit)

          if ((abs(xH) > self.s) or (abs(yH) > self.s)):
            toHit = np.zeros(3)
            dist[i] = -1.0

    smallest = -1.0
    smallestIndex = -1

    for i in range(0,6):
      if smallest == -1.0 and dist[i] > 0.0:
        smallest = dist[i]
        smallestIndex = i
      elif dist[i] > 0.0 and smallest > dist[i]:
        smallest = dist[i]
        smallestIndex = i

    #print hit
    #print dist
    #print str(smallest) + " @ " + str(smallestIndex)
    #print hit[smallestIndex]

    if smallestIndex >= 0:
      #print hit
      #print dist
      #print str(smallest) + " @ " + str(smallestIndex)
      #print hit[smallestIndex]

      return hit[smallestIndex]
    else:
      return None

  def getNormal(self, hit):

    cToHit = hit - self.c

    n = np.zeros(3)

    largest = 0
    largestIndex = 0

    for i in range(0,3):
      n[i] = np.dot(cToHit, self.norms[i])

      if abs(n[i]) > largest:
        largest = abs(n[i])
        largestIndex = i

    if n[largestIndex] < 0:
      largestIndex += 3

    return self.norms[largestIndex]


'''
****
CUBE
****

eye = np.array([0.0,0.0,-30.0])

lookatp = np.array([0.0,1.5,8.0])

lookat = lookatp-eye
lookat = lookat/np.linalg.norm(lookat)

cu = Cube(np.array([0.0, 0.0, 10.0]), \
  np.array([[1.0,1.0,1.0],[0.5,0.5,0.5],[0.0,0.0,0.0]]), \
  10.0, 0.04, None, None, \
  np.array([0.0,1.0,0.0]), np.array([0.0,0.0,-1.0]), 2)

print cu.intersect(eye, lookat)

print cu

********
CYLINDER
********

cy = Cylinder(np.array([ 0.0, -5.0, -10.0]), \
    np.array([[0.70, 0.70, 0.70],[0.65, 0.65, 0.65],[1.00, 1.00, 1.00]]), \
    50.0, 0.03, np.array([0.0, 1.0, 0.0]), 0.75, 9.0)
print(cy)

******
PLANES
******

p = Plane()
print(p)

*******************
SPHERES and OBJECTS
*******************

centre = np.array([0.5, 0.75, 4.5])

s = Sphere(centre, colour = np.array([[1.0,0.0,0.0],[0.0,1.0,0.0],[0.0,0.0,1.0]]), \
      shine = 0.0, reflectance = 0.0, textureName = "earth", texNumCol = 256, \
      rad = 2.0, north = np.array([0.0,1.0,0.0]), west = np.array([-1.0,0.0,0.0]))

lookatp = np.array([0.5, 1.75, 4.5])
eye = np.array([0, 0, 0])

lookat = lookatp - eye
lookat = lookat/np.linalg.norm(lookat)

x = s.intersect(eye, lookat)

normatx = s.getNormal(x)

texColour = s.getTextureColour(x)

print(s)
print(x)
print(normatx)
print(texColour)

*******
OBJECTS
*******

o = Obj()
print(o)
'''
