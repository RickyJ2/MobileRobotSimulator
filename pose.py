from Class.point import Point, dictToPoint

class Pose:
    def __init__(self, point:Point, orientation:float):
        self.point = point #mm, mm
        self.orientation = orientation #radians
    def __add__(self, other):
        return Pose(self.point + other.point, self.orientation + other.orientation)
    def __sub__(self, other):
        return Pose(self.point - other.point, self.orientation - other.orientation)
    def __str__(self):
        return f"Point: {self.point}, Orientation: {self.orientation}"
