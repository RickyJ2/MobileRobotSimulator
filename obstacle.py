import pygame

class Obstacle:
    def __init__(self, x, y, width, height, scale):
        self.x = x
        self.y = y
        self.width  = width
        self.height = height
        self.scale = scale
    
    def isIntersect(self, x, y, x1, y2):
        rect = pygame.Rect(self.x*self.scale, self.y*self.scale, self.width*self.scale, self.height*self.scale)
        clippedLine = rect.clipline(x, y, x1, y2)
        if clippedLine is None:
            return False
        return clippedLine