#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 24 16:07:08 2025

@author: kyrapallod

Logic gate helper module.

If the PyPI library 'pygates' / 'PyGates' is installed, this module will
use it internally. Otherwise it falls back to local gate implementations.
"""

# Try to import external library
HAVE_PYGATES = False
try:
    import PyGates  # as shown on the PyPI page
    HAVE_PYGATES = True
except ImportError:
    try:
        import pygates as PyGates
        HAVE_PYGATES = True
    except ImportError:
        HAVE_PYGATES = False


# Local Logic Gate Classes

class ANDGate:
    def __init__(self, a, b):
        self.a = int(a)
        self.b = int(b)

    def output(self):
        return int(self.a and self.b)


class ORGate:
    def __init__(self, a, b):
        self.a = int(a)
        self.b = int(b)

    def output(self):
        # SWAPPED: OR image shows NOR gate, so compute NOR logic
        return int(not (self.a or self.b))


class NOTGate:
    def __init__(self, a):
        self.a = int(a)

    def output(self):
        return int(not self.a)


class NANDGate:
    def __init__(self, a, b):
        self.a = int(a)
        self.b = int(b)

    def output(self):
        return int(not (self.a and self.b))


class NORGate:
    def __init__(self, a, b):
        self.a = int(a)
        self.b = int(b)

    def output(self):
        # SWAPPED: NOR image shows OR gate, so compute OR logic
        return int(self.a or self.b)


class XORGate:
    def __init__(self, a, b):
        self.a = int(a)
        self.b = int(b)

    def output(self):
        return int(self.a ^ self.b)


class XNORGate:
    def __init__(self, a, b):
        self.a = int(a)
        self.b = int(b)

    def output(self):
        return int(not (self.a ^ self.b))


class BUFGate:
    """Buffer: output = input."""
    def __init__(self, a):
        self.a = int(a)

    def output(self):
        return int(self.a)


# ----------------- Helper Function -----------------

def _use_pygates(gate_type, a, b=None):
    """Try to evaluate using external PyGates library, if present."""
    if not HAVE_PYGATES:
        return None

    # Convert to proper booleans
    A = bool(int(a))
    B = bool(int(b)) if b is not None else None

    gt = gate_type.upper()
    try:
        if gt == "AND":
            return int(PyGates.Gates.AND(A, B))
        elif gt == "OR":
            return int(PyGates.Gates.OR(A, B))
        elif gt == "NOT":
            return int(PyGates.Gates.NOT(A))
        elif gt == "NAND":
            return int(PyGates.Gates.NAND(A, B))
        elif gt == "NOR":
            return int(PyGates.Gates.NOR(A, B))
        elif gt == "XOR":
            return int(PyGates.Gates.XOR(A, B))
        elif gt == "XNOR":
            return int(PyGates.Gates.XNOR(A, B))
        elif gt in ("BUF", "BUFFER"):
            # PyGates may not have buffer; just pass-through
            return int(A)
    except Exception:
        # Fall back to local implementation if it doesnt work
        return None

    return None


def create_gate(gate_type, a, b=None):
    """Evaluate a gate of type gate_type on inputs a, b (0/1 ints)."""
    gate_type = str(gate_type).upper()
    a = int(a)
    if b is not None:
        b = int(b)

    # 1) Try external PyGates if available
    result = _use_pygates(gate_type, a, b)
    if result is not None:
        return result

    # 2) Fall back to local implementations
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
    elif gate_type in ("BUF", "BUFFER"):
        return BUFGate(a).output()
    else:
        print(f"Invalid gate '{gate_type}'. Defaulting output to 0.")
        return 0

