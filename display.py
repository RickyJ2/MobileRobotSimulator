import pygame

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
    def __init__(self, dimensions, caption, scale):
        self.scale = scale
        self.dimensions = dimensions
        mapWidth = dimensions[0]*scale
        mapHeight = dimensions[1]*scale
        pygame.init()
        self.map = pygame.display.set_mode((mapWidth, mapHeight))
        pygame.display.set_caption(caption)
        self.clear()
    
    def clear(self):
        self.map.fill(BLACK)
        
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