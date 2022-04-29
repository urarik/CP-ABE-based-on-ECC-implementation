import random
from nummaster.basic import sqrtmod
from utils import inverse

# https://www.geeksforgeeks.org/python-program-for-basic-and-extended-euclidean-algorithms-2/


class Point:
    def __init__(self, point, curve=None):
        self.curve = curve
        if type(point) is tuple:
            self.x = point[0]
            self.y = point[1]
        elif type(point) is bytes and point != b'0x0':
            if curve is not None:
                x, y = self.decompress(point)
                self.x = x
                self.y = y
            else:
                self.temp_bytes = point
        elif type(point) is Point:
            self.x = point.x
            self.y = point.y
            self.curve = point.curve
        else:
            self.x = None
            self.y = None

    def decompress(self, point: bytes = None):
        if point is None:
            point = self.temp_bytes
        if point[0] == 4:
            x = point[1:33]
            y = point[33:]
        else:
            x = int.from_bytes(point[1:], 'big')
            # Tonelli-Shanks algorithm
            y = sqrtmod((x ** 3) + (self.curve.a * x) + self.curve.b,
                        self.curve.p)
            if point[0] == 2:
                y = y if y % 2 == 0 else self.curve.p - y
            else:
                y = y if y % 2 == 1 else self.curve.p - y
        self.x = x
        self.y = y
        return x, y

    def compress(self):
        if self.x is None and self.y is None:
            return b'0x0'
        elif self.y % 2 == 0:
            point_bytes = bytes([2])
        else:
            point_bytes = bytes([3])

        point_bytes += self.x.to_bytes(32, 'big')
        return point_bytes

    def __add__(self, other):
        if self.x is None and self.y is None:
            return Point((other.x, other.y), other.curve)
        if other.x is None and other.y is None:
            return Point((self.x, self.y), self.curve)
        if self.x == other.x and self.y != other.y:
            return Point((None, None), self.curve)
        if self.x == other.x and self.y == other.y:
            return self.doubling()

        slope = (self.y - other.y) * inverse(self.x - other.x, self.curve.p)
        x = ((slope ** 2) - self.x - other.x) % self.curve.p
        y = ((slope * (other.x - x)) % self.curve.p - other.y) % self.curve.p
        return Point((x, y), self.curve)

    def doubling(self):
        slope = ((3 * (self.x ** 2) + self.curve.a) * inverse(2 * self.y, self.curve.p)) % self.curve.p
        x = ((slope ** 2) - (2 * self.x)) % self.curve.p
        y = (slope * (self.x - x) - self.y) % self.curve.p
        self.x = x
        self.y = y
        return Point((self.x, self.y), self.curve)

    def __mul__(self, other):
        result_key = Point((None, None), self.curve)
        if self.x is None and self.y is None:
            return result_key

        _G = Point(self, self.curve)  # point여야 함!
        if other < 0:
            other = -other
            _G.y = -_G.y % _G.curve.p
        while other != 0:
            if other & 0x1 == 1:
                result_key += _G
            _G.doubling()
            # G += G
            other >>= 1
        return result_key

    def __rmul__(self, other):
        return self.__mul__(other)

    def __sub__(self, other):
        return self.__add__(-1 * other)

    def __str__(self):
        # return "(" + "%X" % self.x + ", " + "%X" % self.y + ")"
        return "(" + str(self.x) + ", " + str(self.y) + ")"

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.curve == other.curve


class Curve:
    def __init__(self, p, a, b, G, n, h):
        self.p = p
        self.a = a
        self.b = b
        self.G = G
        self.n = n
        self.h = h

    def isExist(self, point):
        return (((point.x ** 3) + (self.a * point.x) + self.b - (point.y ** 2)) % self.p) == 0

    def isExistY(self, x):
        try:
            y = sqrtmod((x ** 3) + (self.a * x) + self.b, self.p)
            return y
        except ValueError:
            return False

    def generatePrivateKey(self):
        return random.randint(1, self.n)

    def generatePublicKey(self, private_key):
        public_key = Point((None, None), self)
        G = Point(self.G, self)  # point여야 함!
        while private_key != 0:
            if private_key & 0x1 == 1:
                public_key += G
            G.doubling()
            # G += G
            private_key >>= 1
        return public_key


p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
a = 0
b = 7
G = Point(0x0279BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798.to_bytes(33, 'big'))
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
h = 1

curve = Curve(p, a, b, G, n, h)
G.curve = curve
G.decompress()
