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


# --- Helper Function to Create Gates Dynamically ---
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


#  Main Program 
def main():
    print("\n=== Custom 3-Gate Circuit Simulator ===")
    print("Available gates: AND, OR, NOT, NAND, NOR, XOR, XNOR\n")

    # Inputs for first gate
    a = int(input("Enter input A (0 or 1): "))
    b = int(input("Enter input B (0 or 1): "))

    # Choose and evaluate three gates in sequence
    prev_output = None

    for i in range(1, 4):
        print(f"\n--- Gate {i} ---")
        gate_type = input("Choose gate type: ").strip().upper()

        if i == 1:
            # First gate uses A and 
            if gate_type == "NOT":
                prev_output = create_gate(gate_type, a)
            else:
                prev_output = create_gate(gate_type, a, b)
        else:
            # Subsequent gates use previous output + a new input if needed
            if gate_type == "NOT":
                prev_output = create_gate(gate_type, prev_output)
            else:
                next_input = int(input("Enter next input (0 or 1): "))
                prev_output = create_gate(gate_type, prev_output, next_input)

        print(f"Output of Gate {i} ({gate_type}): {prev_output}")

    print(f"\nFinal Circuit Output: {prev_output}\n")


if __name__ == "__main__":
    main()
