from .astar import astar
import matplotlib.pyplot as plt
import math
import numpy as np

import scipy as sp
import scipy.ndimage

from shapely.geometry import Point
from .Walker import Walker


class Blueprint:
    paths = {}
    fragrances = {}
    walkers = {}
    width = 300
    height = 300
    cellDimension = 15

    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.width = self.x2 - self.x1
        self.height = self.y2 - self.y1

    def setTranslation(self, x, y):
        self.xTranslation = x
        self.yTranslation = y

    def setCellDimension(self, dim, initMaze=True):
        self.cellDimension = dim
        if initMaze:
            self.initMaze()

    def initMaze(self):
        mazeX = math.floor(self.width / self.cellDimension)
        mazeY = math.floor(self.height / self.cellDimension)

        self.maze = np.zeros([mazeX, mazeY])
        self.empty()

    def defineMaze(self, walls):
        for i, row in enumerate(self.maze):
            for j, column in enumerate(row):
                px = (i + 1) * self.cellDimension - (self.cellDimension) / 2
                py = (j + 1) * self.cellDimension - (self.cellDimension) / 2
                pCheck = Point(px - self.xTranslation, py - self.yTranslation)

                for wall in walls:
                    if pCheck.within(wall.poly):
                        self.maze[i][j] = -1
                        break


    def transformPoint(self,cx,cy):
        newCX = int((cx+self.xTranslation) / self.cellDimension)
        newCY = int((cy+self.yTranslation) / self.cellDimension)
        return (newCX,newCY)

    def calcFragrance(self,start,idFrag=None):
        start = self.transformPoint(start['cx'],start['cy'])
        frag = Fragrance(start, self.maze,idFrag)

        self.fragrances[idFrag] = frag

    def calcPath(self, start, end, id=None):
        start = self.transformPoint(start['cx'],start['cy'])
        end   = self.transformPoint(end['cx'],end['cy'])

        p = Path(start, end, id)
        x_sigma = int(self.width / self.cellDimension)
        y_sigma = int(self.height / self.cellDimension)
        p.calcSigma(x_sigma, y_sigma)
        p.findBestPath(self.maze)
        p.createSniffingMap(self.maze)

        self.paths[p.id] = p

    def addWalker(self,start,pathIDs,walkerID=None):
        if not walkerID:
            walkerID = 'walker-'+str(len(self.walkers)+1)

        start = self.transformPoint(start['cx'],start['cy'])

        fragrances = [self.fragrances[fID] for fID in pathIDs]

        self.walkers[walkerID] = Walker(start,fragrances,walkerID)

    def empty(self):
        self.fragrances = {}
        self.paths = {}
        self.walkers = {}



def plotMaze(maze,displayVal=False):
    figure = plt.figure(figsize=[15, 15], dpi=90)

    plt.imshow(np.rot90(maze), cmap='plasma', interpolation='nearest')
    plt.xlabel("$x$")
    plt.ylabel("$y$")
    plt.gca().invert_yaxis()

    if displayVal:
        for (j, i), label in np.ndenumerate(np.rot90(maze)):
            plt.gca().text(i, j, int(label), ha='center', va='center')

    plt.show()

def plotSniffingMapPath(maze, path,title=None):
    preGrad = np.rot90(path.getPreGradientMap(maze))

    fig, ax = plt.subplots(1,2, figsize=[15, 15], dpi=90)

    plt.sca(ax[0])

    # Plot preGrad
    plt.imshow(preGrad, cmap='plasma', interpolation='nearest')
    plt.xlabel("$x$")
    plt.ylabel("$y$")
    plt.gca().invert_yaxis()

    plt.sca(ax[1])

    # Plot sniffing map
    plt.imshow(np.rot90(path.sniffingMap), cmap='plasma', interpolation='nearest')
    plt.xlabel("$x$")
    plt.ylabel("$y$")
    plt.title("$\sigma_x = " + str(path.sigmaX) + "\quad \sigma_y = " + str(path.sigmaY) + "$")
    plt.gca().invert_yaxis()

    if not title:
        title = path.id

    fig.suptitle(title, fontsize=16, y=0.72)

    plt.show()

