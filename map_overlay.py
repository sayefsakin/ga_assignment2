from RedBlackTree import *
from DCEL import *


def

if __name__ == "__main__":
    P1 = [(100, 500), (400, 800), (600, 200), (100, 100)]
    S1 = [[P1[0], P1[1]],
          [P1[1], P1[2]],
          [P1[2], P1[3]],
          [P1[3], P1[0]],
          ]

    P2 = [(500, 900), (700, 800), (350, 100), (200, 500)]
    S2 = [[ P2[0], P2[1]],
          [ P2[1], P2[2]],
          [ P2[2], P2[3]],
          [ P2[3], P2[0]],
          ]


    P3 = P1.copy()
    P3.extend(P2)
    S3 = S1.copy()
    S3.extend(S2)

    # drawSegments(S3)
    myDCEL = DCEL()
    myDCEL.build_dcel(P3, S3)


