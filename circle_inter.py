from RedBlackTree import *
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
    if arc1 == arc2:
        return False
    if arc1.data[0][0] == arc2.data[0][0] and arc1.data[0][1] == arc2.data[0][1] and arc1.data[1] == arc2.data[1]:
        return False
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

def getCirlceIntersection(c1, c2):
    x1 = c1[0][0]
    y1 = c1[0][1]
    r1 = c1[1]
    x2 = c2[0][0]
    y2 = c2[0][1]
    r2 = c2[1]
    d = dist((x1, y1), (x2, y2))
    if feq(d, 0.0):
        return None, None
    l = ((r1*r1) - (r2*r2) + (d*d)) / (2*d)
    h = math.sqrt((r1*r1)-(l*l))
    Ax = (x2-x1)*l/d
    Bx = (y2-y1)*h/d
    Ay = (y2-y1)*l/d
    By = (x2-x1)*h/d
    p1 = (Ax + Bx + x1, Ay - By + y1)
    p2 = (Ax - Bx + x1, Ay + By + y1)
    return p1, p2

def isOnCricle(c, p):
    return feq((((p[0] - c[0][0]) * (p[0] - c[0][0])) + ((p[1] - c[0][1]) * (p[1] - c[0][1]))), (c[1]*c[1]))

def intersection_point(arc1, arc2):
    p1, p2 = getCirlceIntersection(arc1.data, arc2.data)
    if p1 and p2 and p1[0] == p2[0] and p1[1] == p2[1]:
        global intersections
        intersections.append(p1)
        return p1, None, False
    if p1 and isOnCricle(arc1.data, p1) is False:
        p1 = None
    elif p1 and ('_top' in arc1.key and p1[1] < arc1.data[0][1]) or ('_bottom' in arc1.key and p1[1] > arc1.data[0][1]):
        p1 = None
    elif p1 and ('_top' in arc2.key and p1[1] < arc2.data[0][1]) or ('_bottom' in arc2.key and p1[1] > arc2.data[0][1]):
        p1 = None

    if p2 and isOnCricle(arc1.data, p2) is False:
        p2 = None
    elif p2 and ('_top' in arc1.key and p2[1] < arc1.data[0][1]) or ('_bottom' in arc1.key and p2[1] > arc1.data[0][1]):
        p2 = None
    elif p2 and ('_top' in arc2.key and p2[1] < arc2.data[0][1]) or ('_bottom' in arc2.key and p2[1] > arc2.data[0][1]):
        p2 = None

    return p1, p2, True

# -----------------------------------------------------------------
# find_intersections callback
# -----------------------------------------------------------------
def find_intersections_wrapper(clickEvent):
    global S
    intersections = find_intersections(S)
    if clickEvent is not None:
        for ip in intersections:
            drawPoint(ip, 'blue')
    print('circles:')
    print(S)
    print('intersection points: ', len(intersections))
    print(intersections)

