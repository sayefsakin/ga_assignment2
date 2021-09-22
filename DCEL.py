import math as m
from tkinter import *

YSIZE = 750
PSIZE = 4

#------------------------------------------------------------------------
# Class Vertex
#------------------------------------------------------------------------
class Vertex:
  def __init__(self, x, y):
    self.x = x
    self.y = y
    self.hedges = []  # list of halfedges whose tail is this vertex

  def __eq__(self, other):
    if isinstance(other, Vertex):
      return self.x == other.x and self.y == other.y
    return NotImplemented

  def sortHedges(self):
    self.hedges.sort(key=lambda a: a.angle, reverse=True)

  def __repr__(self):
    return "({0},{1})".format(self.x, self.y)


#------------------------------------------------------------------------
# Class Hedge
#------------------------------------------------------------------------
class Hedge:
  def __init__(self, v1, v2):  # v1 -> v2
    self.twin = None
    self.prev = None
    self.next = None
    self.tail = v1
    self.face = None
    self.angle = self.findHAngle(v2.x-v1.x, v2.y-v1.y)

  def __eq__(self, other):
    return self.tail == other.tail and self.next.tail == other.next.tail

  def __repr__(self):
    if self.next is not None:
      return "({0},{1})->({2},{3})".format(self.tail.x, self.tail.y, self.next.tail.x, self.next.tail.y)
    else:
      return "({0},{1})->()".format(self.tail.x, self.tail.y)

  def findHAngle(self, dx, dy):
      l = m.sqrt(dx*dx + dy*dy)
      if dy > 0:
          return m.acos(dx/l)
      else:
          return 2*m.pi - m.acos(dx/l)

#------------------------------------------------------------------------
# Class Face
#------------------------------------------------------------------------
class Face:
  def __init__(self):
    self.halfEdge = None
    self.name = None


