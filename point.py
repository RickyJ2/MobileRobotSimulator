class Point:
    def __init__(self, x, y):
        self.x = x #mm
        self.y = y #mm
    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)
    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)
    def __str__(self):
        return f"({self.x},{self.y})"
    def toDict(self) -> dict:
        return pointToDict(self)

def dictToPoint(d: dict) -> Point:
    return Point(d["x"], d["y"])

def pointToDict(p: Point) -> dict:
    return {
        "x": p.x,
        "y": p.y
    }

def arrayToPoint(a: list) -> Point:
    return Point(a[0], a[1])