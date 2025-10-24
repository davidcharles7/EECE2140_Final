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

# set up assets folders
game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, "Images")    

class Game:
    def __init__(self):
        # init game window etc.
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption("EECE 2140 Final Project")
        self.clock = pg.time.Clock()
        self.running = True
        print(self.screen)
    # sprite and background images
    def load_data(self):
        #insert sprites here
        print("Sprites loaded")

    def new(self):
        # starting a new game
        self.load_data()


        # allows game to access sprites libraries
        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()

        for plat in PLATFORM_LIST:
            p = Platform(*plat)
            self.all_sprites.add(p)
            self.platforms.add(p)
        
        #self.all_sprites.add(self)
        self.run()    

    def run(self):
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            # checkpos makes sure player stays inbounds
            #self.player.checkpos()
            #self.events()
            #self.update()
            #self.draw()
            # print(self.player.pos.x)

    def get_mouse_now(self):
        x,y = pg.mouse.get_pos()
        return (x,y)
    
# instantiates game class
g = Game()

# kick off the game loop
while g.running:
    g.new()

pg.quit()