def find_intersections(S):
    Q = RedBlackTree()
    label = 0
    for s in S:
        S[label] = ((float(s[0][0]), float(s[0][1])), float(s[1]))
        Q.insert(s[0][0] - s[1], Event(s[0][0] - s[1], s[0][1], True, False, s[1], label))  # other_end is radius
        Q.insert(s[0][0] + s[1], Event(s[0][0] + s[1], s[0][1], False, False, s[1], label))  # other_end is radius
        label += 1
  
    T = RedBlackTree()

    global intersections
    intersections = []
    
    while not Q.is_empty():
        min_node = Q.minimum()
        event = min_node.data
        Q.delete(min_node)
        if event.is_left:
            # print("left event")
            node1 = T.insert_circle(str(event.label) + '_top', S[event.label])
            node2 = T.insert_circle(str(event.label) + '_bottom', S[event.label])
            pred = T.predecessor(node2)
            if pred and intersect(node2, pred):
                int_pnt, int_pnt2, is_only = intersection_point(node2, pred)
                if is_only and int_pnt:
                    if int_pnt[0] > event.x:
                        Q.insert(int_pnt[0], Event(int_pnt[0], int_pnt[1], False, True, None, None, pred.key, None, node2.key, None))
                if is_only and int_pnt2:
                    if int_pnt2[0] > event.x:
                        Q.insert(int_pnt2[0], Event(int_pnt2[0], int_pnt2[1], False, True, None, None, pred.key, None, node2.key, None))
                # check for the other parameters in the event object
            succ = T.successor(node1)
            if succ and intersect(node1, succ):
                int_pnt, int_pnt2, is_only = intersection_point(node1, succ)
                if is_only and int_pnt:
                    if int_pnt[0] > event.x:
                        Q.insert(int_pnt[0], Event(int_pnt[0], int_pnt[1], False, True, None, None, node1.key, None, succ.key, None))
                if is_only and int_pnt2:
                    if int_pnt2[0] > event.x:
                        Q.insert(int_pnt2[0], Event(int_pnt2[0], int_pnt2[1], False, True, None, None, node1.key, None, succ.key, None))
                # check for the other parameters in the event object
            if pred and succ and intersect(succ, pred):
                int_pnt, int_pnt2, is_only = intersection_point(succ, pred)
                if is_only and int_pnt:
                    int_node = Q.search(int_pnt[0])
                    if int_node and int_node.data.is_intersection and feq(int_node.data.y, int_pnt[1]):
                        Q.delete(int_node)
                if is_only and int_pnt2:
                    int_node = Q.search(int_pnt2[0])
                    if int_node and int_node.data.is_intersection and feq(int_node.data.y, int_pnt2[1]):
                        Q.delete(int_node)

        elif not event.is_intersection:
            # print("right event")
            node = T.searchx(T.root, str(event.label) + '_top')
            if node:
                pred = T.predecessor(node)
                succ = T.successor(node)
                if pred and succ and intersect(succ, pred):
                    int_pnt, int_pnt2, is_only = intersection_point(succ, pred)
                    if is_only and int_pnt:
                        if int_pnt[0] > event.x:
                            Q.insert(int_pnt[0], Event(int_pnt[0], int_pnt[1], False, True, None, None, pred.key, None, succ.key, None))
                    if is_only and int_pnt2:
                        if int_pnt2[0] > event.x:
                            Q.insert(int_pnt2[0], Event(int_pnt2[0], int_pnt2[1], False, True, None, None, pred.key, None, succ.key, None))
                T.delete(node)
            else:
                print('right endpoint node not found')

            node = T.searchx(T.root, str(event.label) + '_bottom')
            if node:
                pred = T.predecessor(node)
                succ = T.successor(node)
                if pred and succ and intersect(succ, pred):
                    int_pnt, int_pnt2, is_only = intersection_point(succ, pred)
                    if is_only and int_pnt:
                        if int_pnt[0] > event.x:
                            Q.insert(int_pnt[0], Event(int_pnt[0], int_pnt[1], False, True, None, None, pred.key, None, succ.key, None))
                    if is_only and int_pnt2:
                        if int_pnt2[0] > event.x:
                            Q.insert(int_pnt2[0], Event(int_pnt2[0], int_pnt2[1], False, True, None, None, pred.key, None, succ.key, None))
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
                if pred and intersect(n1, pred):
                    int_pnt, int_pnt2, is_only = intersection_point(n1, pred)
                    if is_only and int_pnt:
                        if int_pnt[0] > event.x:
                            Q.insert(int_pnt[0], Event(int_pnt[0], int_pnt[1], False, True, None, None, pred.key, None, n1.key, None))
                    if is_only and int_pnt2:
                        if int_pnt2[0] > event.x:
                            Q.insert(int_pnt2[0], Event(int_pnt2[0], int_pnt2[1], False, True, None, None, pred.key, None, n1.key, None))
            if n2:
                succ = T.successor(n2)
                if succ and intersect(n2, succ):
                    int_pnt, int_pnt2, is_only = intersection_point(n2, succ)
                    if is_only and int_pnt:
                        if int_pnt[0] > event.x:
                            Q.insert(int_pnt[0], Event(int_pnt[0], int_pnt[1], False, True, None, None, n2.key, None, succ.key, None))
                    if is_only and int_pnt2:
                        if int_pnt2[0] > event.x:
                            Q.insert(int_pnt2[0], Event(int_pnt2[0], int_pnt2[1], False, True, None, None, n2.key, None, succ.key, None))
            if n1 and succ and intersect(succ, n1):
                int_pnt, int_pnt2, is_only = intersection_point(succ, n1)
                if int_pnt:
                    int_node = Q.search(int_pnt[0])
                    if int_node and feq(int_node.data.y, int_pnt[1]):
                        Q.delete(int_node)
                if int_pnt2:
                    int_node = Q.search(int_pnt2[0])
                    if int_node and feq(int_node.data.y, int_pnt2[1]):
                        Q.delete(int_node)
            if pred and n2 and intersect(n2, pred):
                int_pnt, int_pnt2, is_only = intersection_point(n2, pred)
                if int_pnt:
                    int_node = Q.search(int_pnt[0])
                    if int_node and feq(int_node.data.y, int_pnt[1]):
                        Q.delete(int_node)
                if int_pnt2:
                    int_node = Q.search(int_pnt2[0])
                    if int_node and feq(int_node.data.y, int_pnt2[1]):
                        Q.delete(int_node)
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

