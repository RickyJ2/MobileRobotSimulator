from time import sleep
import numpy as np
import pygame
import math
from lidar import Lidar

#constant
MANUAL_MODE = 1
LYAPUNOV_MODE = 2
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
        self.mode = MANUAL_MODE
        self.targetPos = startPos
        self.lidar = lidar
        self.radius = 15
        self.getLidarReadings()
        self.previousTime = pygame.time.get_ticks()

    def getLidarReadings(self):
        self.lidarReadings = self.lidar.getLidarReadings(self.x, self.y, self.theta)

    def updateState(self):
        self.getLidarReadings()

    def draw(self, map: pygame.Surface):
        map.blit(self.rotated, self.rect)
        corners, obss = self.findObs()
        for reading in self.lidarReadings:
            if reading[1] == 0:
                continue
            degRad = math.radians(reading[0]) + self.theta
            x1 = self.x + self.radius * math.cos(degRad)
            y1 = self.y + self.radius * math.sin(degRad)
            x2 = self.x + reading[1] * math.cos(degRad)
            y2 = self.y + reading[1] * math.sin(degRad)
            color = (0, 255, 0) if reading[1] == self.lidar.sensor_range else (255, 0, 0)
            pygame.draw.line(map, color, (x1, y1), (x2, y2), 1)
        for corner in corners:
            degRad = math.radians(self.lidarReadings[corner][0]) + self.theta
            x = self.x + self.lidarReadings[corner][1] * math.cos(degRad)
            y = self.y + self.lidarReadings[corner][1] * math.sin(degRad)
            pygame.draw.circle(map, (0, 0, 255), (int(x), int(y)), 5)
        for obs in obss:
            degRad = math.radians(self.lidarReadings[obs[0]][0]) + self.theta
            x1 = self.x + self.lidarReadings[obs[0]][1] * math.cos(degRad)
            y1 = self.y + self.lidarReadings[obs[0]][1] * math.sin(degRad)
            degRad = math.radians(self.lidarReadings[obs[1]][0]) + self.theta
            x2 = self.x + self.lidarReadings[obs[1]][1] * math.cos(degRad)
            y2 = self.y + self.lidarReadings[obs[1]][1] * math.sin(degRad)
            pygame.draw.line(map, (0,255,0), (x1, y1), (x2, y2), 1)

    def findCorner(self, threshold = 2):
        corners = []
        prevGradient = self.lidarReadings[1][1] - self.lidarReadings[0][1]
        for i in range(2, len(self.lidarReadings)):
            gradient = self.lidarReadings[i][1] - self.lidarReadings[i - 1][1]
            if abs(gradient - prevGradient) > threshold and getSign(prevGradient) != getSign(gradient):
                if self.lidarReadings[i][1] != 0:
                    corners.append(i - 1)
                else:
                    corners.append(i - 2)
            prevGradient = gradient
        return corners

    def findObs(self, threshold = 0):
        corners = []
        obss = []
        prevGradient = self.lidarReadings[1][1] - self.lidarReadings[0][1]
        for i in range(2, len(self.lidarReadings)):
            gradient = self.lidarReadings[i][1] - self.lidarReadings[i - 1][1]
            if abs(gradient - prevGradient) > threshold and getSign(prevGradient) != getSign(gradient):
                if self.lidarReadings[i][1] != 0:
                    corners.append(i - 1)
                else:
                    corners.append(i - 2)
            if len(corners) > 1:
                prevCorner = corners[-2]
                diffLen = corners[-1] - prevCorner
                index = round(prevCorner + diffLen/2) % len(self.lidarReadings)
                if self.lidarReadings[index][1] != 0:
                    obss.append([corners[-2], corners[-1]])
            prevGradient = gradient
        return corners, obss

    def move(self, event = None):
        if event is not None:
            if event.type == pygame.MOUSEBUTTONUP:
                self.targetPos = pygame.mouse.get_pos()
                self.mode = LYAPUNOV_MODE
                self.previousTime = pygame.time.get_ticks()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.vLeft += 0.001
                elif event.key == pygame.K_a:
                    self.vLeft -= 0.001
                elif event.key == pygame.K_e:
                    self.vRight += 0.001
                elif event.key == pygame.K_d:
                    self.vRight -= 0.001
                self.mode = MANUAL_MODE
        if self.mode == LYAPUNOV_MODE and pygame.time.get_ticks() - self.previousTime > dt:
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
        # print("v Left: ", self.vLeft,"v Right: ", self.vRight, "v: ", v, "omega: ", math.degrees(omega))
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
        if vLeft > vRight:
            vRight *= maxSpeed/vLeft
            vLeft = maxSpeed
        else:
            vLeft *= maxSpeed/vRight
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
    return 1 if num >= 0 else -1