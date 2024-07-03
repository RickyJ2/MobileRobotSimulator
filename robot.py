from time import sleep
import numpy as np
import pygame
import math
from lidar import Lidar

#constant
max = 0.04
dt = 100 #ms

class Robot:
    def __init__(self, startPos, width, lidar: Lidar):
        self.x = startPos[0]
        self.y = startPos[1]
        self.width = width
        self.body = pygame.image.load("robot.png")
        self.theta = math.radians(0)
        self.vLeft = 0
        self.vRight = 0
        self.rotated = self.body
        self.rect = self.rotated.get_rect(center=(self.x, self.y))
        self.targetPos = startPos
        self.lidar = lidar
        self.radius = 15
        self.getLidarReadings()
        self.previousTime = pygame.time.get_ticks()

    def getLidarReadings(self):
        self.lidarReadings = self.lidar.getLidarReadings(self.x, self.y, self.theta)
        self.diff = []
        self.diff.append([self.lidarReadings[0][0], self.lidarReadings[0][1] - self.lidarReadings[-1][1]])
        for i in range(1, len(self.lidarReadings)):
            self.diff.append([self.lidarReadings[i][0], self.lidarReadings[i][1] - self.lidarReadings[i - 1][1]])

    def updateState(self):
        self.getLidarReadings()

    def draw(self, map: pygame.Surface):
        map.blit(self.rotated, self.rect)
        for reading in self.lidarReadings:
            if reading[1] > 200:
                continue
            degRad = math.radians(reading[0]) + self.theta
            x1 = self.x + self.radius * math.cos(degRad)
            y1 = self.y + self.radius * math.sin(degRad)
            x2 = self.x + reading[1] * math.cos(degRad)
            y2 = self.y + reading[1] * math.sin(degRad)
            color = (0, 255, 0) if reading[1] == self.lidar.sensor_range else (255, 0, 0)
            pygame.draw.line(map, color, (x1, y1), (x2, y2), 1)

    def move(self, event = None):
        if event is not None:
            if event.type == pygame.MOUSEBUTTONUP:
                self.targetPos = pygame.mouse.get_pos()
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
        print("v Left: ", self.vLeft,"v Right: ", self.vRight, "v: ", v, "omega: ", math.degrees(omega))
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

    def LyapunovControl(self, targetPoint):
        errorX = targetPoint[0] - self.x
        errorY = targetPoint[1] - self.y
        errorTheta = targetPoint[2] - (self.theta)
        if abs(errorX) < 5 and abs(errorY) < 5 and abs(errorTheta) < math.radians(180):
            return 0, 0
        k1 = 2.5
        k2 = 1
        k3 = 1
        v = k1 * (errorX * math.cos(self.theta) + errorY * math.sin(self.theta))
        omega = k2 * (-errorX * math.sin(self.theta) + errorY * math.cos(self.theta)) + k3 * (errorTheta)
        
        return v, omega

def getSign(num):
    return 1 if num > 0 else -1 if num < 0 else 0