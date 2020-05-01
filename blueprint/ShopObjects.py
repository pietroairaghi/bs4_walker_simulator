from shapely.geometry import Point, Polygon

class Wall:
    def __init__(self, x, y, width, height, matrix=False, scale=False):
        self.id = 'no_id'
        self.topLeft = {'x': x, 'y': y}
        self.topRight = {'x': x + width, 'y': y}
        self.bottomLeft = {'x': x, 'y': y + height}
        self.bottomRight = {'x': x + width, 'y': y + height}
        self.initPolygonObject()

        if matrix:
            self.matrixTransform(matrix)

        if scale:
            self.scaleTransform(scale)

    def __str__(self):
        return str(self.__dict__)

    def initPolygonObject(self):
        coords = [(self.topLeft['x'], self.topLeft['y']),
                  (self.topRight['x'], self.topRight['y']),
                  (self.bottomRight['x'], self.bottomRight['y']),
                  (self.bottomLeft['x'], self.bottomLeft['y'])]
        self.poly = Polygon(coords)  # shapely Object

    def setID(self, idWall):
        self.id = idWall

    def scaleTransform(self, scale):
        scale = [float(i) for i in scale]

        a = scale[0]
        b = scale[1]

        self.topLeft = {'x': self.topLeft['x'] * a, 'y': self.topLeft['y'] * b}
        self.topRight = {'x': self.topRight['x'] * a, 'y': self.topRight['y'] * b}
        self.bottomLeft = {'x': self.bottomLeft['x'] * a, 'y': self.bottomLeft['y'] * b}
        self.bottomRight = {'x': self.bottomRight['x'] * a, 'y': self.bottomRight['y'] * b}

        self.initPolygonObject()

    def matrixTransform(self, matrix):
        '''See https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/transform '''
        # preventive conversion:
        matrix = [float(i) for i in matrix]

        a = matrix[0]
        b = matrix[1]
        c = matrix[2]
        d = matrix[3]
        e = matrix[4]
        f = matrix[5]

        # top left corner:
        newX = a * self.topLeft['x'] + c * self.topLeft['y'] + e
        newY = b * self.topLeft['x'] + d * self.topLeft['y'] + f
        self.topLeft = {'x': newX, 'y': newY}

        # top right corner:
        newX = a * self.topRight['x'] + c * self.topRight['y'] + e
        newY = b * self.topRight['x'] + d * self.topRight['y'] + f
        self.topRight = {'x': newX, 'y': newY}

        # bottom left corner:
        newX = a * self.bottomLeft['x'] + c * self.bottomLeft['y'] + e
        newY = b * self.bottomLeft['x'] + d * self.bottomLeft['y'] + f
        self.bottomLeft = {'x': newX, 'y': newY}

        # bottom right corner:
        newX = a * self.bottomRight['x'] + c * self.bottomRight['y'] + e
        newY = b * self.bottomRight['x'] + d * self.bottomRight['y'] + f
        self.bottomRight = {'x': newX, 'y': newY}

        self.initPolygonObject()


class attractionPoint:
    def __init__(self, x, y, r=0):
        self.cx = x
        self.cy = y
        self.r = r
        self.id = 'no_id'

        self.p = Point(x, y)  # shapely Object

    def __str__(self):
        return str(self.__dict__)

    def setID(self, pID):
        self.id = pID