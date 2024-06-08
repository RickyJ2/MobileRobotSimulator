import math
from obstacle import Obstacle

class Lidar:
    def __init__(self, sensor_range, degreeGap, obs):
        self.sensor_range = sensor_range
        self.degreeGap = degreeGap
        self.obs: list[Obstacle] = obs
    
    def getDistPoint(self, x1, y1, x2, y2):
        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

    def getLidarReadings(self, x, y, thetaRad):
        readings = []
        for deg in range(0, 360, self.degreeGap):
            angleRad = math.radians(deg) + thetaRad
            x1 = x + self.sensor_range * math.cos(angleRad)
            y1 = y + self.sensor_range * math.sin(angleRad)
            minDist = self.sensor_range
            for obs in self.obs:
                clippedLine = obs.isIntersect(x, y, x1, y1)
                if clippedLine:
                    for point in clippedLine:
                        dist = self.getDistPoint(x, y, point[0], point[1])
                        if dist < minDist:
                            minDist = dist
            if minDist == self.sensor_range:
                minDist = 0
            readings.append([deg, minDist])
        return readings