#------------------------------------------------------------------------
# Class DCEL
#------------------------------------------------------------------------
class DCEL:
  def __init__(self):
    self.vertices = []
    self.hedges = []
    self.faces = []

  #---- Returns the vertex object given x and y
  def findVertex(self, x, y):
    for v in self.vertices:
      if v.x == x and v.y == y:
        return v
    return None

  #---- Returns the halfEdge given v1 and v2, tuples
  def findHalfEdge(self, v1, v2):
    for halfEdge in self.hedges:
      nextEdge = halfEdge.next
      if (halfEdge.tail.x == v1[0] and halfEdge.tail.y == v1[1]) and (nextEdge.tail.x == v2[0] and nextEdge.tail.y == v2[1]):
        return halfEdge
    return None

  #---- build_dcel
  def build_dcel(self, points, segments):
    #  For each point create a vertex and add it to vertices
    for point in points:
        self.vertices.append(Vertex(point[0], point[1]))

    #---- For each input segment, create two hedges and assign their tail vertices and twins
    for segment in segments:
        startVertex = segment[0]
        endVertex = segment[1]

        v1 = self.findVertex(startVertex[0], startVertex[1])
        v2 = self.findVertex(endVertex[0], endVertex[1])

        h1 = Hedge(v1, v2)
        h2 = Hedge(v2, v1)

        h1.twin = h2
        h2.twin = h1

        v1.hedges.append(h1)
        v2.hedges.append(h2)

        self.hedges.append(h1)
        self.hedges.append(h2)

    #---- For each endpt sort the hedges whose tail vertex is that endpt in CW order.

    for vertex in self.vertices:
        vertex.sortHedges()

        noOfHalfEdges = len(vertex.hedges)

        if noOfHalfEdges < 2:
            print("Invalid DCEL, there should be at least two half edges for a vertex")
            return

        # For each pair of half-edges e1, e2 in CW order, e1->twin->next = e2 and e2->prev = e1->twin.
        for i in range(noOfHalfEdges - 1):
            e1 = vertex.hedges[i]
            e2 = vertex.hedges[i+1]
            e1.twin.next = e2
            e2.prev = e1.twin

        # for the last and first halfedges
        e1 = vertex.hedges[noOfHalfEdges - 1]
        e2 = vertex.hedges[0]

        e1.twin.next = e2
        e2.prev = e1.twin

    #---- For every cycle, allocate and assign a face structure.
    faceCount = 0
    for halfEdge in self.hedges:
        if halfEdge.face == None:
            faceCount += 1

            f = Face()
            f.name = "f" + str(faceCount)

            f.halfEdge = halfEdge
            halfEdge.face = f

            h = halfEdge
            while (not h.next == halfEdge):
                h.face = f
                h = h.next
            h.face = f

            self.faces.append(f)

  #---- traverse face given a segment, like [(0, 5), (2, 5)]
  def traverseFace(self, segment):
    # find the half edge whose vertices are that of the segment
    v1 = segment[0]
    v2 = segment[1]
    startEdge = self.findHalfEdge(v1, v2)

    h = startEdge
    while (h.next != startEdge):
      print(h, end="--->")
      h = h.next
    print(h, '--->', startEdge)

  #---- traverse edges starting at a vertex
  def traverseHalfEdges(self, point):
      vp = None
      for v in self.vertices:
          if v.x == point[0] and v.y == point[1]:
              vp = v
      if vp != None:
          for e in vp.hedges:
              print(e)
      else:
          print("no vertex")

  # insert vertex p in edge with endpoints v1 and v2, v3 and v4
  def addNewVertex(self, p, v1, v2, v3, v4):
      x = Vertex(p[0], p[1])
      self.vertices.append(x)

      def addDirectedEdges(t1, t2):
        c12 = self.findHalfEdge(t1, t2)
        if c12 is None:
            print('non found')
        p1 = self.findVertex(t1[0], t1[1])
        p2 = self.findVertex(t2[0], t2[1])
        c12pp = Hedge(p1, x)
        c12p = Hedge(x, p2)
        self.hedges.append(c12p)
        self.hedges.append(c12pp)
        x.hedges.append(c12p)
        p1.hedges.append(c12pp)

        c12p.next = c12.next
        c12p.prev = c12pp
        c12p.face = c12.face

        c12pp.next = c12p
        c12pp.prev = c12.prev
        c12pp.face = c12.face

        e_prev = c12.prev
        e_prev.next = c12pp
        e_next = c12.next
        e_next.prev = c12p

        if c12p.face.halfEdge == c12:
            c12p.face.halfEdge = c12p
        return c12p, c12pp, c12

      # for v1 and v2
      e12p, e12pp, e12 = addDirectedEdges(v1, v2)
      e11pp, e11p, e11 = addDirectedEdges(v2, v1)
      e12p.twin = e11p
      e11p.twin = e12p
      e12pp.twin = e11pp
      e11pp.twin = e12pp

      self.hedges.remove(e12)
      self.hedges.remove(e11)

      # for v3 and v4
      f12p, f12pp, f12 = addDirectedEdges(v3, v4)
      f11pp, f11p, f11 = addDirectedEdges(v4, v3)
      f12p.twin = f11p
      f11p.twin = f12p
      f12pp.twin = f11pp
      f11pp.twin = f12pp

      self.hedges.remove(f12)
      self.hedges.remove(f11)

      f12pp.next = e11pp
      e11pp.prev = f12pp
      e12pp.next = f12p
      f12p.prev = e12pp
      f11p.next = e12p
      e12p.prev = f11p
      e11p.next = f11pp
      f11pp.prev = e11p

  def updateFaces(self):
      # clear old faces
      for halfEdge in self.hedges:
          halfEdge.face = None
      self.faces.clear()

      # add new faces
      faceCount = 0
      for halfEdge in self.hedges:
          if halfEdge.face == None:
              faceCount += 1

              f = Face()
              f.name = "f" + str(faceCount)

              f.halfEdge = halfEdge
              halfEdge.face = f

              h = halfEdge
              while (not h.next == halfEdge):
                  h.face = f
                  h = h.next
              h.face = f

              self.faces.append(f)









#========================================================================
if __name__ == "__main__":
    points = [(0, 5), (2, 5), (3, 0), (0, 0)]
    
    segments = [ [(0, 5), (2, 5)],
                 [(2, 5), (3, 0)],
                 [(3, 0), (0, 0)],
                 [(0, 0), (0, 5)],
                 [(0, 5), (3, 0)],
               ]
    
    myDCEL = DCEL()
    myDCEL.build_dcel(points, segments)
    myDCEL.traverseFace([(3, 0), (0, 5)])
    myDCEL.traverseHalfEdges((0, 5))


    root = Tk()
    root.title("DCEL")
    root.geometry(str(YSIZE)+'x'+str(YSIZE)) #("800x800")

    canvas = Canvas(root, width=YSIZE, height=YSIZE, bg='#FFF', highlightbackground="#999")
    canvas.grid(row=0, column=0)

    drawSegments(segments)
    root.mainloop()