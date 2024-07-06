import logging
import math
from display import display
from robot import Robot
from agv import AGV
from utils.convertJsonToObs import convertJsonToObs
from utils.readJsonFile import readJsonFile
import pygame
from point import Point

#configuration
HexagonSize = 350/2 #mm
width = 7 #number of hexagons
heigth = 7 #number of hexagons
#NOTE X dan Y nya dibalik
XDIM = HexagonSize * heigth * 3 / 2
YDIM = HexagonSize * width * math.sqrt(3)
POSROBOT_X_1 = 0 * HexagonSize * 3/2
POSROBOT_Y_1 = 0 * HexagonSize * math.sqrt(3)
POSROBOT_X_2 = 0 * HexagonSize * 3/2
POSROBOT_Y_2 = 6 * HexagonSize * math.sqrt(3)
SCALE = 0.2
dt = 10 #ms

class Simulation:
    def __init__(self):
        self.display = display([XDIM, YDIM],'Mobile Robot Simulator',SCALE)
        object = readJsonFile("Object.json")
        self.obs = convertJsonToObs(object, SCALE)
        self.agv1:AGV = AGV(1)
        self.agv2:AGV = AGV(2)
        robot1 = Robot(Point(POSROBOT_X_1, POSROBOT_Y_1), 1.5, SCALE, HexagonSize)
        robot2 = Robot(Point(POSROBOT_X_2, POSROBOT_Y_2), 1.5, SCALE, HexagonSize)
        self.agv1.init(robot1)
        self.agv2.init(robot2)
        self.running = False

    def run(self):
        try:
            self.agv1.connectWebsocket()
            self.agv2.connectWebsocket()
            self.displayScreen()
            self.running = True
            self.previousTime = pygame.time.get_ticks()
            while self.running:
                self.displayScreen()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                if pygame.time.get_ticks() - self.previousTime > dt:
                    self.previousTime = pygame.time.get_ticks()
                    self.agv1.robot.move()
                    self.agv2.robot.move()
                self.agv1.run()
                self.agv2.run()
            pygame.quit()
            self.agv1.disconnectWebsocket()
            self.agv2.disconnectWebsocket()
        except KeyboardInterrupt:
            pygame.quit()
            self.agv1.disconnectWebsocket()
            self.agv2.disconnectWebsocket()
        except Exception as e:
            logging.error(e)
            pygame.quit()
            self.agv1.disconnectWebsocket()
            self.agv2.disconnectWebsocket()

    def displayScreen(self):
        self.clearDisplay()
        self.drawObs()
        self.agv1.robot.draw(self.display.map)
        self.agv2.robot.draw(self.display.map)
        self.updateDisplay()

    def drawObs(self):
        self.display.drawObstacles(self.obs)
    
    def clearDisplay(self):
        self.display.clear()

    def updateDisplay(self):
        self.display.update()
        
