#EECE 2140 Final Project - Main Code
#Written by David Charles 

# import libraries
import pygame as pg
import os 
import time
# import settings and sprites
from os import path
from settings import *
from sprites import *
from LogicGates import *

# set up assets folders
project_folder = os.path.dirname(__file__)
img_folder = os.path.join(project_folder, "Images")    

class Game:
    def __init__(self):
        # init game window etc.
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption("EECE 2140 Final Project")
        self.clock = pg.time.Clock()
        self.running = True
        # currently selected draggable sprite (if any)
        self.selected_sprite = None
        # tray state (false = main background only, true = tray open and sprites visible)
        self.tray_open = False
        # button rectangle for toggling tray (placed inside header, next to title)
        self.tray_button_rect = pg.Rect(WIDTH//2 + 628, 26, 115, 60)
        # reset button placed next to the 'Blocks' button with same dimensions
        self.reset_button_rect = pg.Rect(self.tray_button_rect.right - 245, self.tray_button_rect.top, self.tray_button_rect.width, self.tray_button_rect.height)
        # will hold draggable sprites for the tray (created in load_data)
        self.tray_sprites = []
        # tray sprite background (created in load_data, added/removed from group on toggle)
        self.tray_sprite = None
        print(self.screen)
    # sprite and background images
    def load_data(self):
        #insert sprites here
        self.and2_img = pg.image.load(path.join(img_folder, "AND2.png")).convert_alpha()
        self.nand2_img = pg.image.load(path.join(img_folder, "NAND2.png")).convert_alpha()
        self.or2_img = pg.image.load(path.join(img_folder, "OR2.png")).convert_alpha()
        self.nor2_img = pg.image.load(path.join(img_folder, "NOR2.png")).convert_alpha()
        self.xor2_img = pg.image.load(path.join(img_folder, "XOR2.png")).convert_alpha()
        self.xnor2_img = pg.image.load(path.join(img_folder, "XNOR2.png")).convert_alpha()
        self.not1_img = pg.image.load(path.join(img_folder, "NOT.png")).convert_alpha()
        self.buffer_img = pg.image.load(path.join(img_folder, "BUF.png")).convert_alpha()
        
        #backgrounds & statics
        self.background_main_img = pg.image.load(path.join(img_folder, "Background_main.png")).convert()
        print("Sprites loaded")
        # try to load a tray background; if missing, fall back to main background
        try:
            self.background_tray_img = pg.image.load(path.join(img_folder, "Background_tray.png")).convert()
        except Exception:
            self.background_tray_img = self.background_main_img
        # create a TraySprite that will be shown/hidden when tray opens/closes
        # position it using the TRAY_BOX (so it lines up with the white box)
        # place the tray sprite at the original top-left origin so it overlays correctly
        self.tray_sprite = TraySprite(self.background_tray_img, pos=(0, 0))
        print("Sprites loaded")
            # tray sprites are created and stored in load_data(); they will be added to groups
            # only when the tray is opened by the user. This prevents sprites appearing
            # on program start.
        # Create Draggable instances for the tray palette but do NOT add to groups.
        # Positions are inside the tray area (these are just defaults and can be adjusted).
        try:
            # positions inside the tray area (add more slots for letter sprites)
            tray_positions = [
                (40, 630), (230, 630), (420, 630), (610, 630),
                (40, 750), (230, 750), (420, 750), (610, 750),
                (800, 640), (1040, 640), (920, 640), (800, 750)
            ]

            # start with the loaded gate images
            imgs = [
                self.and2_img, self.nand2_img, self.or2_img, self.nor2_img,
                self.xor2_img, self.xnor2_img, self.not1_img, self.buffer_img
            ]

            # input bit sprites
            try:
                font = pg.font.Font(None, 36)
            except Exception:
                pg.font.init()
                font = pg.font.Font(None, 36)


            # input bit sprites
            for letter in ['A', 'B', 'C']:
                s = pg.Surface((70, 70), pg.SRCALPHA)
                s.fill(BLUE)
                txt = font.render(letter, True, WHITE)
                tr = txt.get_rect(center=(35, 35))
                s.blit(txt, tr)
                imgs.append(s)

            # Output bit sprites
            try:
                out_font = pg.font.Font(None, 36)
            except Exception:
                pg.font.init()
                out_font = pg.font.Font(None, 36)
            s_out = pg.Surface((114, 70), pg.SRCALPHA)
            s_out.fill(BLUE)
            txt_out = out_font.render('OUT', True, WHITE)
            tr_out = txt_out.get_rect(center=(57, 35))
            s_out.blit(txt_out, tr_out)
            imgs.append(s_out)

            # create Draggable instances for all images, but do NOT add to sprite groups yet
            self.tray_sprites = []
            for pos, img in zip(tray_positions, imgs):
                dr = Draggable(img, pos=pos, scale=0.8)
                self.tray_sprites.append(dr)
        except Exception:
            # if anything goes wrong creating tray sprites, ensure list exists but empty
            self.tray_sprites = []

    def new(self):
        # starting a new game
        self.load_data()


        # allows game to access sprites libraries
        self.all_sprites = pg.sprite.Group()
        self.gates = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        # separate group for the tray background sprite
        self.tray_ui = pg.sprite.Group()

        for plat in PLATFORM_LIST:
            p = Platform(*plat)
            self.all_sprites.add(p)
            self.platforms.add(p)
        
        # tray sprites are created and stored in load_data(); they will be added to groups only when the tray is opened
        # (this keeps sprites hidden by default on program start)
        # If you want the tray open on startup, set self.tray_open = True before calling new()

        # if the tray should be open on start, add stored tray sprites and tray background to groups
        if self.tray_open:
            self.tray_ui.add(self.tray_sprite)
            for dr in self.tray_sprites:
                self.all_sprites.add(dr)
                self.gates.add(dr)
        # start the game loop
        self.run()

    def draw_grid_overlay(self):
        # Draw a debug grid overlay on the white box area
        # Grid covers the full white box when tray is closed, and the visible white area when tray is open
        if not SHOW_GRID:
            return
        try:
            gx, gy = GRID_ORIGIN
            gs = int(GRID_SIZE)
            color = GRID_COLOR
            tx, ty, tw, th, border = TRAY_BOX
        except Exception:
            return
        
        # Compute white box inner bounds (inside the blue border).
        # Keep an additional padding so grid lines don't touch the blue border.
        try:
            pad = int(GRID_BORDER_PADDING)
        except Exception:
            pad = 0
        inset = border + pad
        box_left = tx + inset
        box_top = ty + inset
        box_right = tx + tw - inset
        box_bottom = ty + th - inset

        # If the tray is open, shrink the grid bottom by GRID_TRAY_SHRINK pixels
        # then optionally extend it downward by GRID_TRAY_EXTENSION to better match the white box.
        try:
            shrink = int(GRID_TRAY_SHRINK)
        except Exception:
            shrink = 400
        try:
            extend = int(GRID_TRAY_EXTENSION)
        except Exception:
            extend = 0

        if self.tray_open:
            box_bottom = box_bottom - shrink + extend
            if box_bottom < box_top:
                box_bottom = box_top

        # Draw vertical grid lines (only inside white box)
        x = gx
        while x < box_right:
            if x >= box_left:
                pg.draw.line(self.screen, color, (x, box_top), (x, box_bottom), 1)
            x += gs

        # Draw horizontal grid lines (only inside white box)
        y = gy
        while y < box_bottom:
            if y >= box_top:
                pg.draw.line(self.screen, color, (box_left, y), (box_right, y), 1)
            y += gs

        # When tray is open, draw a blue border line at the bottom of the grid area
        # to visually separate grid from the tray.
        if self.tray_open:
            try:
                border_width = int(border)
            except Exception:
                border_width = 3
            pg.draw.line(self.screen, BLUE, (box_left, box_bottom), (box_right, box_bottom), border_width)

    def draw(self):
        # draw main background
        self.screen.blit(self.background_main_img, (0,0))
        # draw tray background sprite if tray is open (so sprites render on top of it)
        try:
            self.tray_ui.draw(self.screen)
        except Exception:
            pass
        # draw debug grid overlay (behind sprites so sprites appear above the grid)
        self.draw_grid_overlay()

        # draw all sprites
        try:
            self.all_sprites.draw(self.screen)
            # draw highlight rectangle for selected draggable sprite(s)
            for sprite in self.all_sprites:
                if getattr(sprite, 'selected', False):
                    pg.draw.rect(self.screen, RED, sprite.rect, 3)
        except Exception:
            # if groups not yet ready, skip drawing sprites
            pass
        # draw tray toggle button (simple rectangle + label)
        try:
            pg.draw.rect(self.screen, BLUE, self.tray_button_rect)
            self.draw_text("Blocks", 36, WHITE, self.tray_button_rect.centerx, self.tray_button_rect.centery - 20)
            # draw reset button to the right of the blocks button
            pg.draw.rect(self.screen, RED, self.reset_button_rect)
            self.draw_text("Reset", 28, WHITE, self.reset_button_rect.centerx, self.reset_button_rect.centery - 18)
        except Exception:
            pass
        pg.display.flip()

    def run(self):
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            #self.player.checkpos()
            self.events()
            self.update()
            self.draw()
            # print(self.player.pos.x)

    def draw_text(self, text, size, color, x, y):
        font_name = pg.font.match_font('arial')
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x,y)
        self.screen.blit(text_surface, text_rect)

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            # Handle mouse interaction for draggable sprites and UI
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos

                # Check tray and reset buttons first
                if self.tray_button_rect.collidepoint(mouse_pos):
                    self.tray_open = not self.tray_open
                    if self.tray_open:
                        # Add all tray sprites to groups
                        for sprite in self.tray_sprites:
                            if sprite not in self.all_sprites:
                                self.all_sprites.add(sprite)
                            if sprite not in self.gates:
                                self.gates.add(sprite)
                    else:
                        # Remove only sprites at default position
                        for sprite in self.tray_sprites:
                            if sprite.rect.topleft == sprite.default_pos:
                                self.all_sprites.remove(sprite)
                                self.gates.remove(sprite)
                    continue

                if self.reset_button_rect.collidepoint(mouse_pos):
                    # Reset tray sprites to their defaults
                    self.reset_tray_positions()
                    # If tray is closed, hide defaulted sprites (remove from groups)
                    if not self.tray_open:
                        for sprite in list(self.tray_sprites):
                            try:
                                if sprite in self.all_sprites:
                                    self.all_sprites.remove(sprite)
                                if sprite in self.gates:
                                    self.gates.remove(sprite)
                            except Exception:
                                pass
                        # Clear selection if it pointed to a removed sprite
                        try:
                            if self.selected_sprite and self.selected_sprite in self.tray_sprites:
                                self.selected_sprite = None
                        except Exception:
                            pass
                    continue

                # Check if click is on any tray sprite (topmost first)
                clicked_sprite = None
                for sprite in reversed(self.tray_sprites):
                    if sprite.rect.collidepoint(mouse_pos):
                        clicked_sprite = sprite
                        break

                if clicked_sprite:
                    # Switch selection to the clicked sprite
                    if self.selected_sprite and self.selected_sprite != clicked_sprite:
                        self.selected_sprite.deselect()
                    self.selected_sprite = clicked_sprite
                    self.selected_sprite.select(mouse_pos)
                else:
                    # Clicked empty space: deselect any selected sprite
                    if self.selected_sprite:
                        self.selected_sprite.deselect()
                        self.selected_sprite = None

            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if self.selected_sprite:
                    self.selected_sprite.dragging = False

            elif event.type == pg.MOUSEMOTION:
                if self.selected_sprite and self.selected_sprite.dragging:
                    self.selected_sprite.move(event.pos)

    def update(self):
        self.all_sprites.update()

    def reset_tray_positions(self):
        """Reset all tray palette sprites to their original default positions.
        This moves any sprite whose current topleft differs from its stored
        `default_pos` back to that default and clears selection state.
        """
        if not hasattr(self, 'tray_sprites') or not self.tray_sprites:
            return
        for sprite in self.tray_sprites:
            try:
                dp = getattr(sprite, 'default_pos', None)
                if dp is None:
                    continue
                # if sprite not at default, move it back
                if (sprite.rect.x, sprite.rect.y) != (int(dp[0]), int(dp[1])):
                    sprite.rect.topleft = (int(dp[0]), int(dp[1]))
                # clear any selection and flags
                sprite.selected = False
                if hasattr(sprite, 'dragging'):
                    sprite.dragging = False
                if hasattr(sprite, 'moved_from_default'):
                    sprite.moved_from_default = False
                if hasattr(sprite, 'snap_enabled'):
                    sprite.snap_enabled = False
            except Exception:
                pass

    def get_mouse_now(self):
        x,y = pg.mouse.get_pos()
        return (x,y)
    
# instantiates game class
g = Game()

# kick off the game loop
while g.running:
    g.new()

pg.quit()