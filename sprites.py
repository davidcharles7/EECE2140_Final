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
        self.width = width
        self.height = height
        self.image = pg.Surface((self.width,self.height))
        self.color = color
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.variant = variant


class Draggable(Sprite):
    def __init__(self, image: pg.Surface, pos=(0,0), scale: float = 1.1):

        Sprite.__init__(self)
        # store original image and compute scaled image
        self._orig_image = image.copy()
        try:
            self._orig_image = self._orig_image.convert_alpha()
        except Exception:
            pass

        # compute scaled size
        w, h = self._orig_image.get_size()
        sw = max(1, int(w * scale))
        sh = max(1, int(h * scale))
        try:
            self.image = pg.transform.smoothscale(self._orig_image, (sw, sh))
        except Exception:
            # fallback to simple scale
            self.image = pg.transform.scale(self._orig_image, (sw, sh))

        # ensure transparency preserved
        try:
            self.image = self.image.convert_alpha()
        except Exception:
            pass

        # create rect and selection state
        self.rect = self.image.get_rect(topleft=pos)
        # store scale and original size for later adjustments
        self.scale = float(scale)
        self.orig_size = (w, h)
        self.selected = False
        self._offset = (0, 0)

    def set_scale(self, scale: float):
        """Rescale the sprite image and update rect keeping topleft position."""
        if scale <= 0:
            return
        self.scale = float(scale)
        w, h = self.orig_size
        sw = max(1, int(w * self.scale))
        sh = max(1, int(h * self.scale))
        try:
            self.image = pg.transform.smoothscale(self._orig_image, (sw, sh))
        except Exception:
            self.image = pg.transform.scale(self._orig_image, (sw, sh))
        try:
            self.image = self.image.convert_alpha()
        except Exception:
            pass
        # maintain current topleft
        topleft = (self.rect.x, self.rect.y)
        self.rect = self.image.get_rect(topleft=topleft)

    def select(self, mouse_pos):
        mx, my = mouse_pos
        ox = mx - self.rect.x
        oy = my - self.rect.y
        self._offset = (ox, oy)
        self.selected = True

    def move(self, mouse_pos):
        if not self.selected:
            return
        mx, my = mouse_pos
        ox, oy = self._offset
        self.rect.x = mx - ox
        self.rect.y = my - oy

    def deselect(self):
        self.selected = False

    def update(self):
        # update can be used for animations later; currently nothing needed
        pass