# EECE 2140 Final Project - Sprites
# Written by David Charles

import pygame as pg
from pygame.sprite import Sprite
from settings import *
from random import randint

vec = pg.math.Vector2

class Gate(Sprite):
    def __init__(self, game):
        Sprite.__init__(self)
        self.game = game
        self.image = pg.transform.scale(game.AND2.img, (150,150))
        self.rect = self.image.get_rect()
        self.image.set_colorkey(BLACK)
        self.rect.center = (WIDTH/2, HEIGHT/2)
        self.pos = (1000, 1000)
        self.vel = vec(randint(1,5),randint(1,5))
        self.acc = vec(1,1)
        self.cofric = 0.01
    # ...
    def checkpos(self):
        if self.rect.x > WIDTH:
            self.vel.x *= -1
            # self.acc = self.vel * -self.cofric
        if self.rect.x < 0:
            self.vel.x *= -1
            # self.acc = self.vel * -self.cofric
        if self.rect.y < 0:
            self.pos.y = 25
            self.vel.y *= -1
            # self.acc = self.vel * -self.cofric
        if self.rect.y > HEIGHT:
            self.vel.y *= -1
            # self.acc = self.vel * -self.cofric
    def update(self):
        self.checkpos()
        # self.pos.x += self.vel.x
        # self.pos.y += self.vel.y
        # self.pos += self.vel
        self.rect.center = self.pos


#Creates platform sprite
class Platform(Sprite):
    def __init__(self, x, y, width, height, color, variant):
        Sprite.__init__(self)

        # Original sprite attributes 
        self.width = width
        self.height = height
        self.image = pg.Surface((self.width, self.height))
        self.color = color
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.variant = variant