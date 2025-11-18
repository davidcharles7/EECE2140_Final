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

        # Logic Gate attributes
        self.gate_type = variant.upper()
        self.input_a = 0
        self.input_b = 0
        self.output = 0

        # NOT gate uses only one input
        if self.gate_type == "NOT":
            self.input_b = None

    def compute_output(self):
        """Compute output using LogicGates.py"""
        if self.gate_type == "NOT":
            self.output = create_gate(self.gate_type, self.input_a)
        else:
            self.output = create_gate(self.gate_type, self.input_a, self.input_b)
        return self.output

    def set_input(self, input_number, value):
        """Set input A or B and recompute output."""
        if input_number == 1:
            self.input_a = value
        elif input_number == 2 and self.gate_type != "NOT":
            self.input_b = value
        self.compute_output()
