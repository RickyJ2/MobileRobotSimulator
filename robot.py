import pygame
import math
from lidar import Lidar

#constant
MANUAL_MODE = 1
LYAPUNOV_MODE = 2
max = 0.05

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

    def getLidarReadings(self):
        self.lidarReadings = self.lidar.getLidarReadings(self.x, self.y, self.theta)

    def updateState(self):
        self.getLidarReadings()

    def draw(self, map: pygame.Surface):
        map.blit(self.rotated, self.rect)
        for reading in self.lidarReadings:
            degRad = math.radians(reading[0]) + self.theta
            x1 = self.x + self.radius * math.cos(degRad)
            y1 = self.y + self.radius * math.sin(degRad)
            x2 = self.x + reading[1] * math.cos(degRad)
            y2 = self.y + reading[1] * math.sin(degRad)
            color = (0, 255, 0) if reading[1] == self.lidar.sensor_range else (255, 0, 0)
            pygame.draw.line(map, color, (x1, y1), (x2, y2), 1)

    def move(self, dt, event = None):
        if event is not None:
            if event.type == pygame.MOUSEBUTTONUP:
                self.targetPos = pygame.mouse.get_pos()
                self.mode = LYAPUNOV_MODE
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
        #x,y start 0,0 from top left
        if self.mode == LYAPUNOV_MODE:
            vT, omegaT = self.LyapunovControl([self.targetPos[0], self.targetPos[1], math.radians(0)])
            self.vLeft = vT - omegaT*self.width/2
            self.vRight = vT + omegaT*self.width/2
        self.vLeft = max if self.vLeft > max else -max if self.vLeft < -max else self.vLeft
        self.vRight = max if self.vRight > max else -max if self.vRight < -max else self.vRight
        v = ((self.vLeft + self.vRight)/2)
        omega = ((self.vRight - self.vLeft)/self.width)
        self.x += v * math.cos(self.theta)
        self.y += v * math.sin(self.theta)
        self.theta += omega
        # print("v Left: ", self.vLeft,"v Right: ", self.vRight, "v: ", v, "omega: ", omega, "dx: ", abs(self.x - self.targetPos[0]), "dy: ", abs(self.y - self.targetPos[1]), "dTheta: ", abs(self.theta - 0))
        self.rotated = pygame.transform.rotozoom(self.body, 360 - math.degrees(self.theta),1)
        self.rect = self.rotated.get_rect(center=(self.x, self.y))

    def LyapunovControl(self, targetPoint):
        errorX = targetPoint[0] - self.x
        errorY = targetPoint[1] - self.y
        errorTheta = targetPoint[2] - (self.theta)
        if abs(errorX) < 5 and abs(errorY) < 5 and abs(errorTheta) < math.radians(180):
            return 0, 0
        k1 = 1
        k2 = 8
        k3 = 3
        v = k1 * (errorX * math.cos(self.theta) + errorY * math.sin(self.theta))
        omega = k2 * (-errorX * math.sin(self.theta) + errorY * math.cos(self.theta)) + k3 * (errorTheta)
        
        return v, omega