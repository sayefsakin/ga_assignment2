from RedBlackTree2 import *
from functools import cmp_to_key
import math 
import random
from tkinter import *
from datetime import datetime
import copy
import matplotlib.pyplot as plt

YSIZE = 750
PSIZE = 4

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


def dist(a, b):
    return math.sqrt((a[0]-b[0]) * (a[0]-b[0]) + (a[1]-b[1]) * (a[1]-b[1]))


def is_left(a, b, c):
    return (a[0]*b[1]) + (b[0]*c[1]) + (c[0]*a[1]) - (a[1]*b[0]) - (b[1]*c[0]) - (c[1]*a[0])


def on_segment(a, b, c):
    if (min(a[0], b[0]) < c[0] or feq(min(a[0], b[0]), c[0])) and (c[0] < max(a[0], b[0]) or feq(c[0], max(a[0], b[0]))):
        if (min(a[1], b[1]) < c[1] or feq(min(a[1], b[1]), c[1])) and (c[1] < max(a[1], b[1]) or feq(c[1], max(a[1], b[1]))):
            return True
    return False


def intersect(arc1, arc2):
    d = dist(arc1.data[0], arc2.data[0])
    if d > arc1.data[1] + arc2.data[1]:
        return False
    if d < abs(arc1.data[1] - arc2.data[1]):
        return False
    return True


def getA(p1, p2):
    return p1[1] - p2[1]

def getB(p1, p2):
    return p2[0] - p1[0]

def getC(p1, p2):
    return (p1[0] * p2[1]) - (p2[0] * p1[1])

def intersection_point_in_segmetns(p1, p2, p3, p4):
    a1 = getA(p1, p2)
    b1 = getB(p1, p2)
    c1 = getC(p1, p2)
    a2 = getA(p3, p4)
    b2 = getB(p3, p4)
    c2 = getC(p3, p4)
    x = ((b1*c2) - (b2*c1)) / ((a1*b2) - (a2*b1))
    y = ((c1*a2) - (c2*a1)) / ((a1*b2) - (a2*b1))
    return (x, y)

def intersection_point(arc1, arc2):
    d = dist(arc1.data[0], arc2.data[0])
    if feq(d, (arc1.data[1] + arc2.data[1])):
        x = arc1.data[0][0]
        return intersection_point_in_segmetns(arc1.data[0])

# -----------------------------------------------------------------
# find_intersections callback
# -----------------------------------------------------------------
def find_intersections(clickEvent):
    global S
    Q = RedBlackTree2()
    label = 0
    for s in S:
        S[label] = ((float(s[0][0]), float(s[0][1])), float(s[1]))
        Q.insert(s[0][0], Event(s[0][0] - s[1], s[0][1], True, False, s[1], label))  # other_end is radius
        Q.insert(s[1][0], Event(s[1][0] + s[1], s[1][1], False, False, s[1], label))  # other_end is radius
        label += 1
  
    T = RedBlackTree2()
    
    intersections = []
    
    while not Q.is_empty():
        min_node = Q.minimum()
        event = min_node.data
        Q.delete(min_node)
        if event.is_left:
            # print("left event")
            node = T.insert_segment(str(event.label) + '_top', S[event.label])
            # node = T.insert_segment(str(event.label) + '_top', S[event.label])
            pred = T.predecessor(node)
            if pred and intersect(node, pred):
                int_pnt = intersection_point(node, pred)
                if int_pnt[0] > event.x:
                    Q.insert(int_pnt[0], Event(int_pnt[0], int_pnt[1], False, True, None, None, pred.key, None, event.label, None))
                # check for the other parameters in the event object
            succ = T.successor(node)
            if succ and intersect(node.data[0], node.data[1], succ.data[0], succ.data[1]):
                int_pnt = intersection_point(node.data[0], node.data[1], succ.data[0], succ.data[1])
                if int_pnt[0] > event.x:
                    Q.insert(int_pnt[0], Event(int_pnt[0], int_pnt[1], False, True, None, None, event.label, None, succ.key, None))
                # check for the other parameters in the event object
            if pred and succ and intersect(succ.data[0], succ.data[1], pred.data[0], pred.data[1]):
                int_pnt = intersection_point(succ.data[0], succ.data[1], pred.data[0], pred.data[1])
                int_node = Q.search(int_pnt[0])
                if int_node and feq(int_node.data.y, int_pnt[1]):
                    Q.delete(int_node)

        elif not event.is_intersection:
            # print("right event")
            node = T.searchx(T.root, event.label)
            if node:
                pred = T.predecessor(node)
                succ = T.successor(node)
                if pred and succ and intersect(succ.data[0], succ.data[1], pred.data[0], pred.data[1]):
                    int_pnt = intersection_point(succ.data[0], succ.data[1], pred.data[0], pred.data[1])
                    if int_pnt[0] > event.x:
                        Q.insert(int_pnt[0], Event(int_pnt[0], int_pnt[1], False, True, None, None, pred.key, None, succ.key, None))
                T.delete(node)
            else:
                print('right endpoint node not found')

        else:
            # print("intersection event")
            intersections.append((event.x, event.y))
            n1 = T.searchx(T.root, event.plabel)
            n2 = T.searchx(T.root, event.slabel)
            if n1 and n2:
                T.swap(n1, n2)
            if n1:
                pred = T.predecessor(n1)
                if pred and intersect(n1.data[0], n1.data[1], pred.data[0], pred.data[1]):
                    int_pnt = intersection_point(n1.data[0], n1.data[1], pred.data[0], pred.data[1])
                    if int_pnt[0] > event.x:
                        Q.insert(int_pnt[0], Event(int_pnt[0], int_pnt[1], False, True, None, None, pred.key, None, event.slabel, None))
            if n2:
                succ = T.successor(n2)
                if succ and intersect(n2.data[0], n2.data[1], succ.data[0], succ.data[1]):
                    int_pnt = intersection_point(n2.data[0], n2.data[1], succ.data[0], succ.data[1])
                    if int_pnt[0] > event.x:
                        Q.insert(int_pnt[0], Event(int_pnt[0], int_pnt[1], False, True, None, None, event.plabel, None, succ.key, None))
            if n1 and succ and intersect(succ.data[0], succ.data[1], n1.data[0], n1.data[1]):
                int_pnt = intersection_point(succ.data[0], succ.data[1], n1.data[0], n1.data[1])
                int_node = Q.search(int_pnt[0])
                if int_node and feq(int_node.data.y, int_pnt[1]):
                    Q.delete(int_node)
            if pred and n2 and intersect(n2.data[0], n2.data[1], pred.data[0], pred.data[1]):
                int_pnt = intersection_point(n2.data[0], n2.data[1], pred.data[0], pred.data[1])
                int_node = Q.search(int_pnt[0])
                if int_node and feq(int_node.data.y, int_pnt[1]):
                    Q.delete(int_node)
    if clickEvent is not None:
        for ip in intersections:
            drawPoint(ip)
        return None
    return intersections


