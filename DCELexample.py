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
    for i in range(0, len(myDCEL.faces), 2):  # only take inner or outer face, not both
        seg_sets = []
        h = myDCEL.faces[i].halfEdge
        segs1 = []
        segs2 = []
        segs3 = []
        count = 0
        while (h.next != myDCEL.faces[i].halfEdge):
            if count == 0:
                segs1.append(((h.tail.x, h.tail.y), (h.next.tail.x, h.next.tail.y)))
                count = 1
            elif count == 1:
                segs2.append(((h.tail.x, h.tail.y), (h.next.tail.x, h.next.tail.y)))
                count = 0
            h = h.next
        if count == 0:
            segs3.append(((h.tail.x, h.tail.y), (h.next.tail.x, h.next.tail.y)))
        elif count == 1:
            segs2.append(((h.tail.x, h.tail.y), (h.next.tail.x, h.next.tail.y)))
        if len(segs1):
            seg_sets.append(segs1)
        if len(segs2):
            seg_sets.append(segs2)
        if len(segs3):
            seg_sets.append(segs3)
        distinct_seg_sets.append(seg_sets)
    # print(distinct_seg_sets)
    # drawSegments(segs)
    find_inters(distinct_seg_sets)

def find_inters(dis_S):
    print("find_inters")  # code from Q1
    I = []
    for first_sets in dis_S[0]:
        for second_sets in dis_S[1]:
            S = first_sets + second_sets
            new_inter = seg_inter.find_intersections(S)
            if len(new_inter) > 0:
                I.extend(new_inter)
    print(I)
    for ip in I:
        drawPoint(ip)
    
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

def drawPoint(point):
    p = (point[0], YSIZE - point[1])
    canvas.create_oval(p[0] - PSIZE, p[1] - PSIZE, p[0] + PSIZE, p[1] + PSIZE, fill='red', w=2)

if __name__ == "__main__":
    # =========================================
    root = Tk()
    root.title("DCEL Test")
    root.geometry(str(YSIZE)+'x'+str(YSIZE)) #("800x800")

    canvas = Canvas(root, width=YSIZE, height=YSIZE, bg='#FFF', highlightbackground="#999")
    canvas.bind("<Button-1>", find_intersections)
    canvas.grid(row=0, column=0)


    P1 = [(100, 500), (250, 190), (400, 800), (600, 200), (100, 100)]

    S1 = [[ P1[0], P1[1]],
          [ P1[1], P1[2]],
          [ P1[2], P1[3]],
          [ P1[3], P1[4]],
          [ P1[4], P1[0]],
        ]
    # P1 = [(100, 500), (400, 800), (600, 200), (100, 100)]
    #
    # S1 = [[ P1[0], P1[1]],
    #      [ P1[1], P1[2]],
    #      [ P1[2], P1[3]],
    #      [ P1[3], P1[0]],
    #     ]

    #myDCEL = DCEL()
    #myDCEL.build_dcel(P1, S1)
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


    P3 = P1.copy()
    P3.extend(P2)
    S3 = S1.copy()
    S3.extend(S2)

    # drawSegments(S3)
    myDCEL = DCEL()
    myDCEL.build_dcel(P3, S3)
    drawFaces(myDCEL)

    # for f in myDCEL.faces:
    #     print(f.name)
    # print(myDCEL.faces[0].name)

    root.mainloop()

