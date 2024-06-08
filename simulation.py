from display import display
from robot import Robot
from utils.convertJsonToObs import convertJsonToObs
from utils.readJsonFile import readJsonFile
import pygame
from lidar import Lidar

#configuration
XDIM = 30
YDIM = 50
POSROBOT_X = 100
POSROBOT_Y = 20
SCALE = 10
LIDAR_MAX_RANGE = 100
LIDAR_ANGLE = 5

class Simulation:
    def __init__(self):
        self.display = display([XDIM, YDIM],'Mobile Robot Simulator' ,SCALE)
        object = readJsonFile("Object.json")
        self.obs = convertJsonToObs(object, SCALE)
        self.robot = Robot([POSROBOT_X, POSROBOT_Y], 1.5, Lidar(LIDAR_MAX_RANGE, LIDAR_ANGLE, self.obs))
        self.running = False
        self.dt = 0
        self.lastTime = pygame.time.get_ticks() 
    
    def run(self):
        self.displayScreen()
        self.running = True
        while self.running:
            self.robot.updateState()
            self.displayScreen()
            self.dt = (pygame.time.get_ticks() - self.lastTime)/1000
            self.lastTime = pygame.time.get_ticks()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.robot.move(self.dt, event)
            self.robot.move(self.dt)
        pygame.quit()

    def displayScreen(self):
        self.clearDisplay()
        self.robot.draw(self.display.map)
        self.drawObs()
        self.updateDisplay()

    def drawObs(self):
        self.display.drawObstacles(self.obs)
    
    def clearDisplay(self):
        self.display.clear()

    def updateDisplay(self):
        self.display.update()
        
