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
        # create draggable sprites for each gate image so user can pick them up
        try:
            # positions for initial placement (moved downward into the block area)
            positions = [(150, 300), (300, 300), (450, 300), (150, 440), (300, 440), (450, 440), (600, 300), (600, 440)]
            imgs = [self.and2_img, self.nand2_img, self.or2_img, self.nor2_img, self.xor2_img, self.xnor2_img, self.not1_img, self.buffer_img]
            for img, pos in zip(imgs, positions):
                # Draggable class is defined in sprites.py (imported via from sprites import *)
                # create a slightly larger sprite (scale=1.25)
                dr = Draggable(img, pos, scale=1.25)
                # add to sprite groups if they exist; new() will add later if not
                try:
                    self.all_sprites.add(dr)
                except Exception:
                    pass
        except Exception:
            # if Draggable isn't available or images missing, continue without creating
            pass

    def new(self):
        # starting a new game
        self.load_data()


        # allows game to access sprites libraries
        self.all_sprites = pg.sprite.Group()
        self.gates = pg.sprite.Group()
        self.platforms = pg.sprite.Group()

        for plat in PLATFORM_LIST:
            p = Platform(*plat)
            self.all_sprites.add(p)
            self.platforms.add(p)
        
        # create draggable gate sprites now that groups exist
        try:
            # place gate sprites inside the 'block and gates' box on the background
            positions = [(20, 590), (270, 590), (530, 590), (20, 730), (270, 730), (530, 730), (780, 590), (780, 730)]
            imgs = [self.and2_img, self.nand2_img, self.or2_img, self.nor2_img, self.xor2_img, self.xnor2_img, self.not1_img, self.buffer_img]
            for img, pos in zip(imgs, positions):
                dr = Draggable(img, pos, scale=1.25)
                self.all_sprites.add(dr)
                self.gates.add(dr)
        except Exception:
            pass

        # start the game loop
        self.run()

    def draw(self):
        self.screen.blit(self.background_main_img, (0,0))
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
            # Handle mouse interaction for draggable sprites
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                # iterate in reverse draw order so topmost sprite is selected
                if hasattr(self, 'all_sprites'):
                    for sprite in reversed(self.all_sprites.sprites()):
                        if sprite.rect.collidepoint(pos) and hasattr(sprite, 'select'):
                            sprite.select(pos)
                            self.selected_sprite = sprite
                            # bring sprite to front by re-adding to group
                            self.all_sprites.remove(sprite)
                            self.all_sprites.add(sprite)
                            break

            elif event.type == pg.MOUSEMOTION:
                if self.selected_sprite and hasattr(self.selected_sprite, 'move'):
                    self.selected_sprite.move(event.pos)

            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if self.selected_sprite and hasattr(self.selected_sprite, 'deselect'):
                    self.selected_sprite.deselect()
                self.selected_sprite = None
    
    def update(self):
        self.all_sprites.update()

    def get_mouse_now(self):
        x,y = pg.mouse.get_pos()
        return (x,y)
    
# instantiates game class
g = Game()

# kick off the game loop
while g.running:
    g.new()

pg.quit()