def drawCircles():
    global S
    for s in S:
        drawPoint(s[0])
        # drawLine(s[0], s[1], 'black')
        create_circle(s[0][0], s[0][1], s[1])

def create_circle(x, y, r): #center coordinates, radius
    x0 = x - r
    y0 = y - r
    x1 = x + r
    y1 = y + r
    return canvas.create_oval(x0, YSIZE - y0, x1, YSIZE - y1)

def drawLine(p1, p2, color):
    p1 = (p1[0], YSIZE - p1[1])
    p2 = (p2[0], YSIZE - p2[1])
    canvas.create_line(p1, p2, fill=color)

def drawPoint(point):
    p = (point[0], YSIZE - point[1])
    canvas.create_oval(p[0] - PSIZE, p[1] - PSIZE, p[0] + PSIZE, p[1] + PSIZE, fill='red', w=2)


def generateRandomCircles(sc):
    global S
    minRadius = 30
    maxRadius = 80
    S = [((random.randint(minRadius, YSIZE - minRadius), random.randint(minRadius, YSIZE-minRadius)), random.randint(minRadius, maxRadius)) for _ in range(sc)]



def plot_line(x_points, y_points1):
    plt.plot(x_points, y_points1, color='green', label='output-time')
    # plt.plot(x_points, y_points2, color="red", label="Andrews Scan")
    # plt.plot(x_points, y_points3, color="blue", label="Divide and Conquer")
    spacing = 50
    plt.xlim([min(x_points) - spacing, max(x_points) + spacing])
    plt.title('Bentley-Ottmann')
    plt.xlabel('Number of Intersections')
    plt.ylabel('Time (ms)')
    plt.legend()
    plt.grid()
    plt.show()


def estimateTime():
    max_points = 20
    cp_bf_x = list()
    cp_bf_y = list()
    cp = list()
    for n_points in range(max_points):
        generateRandomSegments(50)
        begin_time = datetime.now().timestamp() * 1000
        I = find_intersections(None)
        time_taken = (datetime.now().timestamp() * 1000) - begin_time
        cp_bf_y.append(time_taken)
        cp_bf_x.append(len(I))
        cp.append({'time': time_taken, 'ip': len(I)})
    cp = sorted(cp, key=lambda x: x['ip'])
    plot_line([d['ip'] for d in cp], [d['time'] for d in cp])


if __name__ == "__main__":
    # =========================================
    root = Tk()
    root.title("Segments")
    root.geometry(str(YSIZE)+'x'+str(YSIZE)) #("800x800")

    canvas = Canvas(root, width=YSIZE, height=YSIZE, bg='#FFF', highlightbackground="#999")
    # canvas.bind("<Button-1>", find_intersections)
    canvas.grid(row=0, column=0)

    generateRandomCircles(5)
    drawCircles()
    I = find_intersections(None)
    root.mainloop()

    # estimateTime()