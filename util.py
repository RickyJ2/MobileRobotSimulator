import math
from typing import Union
from point import Point
from pose import Pose

def distance(pos: Union[Point, Pose], target: Union[Point, Pose]) -> float:
    if isinstance(pos, Pose):
        pos = pos.point
    if isinstance(target, Pose):
        target = target.point
    return math.sqrt((pos.x - target.x)**2 + (pos.y - target.y)**2)

def findOrientation(pos: Union[Point, Pose], target:Union[Point, Pose]) -> float:
    if isinstance(pos, Pose):
        pos = pos.point
    if isinstance(target, Pose):
        target = target.point
    return math.degrees(math.atan2(target.y - pos.y, target.x - pos.x))