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
    def __init__(self, image: pg.Surface, pos=(0,0), scale: float = 1.0, stretch_px: int = 0, snap_offset=(0,0)):

        Sprite.__init__(self)
        # store original image and compute scaled image
        self._orig_image = image.copy()
        try:
            self._orig_image = self._orig_image.convert_alpha()
        except Exception:
            pass

        # cache stretch amount (horizontal pixels). Image will shift left by half of this.
        try:
            self.stretch_px = int(stretch_px)
        except Exception:
            self.stretch_px = 0
        # snapshot offsets for snapping to grid (pixels)
        try:
            self.snap_off_x = int(snap_offset[0]) if isinstance(snap_offset, (list, tuple)) else int(snap_offset)
        except Exception:
            self.snap_off_x = 0
        try:
            self.snap_off_y = int(snap_offset[1]) if isinstance(snap_offset, (list, tuple)) else 0
        except Exception:
            self.snap_off_y = 0

        # compute scaled size
        w, h = self._orig_image.get_size()
        sw = max(1, int(w * scale))
        sh = max(1, int(h * scale))
        # build final image: scale, then horizontally stretch by stretch_px using original source
        try:
            final_w = sw + max(0, self.stretch_px)
            final_h = sh
            stretched = pg.transform.smoothscale(self._orig_image, (final_w, final_h))
        except Exception:
            stretched = pg.transform.scale(self._orig_image, (sw + max(0, self.stretch_px), sh))
        try:
            self.image = stretched.convert_alpha()
        except Exception:
            self.image = stretched

        # position: shift left by half of the horizontal stretch
        self.rect = self.image.get_rect(topleft=(pos[0] - (max(0, self.stretch_px) // 2), pos[1]))
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
        # remembers where the mouse went down to apply a drag threshold
        self.press_pos = None
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
            new_w = sw + max(0, self.stretch_px)
            stretched = pg.transform.smoothscale(self._orig_image, (new_w, sh))
        except Exception:
            stretched = pg.transform.scale(self._orig_image, (sw + max(0, self.stretch_px), sh))
        try:
            self.image = stretched.convert_alpha()
        except Exception:
            self.image = stretched
        # keep current topleft constant when scaling
        tl = self.rect.topleft
        self.rect = self.image.get_rect(topleft=tl)

    def snap_to_grid(self):
        # Snap the sprite's topleft to the nearest grid intersection
        try:
            gx, gy = GRID_ORIGIN
        except Exception:
            gx, gy = (0, 0)
        # apply global grid offset if configured
        try:
            gx = int(gx) + int(GRID_OFFSET_X)
        except Exception:
            gx = int(gx)
        try:
            gy = int(gy) + int(GRID_OFFSET_Y)
        except Exception:
            gy = int(gy)
        try:
            gs = int(GRID_SIZE)
            if gs <= 0:
                gs = 40
        except Exception:
            gs = 40
        # Align so (rect.x + snap_off_x, rect.y + snap_off_y) lands on grid lines
        nx = gx + round(((self.rect.x + self.snap_off_x) - gx) / gs) * gs - self.snap_off_x
        ny = gy + round(((self.rect.y + self.snap_off_y) - gy) / gs) * gs - self.snap_off_y
        self.rect.x = int(nx)
        self.rect.y = int(ny)

    def select(self, mouse_pos):
        mx, my = mouse_pos
        ox = mx - self.rect.x
        oy = my - self.rect.y
        self._offset = (ox, oy)
        # mark as selected; don't start dragging until threshold is exceeded
        self.selected = True
        self.dragging = False
        self.press_pos = (mx, my)
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
            expected_default = (int(self.default_pos[0]) - (max(0, self.stretch_px) // 2), int(self.default_pos[1]))
            if self.rect.topleft != expected_default:
                self.moved_from_default = True
                self.in_tray = False
        except Exception:
            self.moved_from_default = True
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
            expected_default = (int(self.default_pos[0]) - (max(0, self.stretch_px) // 2), int(self.default_pos[1]))
            if self.rect.topleft != expected_default:
                self.moved_from_default = True
            self.in_tray = (self.rect.topleft == expected_default)
        except Exception:
            self.in_tray = False

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

    def clone(self):
        """Create a duplicate sprite with the same image and default position.
        Used for creating replacement sprites in the tray when user drags one out.
        """
        try:
            new_sprite = Draggable(self._orig_image, pos=self.default_pos, scale=self.scale, stretch_px=self.stretch_px, snap_offset=(self.snap_off_x, self.snap_off_y))
            # Copy sprite_info if it exists
            if hasattr(self, 'sprite_info'):
                new_sprite.sprite_info = self.sprite_info
            return new_sprite
        except Exception:
            return None

    def update(self):
        # If not currently being dragged, ensure the sprite rests on the grid.
        # This allows a sprite to remain selected while snapping when idle.
        if not self.dragging and self.snap_enabled:
            try:
                self.snap_to_grid()
            except Exception:
                pass

    # removed anchor helper; rect.topleft represents sprite position


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