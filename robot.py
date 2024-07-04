import pygame
import math
from pose import Pose
from point import Point

#constant
max = 0.04
dt = 100 #ms

class Robot:
    def __init__(self, startPos: Point, width):
        self.currentPose: Pose = Pose(startPos, math.degrees(0))
        self.width = width
        self.body = pygame.image.load("robot.png")
        self.vLeft = 0
        self.vRight = 0
        self.rotated = self.body
        self.rect = self.rotated.get_rect(center=(startPos.x, startPos.y))
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
        self.rotated = pygame.transform.rotozoom(self.body, 360 - math.degrees(self.currentPose.orientation),1)
        self.rect = self.rotated.get_rect(center=(self.currentPose.point.x, self.currentPose.point.y))

    def move22(self, targetPose: Pose):
        self.targetPos = targetPose
        self.previousTime = pygame.time.get_ticks()
        if pygame.time.get_ticks() - self.previousTime > dt:
            self.previousTime = pygame.time.get_ticks()
            vT, omegaT = self.LyapunovControl([self.targetPos[0], self.targetPos[1], math.radians(0)])
            self.vLeft = vT - omegaT*self.width/2
            self.vRight = vT + omegaT*self.width/2
        self.vLeft, self.vRight = self.saturatedSpeed(self.vLeft, self.vRight, max)
        v = ((self.vLeft + self.vRight)/2)
        omega = ((self.vRight - self.vLeft)/self.width)
        self.x += v * math.cos(self.theta)
        self.y += v * math.sin(self.theta)
        self.theta += omega
        self.rotated = pygame.transform.rotozoom(self.body, 360 - math.degrees(self.theta),1)
        self.rect = self.rotated.get_rect(center=(self.x, self.y))
    
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