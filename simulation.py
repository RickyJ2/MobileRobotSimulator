from display import display
from robot import Robot
from utils.convertJsonToObs import convertJsonToObs
from utils.readJsonFile import readJsonFile
import pygame
from lidar import Lidar
from plotter import Plotter

#configuration
XDIM = 30
YDIM = 50
POSROBOT_X = 80
POSROBOT_Y = 200
SCALE = 10
LIDAR_MAX_RANGE = 100
LIDAR_ANGLE = 5
PLOT_DPI = 100
PLOT_XDIM = 4
PLOT_YDIM = YDIM*SCALE/PLOT_DPI
#Set True if only want to see robot movement
disabledPlotter = True

class Simulation:
    def __init__(self):
        self.display = display([XDIM, YDIM],'Mobile Robot Simulator',SCALE, Plotter(PLOT_XDIM, PLOT_YDIM, PLOT_DPI))
        object = readJsonFile("Object.json")
        self.obs = convertJsonToObs(object, SCALE)
        self.obs = []
        self.robot = Robot([POSROBOT_X, POSROBOT_Y], 1.5, Lidar(LIDAR_MAX_RANGE, LIDAR_ANGLE, self.obs))
        self.running = False

    def run(self):
        self.displayScreen()
        self.running = True
        while self.running:
            self.robot.updateState()
            self.displayScreen()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.robot.move(event)
            self.robot.move()
        pygame.quit()

    def displayScreen(self):
        self.clearDisplay()
        if not disabledPlotter:
            self.display.clearPlotter()
            self.display.updatePlot(self.robot.lidarReadings)
            self.display.drawPlot()
        self.robot.draw(self.display.map)
        self.drawObs()
        self.updateDisplay()

    def drawObs(self):
        self.display.drawObstacles(self.obs)
    
    def clearDisplay(self):
        self.display.clear()

    def updateDisplay(self):
        self.display.update()
        
