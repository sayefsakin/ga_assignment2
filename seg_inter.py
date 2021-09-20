from RedBlackTree import *
from functools import cmp_to_key
import math 
import random
from tkinter import *
import copy

YSIZE = 1000
PSIZE = 4
EPS = 0.0000000001

# -----------------------------------------------------------------
# Event class for endpts and intersection pts in our event queue
# -----------------------------------------------------------------


class Event:
    def __init__(self, x, y, is_left=True, is_intersection=False, other_end=None, label=None, pl=None, ps=None, sl=None, ss=None):
        self.x = x
        self.y = y
        self.is_left = is_left
        self.is_intersection = is_intersection
        self.other_end = other_end
        self.label = label
        # fields for intersection events
        self.plabel=pl  # maybe this is predecessor label
        self.psegment=ps
        self.slabel=sl  # maybe this is successor label
        self.ssegment=ss

    def __str__(self):
        return str(self.label) + ' ' + str(self.plabel) + ' ' + str(self.slabel)


# -----------------------------------------------------------------
# checks if line segment p1p2 and p3p4 intersect
# -----------------------------------------------------------------
def feq(a, b):
    return (a-b) < EPS


def dist(a, b):
    return (a[0]-b[0]) * (a[0]-b[0]) + (a[1]-b[1]) * (a[1]-b[1])


def is_left(a, b, c):
    return (a[0]*b[1]) + (b[0]*c[1]) + (c[0]*a[1]) - (a[1]*b[0]) - (b[1]*c[0]) - (c[1]*a[0])


def on_segment(a, b, c):
    if (min(a[0], b[0]) < c[0] or feq(min(a[0], b[0]), c[0])) and (c[0] < max(a[0], b[0]) or feq(c[0], max(a[0], b[0]))):
        if (min(a[1], b[1]) < c[1] or feq(min(a[1], b[1]), c[1])) and (c[1] < max(a[1], b[1]) or feq(c[1], max(a[1], b[1]))):
            return True
    return False


def intersect(p1, p2, p3, p4):
    d1 = is_left(p1, p2, p3)
    d2 = is_left(p1, p2, p4)
    d3 = is_left(p3, p4, p1)
    d4 = is_left(p3, p4, p2)
    if (d1*d2) < 0 and (d3*d4) < 0:
        return True
    elif feq(d1, 0) and on_segment(p1, p2, p3):
        return True
    elif feq(d2, 0) and on_segment(p1, p2, p4):
        return True
    elif feq(d3, 0) and on_segment(p3, p4, p1):
        return True
    elif feq(d4, 0) and on_segment(p3, p4, p2):
        return True
    return False


def getA(p1, p2):
    return p1[1] - p2[1]

def getB(p1, p2):
    return p2[0] - p1[0]

def getC(p1, p2):
    return (p1[0] * p2[1]) - (p2[0] * p1[1])

def intersection_point(p1, p2, p3, p4):
    a1 = getA(p1, p2)
    b1 = getB(p1, p2)
    c1 = getC(p1, p2)
    a2 = getA(p3, p4)
    b2 = getB(p3, p4)
    c2 = getC(p3, p4)
    x = ((b1*c2) - (b2*c1)) / ((a1*b2) - (a2*b1))
    y = ((c1*a2) - (c2*a1)) / ((a1*b2) - (a2*b1))
    return (x, y)

