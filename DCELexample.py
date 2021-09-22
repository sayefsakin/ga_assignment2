import copy

import seg_inter
from RedBlackTree import *
from DCEL import *
import math 
import random
from tkinter import *

YSIZE = 1000
PSIZE = 4
colors = ['red', 'green', 'blue', 'yellow']
color_idx = 0


def find_intersections(event):
    global myDCEL
    distinct_seg_sets = []
    plain_seg = []
    for i in range(0, len(myDCEL.faces), 2):  # only take inner or outer face, not both
        seg_sets = []
        h = myDCEL.faces[i].halfEdge
        segs1 = []
        segs2 = []
        segs3 = []
        count = 0
        while (h.next != myDCEL.faces[i].halfEdge):
            c_seg = ((h.tail.x, h.tail.y), (h.next.tail.x, h.next.tail.y))
            if count == 0:
                segs1.append(c_seg)
                count = 1
            elif count == 1:
                segs2.append(c_seg)
                count = 0
            plain_seg.append(c_seg)
            h = h.next
        c_seg = ((h.tail.x, h.tail.y), (h.next.tail.x, h.next.tail.y))
        if count == 0:
            segs3.append(c_seg)
        elif count == 1:
            segs2.append(c_seg)
        plain_seg.append(c_seg)
        if len(segs1):
            seg_sets.append(segs1)
        if len(segs2):
            seg_sets.append(segs2)
        if len(segs3):
            seg_sets.append(segs3)
        distinct_seg_sets.append(seg_sets)
    # print(distinct_seg_sets)
    # drawSegments(segs)
    original_vertics = copy.deepcopy(myDCEL.vertices)
    find_inters(distinct_seg_sets)
    for ep in original_vertics:
        drawPoint((ep.x, ep.y))
    # drawSegments(plain_seg)
    # find_inters(plain_seg)

def find_inters(dis_S):
    I = []
    IS = []
    for first_sets in dis_S[0]:
        for second_sets in dis_S[1]:
            S = first_sets + second_sets
            new_inter = seg_inter.find_intersections(S)
            if len(new_inter) > 0:
                I.extend(new_inter)
    # #
    # print("find_intersections")
    # print("------------------")
    # print("segments:")
    # print(dis_S)
    # I = seg_inter.find_intersections(dis_S)
    print("intersections: ", len(I))
    # print(I)
    global myDCEL
    for ind, ip in enumerate(I):
        myDCEL.addNewVertex(ip[0], ip[1][0], ip[1][1], ip[2][0], ip[2][1])
        for j, other_ip in enumerate(I[ind+1:], start=ind+1):
            if ip[1] == other_ip[1] or ip[2] == other_ip[1]:
                if seg_inter.on_segment(ip[0], other_ip[1][0], other_ip[0]):
                    other_ip[1] = (other_ip[1][0], ip[0])
                if seg_inter.on_segment(ip[0], other_ip[1][1], other_ip[0]):
                    other_ip[1] = (ip[0], other_ip[1][1])
            elif ip[1] == other_ip[2] or ip[2] == other_ip[2]:
                if seg_inter.on_segment(ip[0], other_ip[2][0], other_ip[0]):
                    other_ip[2] = (other_ip[2][0], ip[0])
                if seg_inter.on_segment(ip[0], other_ip[2][1], other_ip[0]):
                    other_ip[2] = (ip[0], other_ip[2][1])
    myDCEL.updateFaces()
    drawFaces(myDCEL)
    for ip in I:
        drawPoint(ip[0], 'blue')

def drawSegments(S):
    for s in S:
        drawLine(s[0], s[1], 'black')

def drawFaces(dcel):
    global color_idx
    for f in dcel.faces:
        print('polygon')
        verts = []
        h = f.halfEdge
        while (h.next != f.halfEdge):
            print((h.tail.x, h.tail.y), end="->")
            verts.append(h.tail.x)
            verts.append(YSIZE - h.tail.y)
            h = h.next
        print((h.tail.x, h.tail.y))
        verts.append(h.tail.x)
        verts.append(YSIZE - h.tail.y)
        print('\nverts ', verts)
        canvas.create_polygon(verts, outline='black', fill=colors[color_idx], width=2)
        color_idx = (color_idx + 1) % 4
        print('\n')