def plotWalkerPathway(maze,walker,title=None):
    a = np.copy(maze)

    for i, (x, y) in enumerate(walker.pathway):
        a[x][y] = walker.pathway[i]*i

    figure = plt.figure(figsize=[15, 15], dpi=90)

    plt.imshow(np.rot90(a), cmap='plasma', interpolation='nearest')
    plt.xlabel("$x$")
    plt.ylabel("$y$")
    plt.gca().invert_yaxis()

    plt.show()


class Fragrance:

    maxDistance = 999
    mapWall     = -1

    def __init__(self, location, maze, id=None, init=True):
        self.location = location
        self.sniffingMap = np.copy(maze)
        self.maxDistance = maze.shape[0]*maze.shape[1]

        if id:
            self.id = id
        else:
            self.id = "p-" + str(location)

        if init:
            self.createSniffingMap()

    def createSniffingMap(self):
        distance = 0

        toEvaluate = [self.location]

        while len(toEvaluate):
            toEvaluateNext = []
            for position in toEvaluate:
                evalNeighbours = self.evalNeighbours(position, distance)
                if len(evalNeighbours):
                    if len(toEvaluateNext):
                        toEvaluateNext = np.concatenate((toEvaluateNext, evalNeighbours))
                    else:
                        toEvaluateNext = np.copy(evalNeighbours)

            toEvaluate = np.copy(toEvaluateNext)
            distance += 1


        # be sure that is float
        self.sniffingMap = self.sniffingMap.astype(float)

        # normalize non-wall from 1 to minDistance+1
        self.sniffingMap[self.sniffingMap>0]-=np.amin(self.sniffingMap[self.sniffingMap>self.mapWall])+1





    def evalNeighbours(self, position, distance):

        evaluated = []
        a = np.ones((3, 3)) * -1
        for i, r in enumerate(a):
            for j, c in enumerate(r):
                if i == 1 and j == 1:
                    continue
                try:
                    toMapX = -1 + j + position[0]
                    toMapY = 1 - i + position[1]

                    if toMapX < 0 or toMapY < 0:
                        continue

                    if self.sniffingMap[toMapX][toMapY] == 0:
                        self.sniffingMap[toMapX][toMapY] = self.maxDistance-(distance + 1)
                        evaluated.append((toMapX, toMapY))
                except IndexError:
                    continue

        return evaluated

class Path:
    preGradientF = -100
    mode = 'nearest'
    m_sigma = 0.035
    b_sigma = -0.1

    def __init__(self, start, end, id=None):
        self.start = start
        self.end = end
        self.path = None
        if id:
            self.id = id
        else:
            self.id = "p-" + str(start) + "-" + str(end)

    def _repr_html_(self):
        return "<h1>" + str(self.start) + "</h1>"

    def gradPathF(self,x):
        return x*x

    def calcSigma(self, x_sigma, y_sigma):
        self.sigmaX = self.m_sigma * x_sigma + self.b_sigma
        self.sigmaY = self.m_sigma * y_sigma + self.b_sigma

    def setPathGradFunction(self, f):
        self.gradPathF = f

    def findBestPath(self, maze):
        print("\t" + self.id + ": finding best path...")
        maze /= maze.max()
        self.path = astar(maze, self.start, self.end)
        self.createSniffingMap(maze, False)

    def getPreGradientMap(self, maze, toNormalize=True):
        a = np.copy(maze)
        if toNormalize:
            a /= maze.max()
        a *= self.preGradientF
        for i, (x, y) in enumerate(self.path):
            a[x][y] = self.gradPathF(i)

        return a

    def createSniffingMap(self, maze, toNormalize=True):
        mazePathMap = self.getPreGradientMap(maze, toNormalize)
        self.sniffingMap = sp.ndimage.filters \
            .gaussian_filter(mazePathMap, [self.sigmaX, self.sigmaY], mode=self.mode)