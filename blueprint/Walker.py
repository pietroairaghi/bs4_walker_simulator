import random
from shapely.geometry.point import Point
import numpy as np


def probDistr(n, predictability=0.45):
    arr = []
    for x in range(1, n + 1):
        p = -((2.5 * predictability) ** 3) * (x - 1) + 10
        if p < 0:
            p = 0
        arr.append(p)
    return [float(i) / sum(arr) for i in arr]


class Walker:
    pathway = []
    steps = 0
    predictability = 0.05
    currentPath = None
    currentI    = 1
    maxSteps = 10000

    def __init__(self, start, paths, name):
        self.id = name
        self.currentPosition = start
        self.start = start
        self.end = paths[-1].location
        self.paths = paths
        self.pathway = []

    def startWalking(self):
        for path in self.paths:
            self.updatePosition()
            self.currentPath = path
            self.followSniffingPath()
            self.currentI+=1

    def getRandomDirection(self, path=None):
        if not path:
            path = self.currentPath

        # get points around the current pos
        a = np.ones((3, 3)) * -1
        for i, r in enumerate(a):
            for j, c in enumerate(r):
                if i == 1 and j == 1:
                    continue
                try:
                    toMapX = -1 + j + self.currentPosition[0]
                    toMapY = 1 - i + self.currentPosition[1]
                    if toMapX <0 or toMapY<0:
                        continue
                    a[i][j] = path.sniffingMap[toMapX][toMapY]
                except IndexError:
                    a[i][j] = -10

        # get the random direction based on the predicibility
        n = np.random.choice(np.arange(1, 9), p=probDistr(8, self.predictability))
        largest = a.flatten().argsort()[-n:][::-1]

        iNeg = len(largest)
        for ix, i in enumerate(largest):
            rowI = int(i / 3)
            colI = i % 3
            val = a[rowI][colI]
            if val < 0:
                iNeg = ix
                break

        possibleDirections = largest[:iNeg]  # avoid negative numbers
        selectedDirection = possibleDirections[random.randint(0, len(possibleDirections) - 1)]

        return (int(selectedDirection / 3), selectedDirection % 3)

    def updatePosition(self, direction=(1, 1)):
        self.currentPosition = (self.currentPosition[0] - 1 + direction[1],
                                self.currentPosition[1] + 1 - direction[0])
        self.pathway.append(self.currentPosition)




    def followSniffingPath(self):
        i = 0
        while True:

            arrived = Point(self.currentPosition[0], self.currentPosition[1]) \
                .within(Point(self.currentPath.location[0], self.currentPath.location[1]).buffer(5.0))

            if arrived:
                if self.currentI >= len(self.paths):
                    break
                if random.random()*100 > 80:
                    break

            if i > self.maxSteps:
                print("reached max step for a walker")
                break
            direction = (self.getRandomDirection())
            self.updatePosition(direction)
            i += 1
