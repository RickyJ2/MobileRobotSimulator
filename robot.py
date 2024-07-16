import pygame
import math
from pose import Pose
from point import Point

#constant
max = 1.5

class Robot:
    def __init__(self, startPos: Point, width, scale, HexagonSize, YDIM):
        self.currentPose: Pose = Pose(startPos, math.radians(90))
        self.width = width
        self.body = pygame.image.load("robot.png")
        self.scale = scale
        self.HexagonSize = HexagonSize
        self.vLeft = 0
        self.vRight = 0
        self.YDIM = YDIM
        self.rotated = pygame.transform.rotozoom(self.body, math.degrees(self.currentPose.orientation), 1)
        self.rect = self.rotated.get_rect(center=((startPos.x + HexagonSize) * scale, YDIM * scale - (startPos.y + HexagonSize) * scale))
        self.targetPos = startPos
        self.previousTime = pygame.time.get_ticks()

    def draw(self, map: pygame.Surface):
        map.blit(self.rotated, self.rect)

    def getPos(self) -> Pose:
        return self.currentPose

    def getVelocity(self) -> float:
        return ((self.vLeft + self.vRight)/2)
    
    def stop(self):
        self.vLeft = 0
        self.vRight = 0

    def setSpeed(self, v, omega):
        self.vLeft = v - omega*self.width/2
        self.vRight = v + omega*self.width/2
        self.vLeft, self.vRight = self.saturatedSpeed(self.vLeft, self.vRight, max)

    def move(self):
        v = ((self.vLeft + self.vRight)/2)
        omega = ((self.vRight - self.vLeft)/self.width)
        self.currentPose.point.x += v * math.cos(self.currentPose.orientation)
        self.currentPose.point.y += v * math.sin(self.currentPose.orientation)
        self.currentPose.orientation += omega
        if self.currentPose.orientation > 2 * math.pi:
            self.currentPose.orientation = self.currentPose.orientation % (2 * math.pi)
        elif self.currentPose.orientation < 0:
            self.currentPose.orientation = self.currentPose.orientation % (2 * math.pi)
            self.currentPose.orientation += 2 * math.pi
        self.rotated = pygame.transform.rotozoom(self.body, math.degrees(self.currentPose.orientation), 1)
        self.rect = self.rotated.get_rect(center=((self.currentPose.point.x + self.HexagonSize) * self.scale, self.YDIM * self.scale - (self.currentPose.point.y + self.HexagonSize) * self.scale))
    
    def saturatedSpeed(self, vLeft, vRight, maxSpeed):
        if vLeft < maxSpeed and vLeft > -maxSpeed and vRight < maxSpeed and vRight > -maxSpeed:
            return vLeft, vRight
        timesLeft = 1
        timesRight = 1
        if vLeft < 0:
            timesLeft = -1
            vLeft = -vLeft
        if vRight < 0:
            timesRight = -1
            vRight = -vRight
        if vLeft > maxSpeed and vRight > maxSpeed:
            if vLeft > vRight:
                vRight *= maxSpeed/vLeft
                vLeft = maxSpeed
            else:
                vLeft *= maxSpeed/vRight
                vRight = maxSpeed
        elif vLeft > maxSpeed:
            vLeft = maxSpeed
        elif vRight > maxSpeed:
            vRight = maxSpeed
        return vLeft * timesLeft, vRight * timesRight

def getSign(num):
    return 1 if num > 0 else -1 if num < 0 else 0