import pygame
import math
from display import GREEN

class Robot:
    def __init__(self, startPos, width, height):
        self.body = pygame.Rect(
            startPos[0] - width/2, 
            startPos[1] - height/2, 
            width, 
            height)
        self.x = startPos[0]
        self.y = startPos[1]
        self.width = width
        self.height = height
        self.theta = 0
        self.vLeft = 0
        self.vRight = 0

    def draw(self, map):
        map.drawRect(GREEN, pygame.Rect(
                self.x - self.width/2, 
                self.y - self.height/2, 
                self.width, 
                self.height)
            )
        
    def move(self, event = None):
        if event is not None:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.y += 1
                if event.key == pygame.K_DOWN:
                    self.y -= 1
                if event.key == pygame.K_LEFT:
                    self.x -= 1
                if event.key == pygame.K_RIGHT:
                    self.x += 1