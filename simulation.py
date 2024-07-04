from display import display
from robot import Robot
from agv import AGV
from utils.convertJsonToObs import convertJsonToObs
from utils.readJsonFile import readJsonFile
import pygame
from point import Point

#configuration
XDIM = 30
YDIM = 50
POSROBOT_X = 80
POSROBOT_Y = 180
SCALE = 10
LIDAR_MAX_RANGE = 250
LIDAR_ANGLE = 5

class Simulation:
    def __init__(self):
        self.display = display([XDIM, YDIM],'Mobile Robot Simulator',SCALE)
        object = readJsonFile("Object.json")
        self.obs = convertJsonToObs(object, SCALE)
        
        self.agv:AGV = AGV(1)
        robot1 = Robot(Point(POSROBOT_X, POSROBOT_Y), 1.5)
        self.agv.init(robot1)
        self.running = False

    def run(self):
        self.agv.connectWebsocket()
        self.displayScreen()
        self.running = True
        while self.running:
            self.displayScreen()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            self.agv.robot.move()
        pygame.quit()
        self.agv.disconnectWebsocket()

    def displayScreen(self):
        self.clearDisplay()
        self.drawObs()
        self.agv.robot.draw(self.display.map)
        self.updateDisplay()

    def drawObs(self):
        self.display.drawObstacles(self.obs)
    
    def clearDisplay(self):
        self.display.clear()

    def updateDisplay(self):
        self.display.update()
        