# -----------------------------------------------------------------
# find_intersections callback
# -----------------------------------------------------------------
def find_intersections(event):
    global S
    Q = RedBlackTree()
    label = 0
    for s in S:
        if s[0][0] > s[1][0]:
            S[label] = (s[1], s[0])
            s = S[label]
        Q.insert(s[0][0], Event(s[0][0], s[0][1], True, False, s[1], label))
        Q.insert(s[1][0], Event(s[1][0], s[1][1], False, False, s[0], label))
        label += 1
  
    T = RedBlackTree()
    
    intersections = []
    
    while not Q.is_empty():
        min_node = Q.minimum()
        event = min_node.data
        Q.delete(min_node)
        if event.is_left:
            # print("left event")
            node = T.insert_segment(event.label, S[event.label])
            pred = T.predecessor(node)
            if pred and intersect(node.data[0], node.data[1], pred.data[0], pred.data[1]):
                int_pnt = intersection_point(node.data[0], node.data[1], pred.data[0], pred.data[1])
                Q.insert(int_pnt[0], Event(int_pnt[0], int_pnt[1], False, True, None, None, pred.key, None, event.label, None))
                # check for the other parameters in the event object
            succ = T.successor(node)
            if succ and intersect(node.data[0], node.data[1], succ.data[0], succ.data[1]):
                int_pnt = intersection_point(node.data[0], node.data[1], succ.data[0], succ.data[1])
                Q.insert(int_pnt[0], Event(int_pnt[0], int_pnt[1], False, True, None, None, event.label, None, succ.key, None))
                # check for the other parameters in the event object
            if pred and succ and intersect(succ.data[0], succ.data[1], pred.data[0], pred.data[1]):
                int_pnt = intersection_point(succ.data[0], succ.data[1], pred.data[0], pred.data[1])
                int_node = Q.search(int_pnt[0])
                if int_node and feq(int_node[1], int_pnt[1]):
                    Q.delete(int_node)

        elif not event.is_intersection:
            # print("right event")
            node = T.searchx(T.root, event.label)
            if node:
                pred = T.predecessor(node)
                succ = T.successor(node)
                if pred and succ and intersect(succ.data[0], succ.data[1], pred.data[0], pred.data[1]):
                    int_pnt = intersection_point(succ.data[0], succ.data[1], pred.data[0], pred.data[1])
                    Q.insert(int_pnt[0], Event(int_pnt[0], int_pnt[1], False, True, None, None, pred.key, None, succ.key, None))
                T.delete(node)

        else:
            # print("intersection event")
            intersections.append((event.x, event.y))
            n2 = T.searchx(T.root, event.plabel)
            n1 = T.searchx(T.root, event.slabel)
            if n1 and n2:
                T.swap(n1, n2)
            pred = T.predecessor(n1)
            if pred and intersect(n1.data[0], n1.data[1], pred.data[0], pred.data[1]):
                int_pnt = intersection_point(n1.data[0], n1.data[1], pred.data[0], pred.data[1])
                Q.insert(int_pnt[0], Event(int_pnt[0], int_pnt[1], False, True, None, None, pred.key, None, event.label, None))
            succ = T.successor(n2)
            if succ and intersect(n2.data[0], n2.data[1], succ.data[0], succ.data[1]):
                int_pnt = intersection_point(n2.data[0], n2.data[1], succ.data[0], succ.data[1])
                Q.insert(int_pnt[0], Event(int_pnt[0], int_pnt[1], False, True, None, None, event.label, None, succ.key, None))
            if n1 and succ and intersect(succ.data[0], succ.data[1], n1.data[0], n1.data[1]):
                int_pnt = intersection_point(succ.data[0], succ.data[1], n1.data[0], n1.data[1])
                int_node = Q.search(int_pnt[0])
                if int_node and feq(int_node[1], int_pnt[1]):
                    Q.delete(int_node)
            if pred and n2 and intersect(n2.data[0], n2.data[1], pred.data[0], pred.data[1]):
                int_pnt = intersection_point(n2.data[0], n2.data[1], pred.data[0], pred.data[1])
                int_node = Q.search(int_pnt[0])
                if int_node and feq(int_node[1], int_pnt[1]):
                    Q.delete(int_node)
    return intersections


def drawSegments(S):
    for s in S:
        drawLine(s[0], s[1], 'black')

def drawLine(p1, p2, color):
    p1 = (p1[0], YSIZE - p1[1])
    p2 = (p2[0], YSIZE - p2[1])
    canvas.create_line(p1, p2, fill=color)

def drawPoint(point):
    p = (point[0], YSIZE - point[1])
    canvas.create_oval(p[0] - PSIZE, p[1] - PSIZE, p[0] + PSIZE, p[1] + PSIZE, fill='red', w=2)


if __name__ == "__main__":
    # =========================================
    root = Tk()
    root.title("Segments")
    root.geometry(str(YSIZE)+'x'+str(YSIZE)) #("800x800")

    canvas = Canvas(root, width=YSIZE, height=YSIZE, bg='#FFF', highlightbackground="#999")
    canvas.bind("<Button-1>", find_intersections)
    canvas.grid(row=0, column=0)

    #S = [((20,50),(900,400)), ((80,500),(850,200))]
    S = [((random.randint(100, 900), random.randint(100, 900)),(random.randint(100, 900), random.randint(100, 900))) for _ in range(10)]

    print(S)
    find_intersections(None)
    drawSegments(S)

    root.mainloop()