def drawPoint(point, color='red'):
    p = (point[0], YSIZE - point[1])
    canvas.create_oval(p[0] - PSIZE, p[1] - PSIZE, p[0] + PSIZE, p[1] + PSIZE, fill=color, w=2)


def generateRandomCircles(sc):
    global S
    minRadius = 30
    maxRadius = 80
    # S = [((random.randint(maxRadius, YSIZE - maxRadius), random.randint(maxRadius, YSIZE-maxRadius)), random.randint(minRadius, maxRadius)) for _ in range(sc)]
    # S = [((376.0, 453.0), 78.0), ((327.0, 373.0), 54.0), ((274.0, 297.0), 49.0), ((422.0, 583.0), 64.0), ((423.0, 373.0), 51.0), ((538.0, 625.0), 72.0), ((342.0, 279.0), 30.0), ((559.0, 548.0), 59.0)]
    S = [((327.0, 373.0), 54.0), ((274.0, 297.0), 49.0), ((342.0, 279.0), 30.0)]



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

#
# def estimateTime():
#     max_points = 20
#     cp_bf_x = list()
#     cp_bf_y = list()
#     cp = list()
#     for n_points in range(max_points):
#         generateRandomSegments(50)
#         begin_time = datetime.now().timestamp() * 1000
#         I = find_intersections(None)
#         time_taken = (datetime.now().timestamp() * 1000) - begin_time
#         cp_bf_y.append(time_taken)
#         cp_bf_x.append(len(I))
#         cp.append({'time': time_taken, 'ip': len(I)})
#     cp = sorted(cp, key=lambda x: x['ip'])
#     plot_line([d['ip'] for d in cp], [d['time'] for d in cp])


if __name__ == "__main__":
    # =========================================
    root = Tk()
    root.title("Segments")
    root.geometry(str(YSIZE)+'x'+str(YSIZE)) #("800x800")

    canvas = Canvas(root, width=YSIZE, height=YSIZE, bg='#FFF', highlightbackground="#999")
    canvas.bind("<Button-1>", find_intersections_wrapper)
    canvas.grid(row=0, column=0)

    generateRandomCircles(10)
    drawCircles()

    # def is_intersect(arc1, arc2):
    #     d = dist(arc1[0], arc2[0])
    #     if d > arc1[1] + arc2[1]:
    #         return False
    #     if d < abs(arc1[1] - arc2[1]):
    #         return False
    #     return True
    #
    # global S
    # for i, c1 in enumerate(S):
    #     for j, c2 in enumerate(S[i+1:], start=i+1):
    #         if is_intersect(c1, c2):
    #             p1, p2 = getCirlceIntersection(c1, c2)
    #             drawPoint(p1)
    #             drawPoint(p2)

    root.mainloop()
