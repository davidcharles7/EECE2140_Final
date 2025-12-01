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
    def __init__(self, image: pg.Surface, pos=(0,0), scale: float = 1.0):

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
        # remember the default (original) position so we can reset sprites later
        try:
            # store as a tuple
            self.default_pos = (int(pos[0]), int(pos[1]))
        except Exception:
            self.default_pos = (self.rect.x, self.rect.y)
        # store scale and original size for later adjustments
        self.scale = float(scale)
        self.orig_size = (w, h)
        self.selected = False
        self._offset = (0, 0)
        # whether the sprite is currently being dragged (mouse held)
        self.dragging = False
        # enable snapping only after user picks up the sprite (avoid auto-snap in tray)
        self.snap_enabled = False
        # tracks if the sprite has been moved from its default tray position
        self.moved_from_default = False
        # whether this sprite is currently stored in the tray (i.e. at its default)
        # When the user moves a sprite away from its default, this will be set False.
        self.in_tray = True

    def set_scale(self, scale: float):
        #Rescale the sprite image and update rect keeping topleft position.
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

    def snap_to_grid(self):
        # Snap the sprite's topleft to the nearest grid intersection
        try:
            gx, gy = GRID_ORIGIN
        except Exception:
            gx, gy = (0, 0)
        try:
            gs = int(GRID_SIZE)
            if gs <= 0:
                gs = 40
        except Exception:
            gs = 40

        # compute nearest grid-aligned coordinates
        nx = gx + round((self.rect.x - gx) / gs) * gs
        ny = gy + round((self.rect.y - gy) / gs) * gs

        # assign snapped position
        self.rect.x = int(nx)
        self.rect.y = int(ny)

    def select(self, mouse_pos):
        mx, my = mouse_pos
        ox = mx - self.rect.x
        oy = my - self.rect.y
        self._offset = (ox, oy)
        # mark as selected and start dragging immediately
        self.selected = True
        self.dragging = True
        self.snap_enabled = True

    def move(self, mouse_pos):
        # only move when actively dragging (mouse button held)
        if not self.dragging:
            return
        mx, my = mouse_pos
        ox, oy = self._offset
        self.rect.x = mx - ox
        self.rect.y = my - oy
        try:
            if (self.rect.x, self.rect.y) != (int(self.default_pos[0]), int(self.default_pos[1])):
                self.moved_from_default = True
        except Exception:
            pass
        # mark as removed from tray as soon as it deviates from its default
        try:
            if (self.rect.x, self.rect.y) != (int(self.default_pos[0]), int(self.default_pos[1])):
                self.in_tray = False
        except Exception:
            self.in_tray = False

    def deselect(self):
        # fully clear selection state and snap to grid
        self.selected = False
        self.dragging = False
        try:
            self.snap_to_grid()
        except Exception:
            pass
        try:
            if (self.rect.x, self.rect.y) != (int(self.default_pos[0]), int(self.default_pos[1])):
                self.moved_from_default = True
        except Exception:
            pass
        # after snapping, update whether this sprite is considered inside the tray
        try:
            if (self.rect.x, self.rect.y) == (int(self.default_pos[0]), int(self.default_pos[1])):
                self.in_tray = True
            else:
                self.in_tray = False
        except Exception:
            pass

    def clear_selection(self):
        """Clear selection state without snapping the sprite. Useful when
        switching selection to another sprite and you don't want the previous
        sprite to be forced back to the grid immediately.
        """
        try:
            self.selected = False
            self.dragging = False
        except Exception:
            pass

    def update(self):
        # If not currently being dragged, ensure the sprite rests on the grid.
        # This allows a sprite to remain selected while snapping when idle.
        if not self.dragging and self.snap_enabled:
            try:
                self.snap_to_grid()
            except Exception:
                pass


class TraySprite(Sprite):
    # A sprite that displays the tray background image at a fixed position
    def __init__(self, image: pg.Surface, pos=(0, 0)):
        Sprite.__init__(self)
        self.image = image
        try:
            self.image = self.image.convert()
        except Exception:
            pass
        self.rect = self.image.get_rect(topleft=pos)
    
    def update(self):
        pass