#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 24 16:07:08 2025

@author: kyrapallod
"""
# Logic Gate Classes
class ANDGate:
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def output(self):
        return int(self.a and self.b)


class ORGate:
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def output(self):
        return int(self.a or self.b)


class NOTGate:
    def __init__(self, a):
        self.a = a
    def output(self):
        return int(not self.a)


class NANDGate:
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def output(self):
        return int(not (self.a and self.b))


class NORGate:
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def output(self):
        return int(not (self.a or self.b))


class XORGate:
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def output(self):
        return int(self.a != self.b)


class XNORGate:
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def output(self):
        return int(self.a == self.b)


# Helper Function to Create Gates Dynamically
def create_gate(gate_type, a, b=None):
    gate_type = gate_type.upper()

    if gate_type == "AND":
        return ANDGate(a, b).output()
    elif gate_type == "OR":
        return ORGate(a, b).output()
    elif gate_type == "NOT":
        return NOTGate(a).output()
    elif gate_type == "NAND":
        return NANDGate(a, b).output()
    elif gate_type == "NOR":
        return NORGate(a, b).output()
    elif gate_type == "XOR":
        return XORGate(a, b).output()
    elif gate_type == "XNOR":
        return XNORGate(a, b).output()
    else:
        print("Invalid gate. Defaulting output to 0.")
        return 0

