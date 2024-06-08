import pygame
SCALE = 10

class Obstacle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width  = width
        self.height = height
    
    def isIntersect(self, x, y, x1, y2):
        rect = pygame.Rect(self.x*SCALE, self.y*SCALE, self.width*SCALE, self.height*SCALE)
        clippedLine = rect.clipline(x, y, x1, y2)
        if clippedLine is None:
            return False
        return clippedLine