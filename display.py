import pygame
from plotter import Plotter

#constant
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (70, 70, 70)
BLUE = (0,0,255)
RED = (255,0,0)
GREEN = (0,255,0)
NODERAD = 2
NODETHICKNESS = 0
EDGETHICKNESS = 1

class display:
    def __init__(self, dimensions, caption, scale, plotter: Plotter):
        self.plotter: Plotter = plotter
        self.scale = scale
        self.dimensions = dimensions
        mapWidth = dimensions[0]*scale + plotter.width*plotter.dpi
        mapHeight = dimensions[1]*scale
        self.map = pygame.display.set_mode((mapWidth, mapHeight))
        pygame.display.set_caption(caption)
        self.clear()
    
    def clear(self):
        self.map.fill(BLACK)

    def clearPlotter(self):
        self.plotter.clear()

    def updatePlot(self, data):
        self.plotter.plot(data)

    def drawPlot(self):
        startPoint = (self.dimensions[0]*self.scale, 0)
        self.plotter.draw(self.map, startPoint)
    #draws a circle on the map
    #center[0]: x
    #center[1]: y
    def drawCircle(self, color, center, radius = NODERAD, thickness = NODETHICKNESS):
        pygame.draw.circle(self.map, color, (center[0]*self.scale, center[1]*self.scale), radius*self.scale, thickness*self.scale)
    
    def drawLine(self, color, start, end, thickness = EDGETHICKNESS):
        pygame.draw.line(self.map, color, start, end, thickness*self.scale)
    
    def drawObstacles(self, obstacles):
        for obs in obstacles:
            self.drawRect(GREY, obs)

    def drawRect(self, color, rect):
        pygame.draw.rect(self.map, color, (rect.x*self.scale, rect.y*self.scale, rect.width*self.scale, rect.height*self.scale))
    
    def update(self):
        pygame.display.update()