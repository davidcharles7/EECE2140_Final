# EECE 2140 Final Project - Sprites
# Written by David Charles

import pygame as pg
from pygame.sprite import Sprite
from settings import *
from random import randint

vec = pg.math.Vector2

#Creates platform sprite
class Platform(Sprite):
    def __init__(self, x, y, width, height, color, variant):
        Sprite.__init__(self)
        self.width = width
        self.height = height
        self.image = pg.Surface((self.width,self.height))
        self.color = color
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.variant = variant