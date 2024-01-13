from display import display, GREEN
from robot import Robot
from utils.convertJsonToObs import convertJsonToObs
from utils.readJsonFile import readJsonFile
import pygame

#configuration
XDIM = 30
YDIM = 50
POSROBOT_X = 10
POSROBOT_Y = 2
GOALNODE_X = XDIM/2
GOALNODE_Y = YDIM/2
GOALRADIUS = 1
SCALE = 10

class Simulation:
    def __init__(self):
        self.display = display([XDIM, YDIM],'Mobile Robot Simulator' ,SCALE)
        object = readJsonFile("Object.json")
        self.obs = convertJsonToObs(object)
        self.robot = Robot([POSROBOT_X, POSROBOT_Y], 1.5, 1.5)
        self.running = False
    
    def run(self):
        posPlayer = [POSROBOT_X, POSROBOT_Y]
        self.displayScreen(posPlayer)
        self.running = True
        while self.running:
            self.displayScreen(posPlayer)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.robot.move(event)
        pygame.quit()

    def displayScreen(self, posPlayer):
        self.clearDisplay()
        self.robot.draw(self.display)
        self.drawObs()
        self.updateDisplay()
    
    def drawPlayer(self, posPlayer):
        self.display.drawCircle(GREEN, posPlayer)

    def drawObs(self):
        self.display.drawObstacles(self.obs)
    
    def clearDisplay(self):
        self.display.clear()

    def updateDisplay(self):
        self.display.update()
        