def drawLine(p1, p2, color):
    p1 = (p1[0], YSIZE - p1[1])
    p2 = (p2[0], YSIZE - p2[1])
    canvas.create_line(p1, p2, fill=color)

def drawPoint(point, color='red'):
    p = (point[0], YSIZE - point[1])
    canvas.create_oval(p[0] - PSIZE, p[1] - PSIZE, p[0] + PSIZE, p[1] + PSIZE, fill=color, w=2)

def makeRandomSegment(sc, spacing=50):
    def andrews_scan(points):
        convex_hull = list()
        sorted_points = sorted(points, key=lambda op: (op[0], op[1]))
        # lower hull
        for i, p in enumerate(sorted_points):
            while len(convex_hull) >= 2 and seg_inter.is_left(convex_hull[-2], convex_hull[-1], p) <= 0:
                convex_hull.pop()
            convex_hull.append(p)

        lower_hull_size = len(convex_hull)
        # upper hull
        for p in reversed(sorted_points):
            while len(convex_hull) >= lower_hull_size and seg_inter.is_left(convex_hull[-2], convex_hull[-1], p) <= 0:
                convex_hull.pop()
            convex_hull.append(p)
        return convex_hull

    CP = [(random.randint(spacing, YSIZE-spacing), random.randint(spacing, YSIZE-spacing)) for _ in range(sc)]
    P = andrews_scan(CP)
    S = []
    for i, p in enumerate(P):
        next_p = i + 1
        if next_p >= len(P):
            break
        S.append([p, P[next_p]])
    return P[:len(P)-1], S

if __name__ == "__main__":
    # =========================================
    root = Tk()
    root.title("DCEL Test")
    root.geometry(str(YSIZE)+'x'+str(YSIZE)) #("800x800")

    canvas = Canvas(root, width=YSIZE, height=YSIZE, bg='#FFF', highlightbackground="#999")
    canvas.bind("<Button-1>", find_intersections)
    canvas.grid(row=0, column=0)

    # P1, S1 = makeRandomSegment(100, 100)
    # P2, S2 = makeRandomSegment(100, 100)
    # make nested convex polygons
    # P11, S11 = makeRandomSegment(10)
    # P12, S12 = makeRandomSegment(10)
    #
    # P21, S21 = makeRandomSegment(10)
    # P22, S22 = makeRandomSegment(10)
    #
    # P1 = P11 + P12
    # S1 = S11 + S12
    #
    # P2 = P21 + P22
    # S2 = S21 + S22

    # P1 = [(100, 500), (250, 190), (400, 800), (600, 200), (100, 100)]
    #
    # S1 = [[ P1[0], P1[1]],
    #       [ P1[1], P1[2]],
    #       [ P1[2], P1[3]],
    #       [ P1[3], P1[4]],
    #       [ P1[4], P1[0]],
    #     ]
    P1 = [(100, 500), (400, 800), (600, 200), (110, 100)]

    S1 = [[ P1[0], P1[1]],
         [ P1[1], P1[2]],
         [ P1[2], P1[3]],
         [ P1[3], P1[0]],
        ]

    # myDCEL = DCEL()
    # myDCEL.build_dcel(P1, S1)
    #drawFaces(myDCEL)


    P2 = [(500, 900), (700, 800), (350, 100), (200, 500)]

    S2 = [[ P2[0], P2[1]],
         [ P2[1], P2[2]],
         [ P2[2], P2[3]],
         [ P2[3], P2[0]],
        ]

    # myDCEL = DCEL()
    # myDCEL.build_dcel(P2, S2)
    # drawFaces(myDCEL)
    global P3
    global S3

    P3 = P1.copy()
    P3.extend(P2)
    S3 = S1.copy()
    S3.extend(S2)
    #
    myDCEL = DCEL()
    myDCEL.build_dcel(P3, S3)
    drawFaces(myDCEL)
    #
    # # for f in myDCEL.faces:
    # #     print(f.name)
    # # print(myDCEL.faces[0].name)

    root.mainloop()

