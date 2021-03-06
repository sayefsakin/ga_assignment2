from RedBlackTree import *
import random
from tkinter import *
from datetime import datetime
import matplotlib.pyplot as plt

YSIZE = 800
PSIZE = 4
isFirstClick = False

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
        self.plabel = pl
        self.psegment = ps
        self.slabel = sl
        self.ssegment = ss

    def __str__(self):
        return str(self.label) + ' ' + str(self.plabel) + ' ' + str(self.slabel)


# -----------------------------------------------------------------
# checks if line segment p1p2 and p3p4 intersect
# -----------------------------------------------------------------
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
    elif feq(d1, 0.0) and on_segment(p1, p2, p3):
        return True
    elif feq(d2, 0.0) and on_segment(p1, p2, p4):
        return True
    elif feq(d3, 0.0) and on_segment(p3, p4, p1):
        return True
    elif feq(d4, 0.0) and on_segment(p3, p4, p2):
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
def find_intersections_wrapper(clickEvent):
    global isFirstClick
    global root
    if isFirstClick is True:
        root.destroy()
        return
    isFirstClick = True

    global S
    intersections = find_intersections(S)
    if clickEvent is not None:
        for ip in intersections:
            drawPoint(ip[0])


def find_intersections(S):
    Q = RedBlackTree()
    S = makeSegmentXDistinct(S)
    label = 0
    for s in S:
        S[label] = ((float(s[0][0]), float(s[0][1])), (float(s[1][0]), float(s[1][1])))
        if s[0][0] > s[1][0]:
            S[label] = ((float(s[1][0]), float(s[1][1])), (float(s[0][0]), float(s[0][1])))
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
            intersections.append([(event.x, event.y), S[event.plabel], S[event.slabel]])
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
    return intersections


def drawSegments():
    global S
    for s in S:
        drawLine(s[0], s[1], 'black')


def drawLine(p1, p2, color):
    p1 = (p1[0], YSIZE - p1[1])
    p2 = (p2[0], YSIZE - p2[1])
    canvas.create_line(p1, p2, fill=color)


def drawPoint(point):
    p = (point[0], YSIZE - point[1])
    canvas.create_oval(p[0] - PSIZE, p[1] - PSIZE, p[0] + PSIZE, p[1] + PSIZE, fill='red', w=2)


def makeSegmentXDistinct(S):
    while True:
        equalNotFound = True
        for i, s in enumerate(S):
            if feq(s[0][0], s[1][0]):
                equalNotFound = False
                S[i] = ((float(s[0][0]) + 0.9, s[0][1]), s[1])
            for j, t in enumerate(S[i+1:], start=i+1):
                if feq(s[0][0], t[0][0]) or feq(s[0][0], t[1][0]):
                    equalNotFound = False
                    S[i] = ((float(s[0][0]) + 0.9, s[0][1]), s[1])
                if feq(s[1][0], t[0][0]) or feq(s[1][0], t[1][0]):
                    equalNotFound = False
                    S[i] = (s[0], (float(s[1][0]) + 0.9, s[1][1]))
        if equalNotFound:
            break
    return S


def generateRandomSegments(sc):
    global S
    spacing = 50
    S = [((random.randint(spacing, YSIZE-spacing), random.randint(spacing, YSIZE-spacing)),
          (random.randint(spacing, YSIZE-spacing), random.randint(spacing, YSIZE-spacing))) for _ in range(sc)]
    # S = makeSegmentXDistinct(S)


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
        global S
        I = find_intersections(S)
        time_taken = (datetime.now().timestamp() * 1000) - begin_time
        cp_bf_y.append(time_taken)
        cp_bf_x.append(len(I))
        cp.append({'time': time_taken, 'ip': len(I)})
    cp = sorted(cp, key=lambda x: x['ip'])
    plot_line([d['ip'] for d in cp], [d['time'] for d in cp])


if __name__ == "__main__":
    number_of_segments = 10
    if len(sys.argv) > 1:
        number_of_segments = int(sys.argv[1])
    # =========================================
    root = Tk()
    root.title("Segments")
    root.geometry(str(YSIZE)+'x'+str(YSIZE)) #("800x800")

    canvas = Canvas(root, width=YSIZE, height=YSIZE, bg='#FFF', highlightbackground="#999")
    canvas.bind("<Button-1>", find_intersections_wrapper)
    canvas.grid(row=0, column=0)

    generateRandomSegments(number_of_segments)
    drawSegments()
    root.mainloop()

    # estimateTime()