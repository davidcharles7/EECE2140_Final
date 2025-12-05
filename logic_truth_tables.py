# logic_truth_table.py
# written by Bethany Davies
# generates truth tables for the user's built circuit.
# Opens a pygame popup window to display the full truth table.

import pygame as pg
from itertools import product
from main import *
from settings import *
from LogicGates import *


# ===================================================================
#   CIRCUIT EVALUATOR CLASS
# ===================================================================

class CircuitEvaluator:
    """Evaluates a circuit by building a dependency graph from wires and gates."""
    
    def __init__(self, all_sprites, tray_sprites, wires):
        try:
            print("CircuitEvaluator __init__ called")
            self.all_sprites = all_sprites
            self.tray_sprites = tray_sprites
            self.wires = wires
            
            # Get circuit sprites (not in tray)
            self.circuit_sprites = [s for s in all_sprites if s not in tray_sprites]
            print(f"Circuit sprites: {len(self.circuit_sprites)}, Tray sprites: {len(tray_sprites)}")
            
            # Build wire connectivity map
            self.build_connectivity()
        except Exception as e:
            print(f"ERROR in CircuitEvaluator.__init__: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def build_connectivity(self):
        """Build a map of which sprites/nodes are connected by wires."""
        self.connections = {}  # (sprite, node_name) -> set of (connected_sprite, connected_node)
        
        print(f"\n  Building connectivity from {len(self.wires)} wires...")
        
        for wire in self.wires:
            # Direct wire connections
            if wire.start_connection and wire.end_connection:
                start = wire.start_connection
                end = wire.end_connection
                
                if start not in self.connections:
                    self.connections[start] = set()
                if end not in self.connections:
                    self.connections[end] = set()
                
                # Bidirectional connection
                self.connections[start].add(end)
                self.connections[end].add(start)
                
                # Debug: show what we connected
                start_sprite, start_node = start
                end_sprite, end_node = end
                start_type = getattr(start_sprite, 'node_type', None) or getattr(start_sprite, 'gate_type', 'gate')
                end_type = getattr(end_sprite, 'node_type', None) or getattr(end_sprite, 'gate_type', 'gate')
                print(f"    Wire: {start_type}.{start_node} <-> {end_type}.{end_node}")
            
            # Handle wire-to-wire connections (junctions)
            if len(wire.wire_connections) > 0:
                print(f"    Wire has {len(wire.wire_connections)} wire-to-wire junctions")
                
                for other_wire, intersection in wire.wire_connections:
                    # Connect all endpoints of connected wires
                    wire_endpoints = []
                    if wire.start_connection:
                        wire_endpoints.append(wire.start_connection)
                    if wire.end_connection:
                        wire_endpoints.append(wire.end_connection)
                    
                    other_endpoints = []
                    if other_wire.start_connection:
                        other_endpoints.append(other_wire.start_connection)
                    if other_wire.end_connection:
                        other_endpoints.append(other_wire.end_connection)
                    
                    # Connect all combinations
                    for ep1 in wire_endpoints:
                        if ep1 not in self.connections:
                            self.connections[ep1] = set()
                        for ep2 in other_endpoints:
                            if ep2 not in self.connections:
                                self.connections[ep2] = set()
                            self.connections[ep1].add(ep2)
                            self.connections[ep2].add(ep1)
                            
                            # Debug
                            s1, n1 = ep1
                            s2, n2 = ep2
                            t1 = getattr(s1, 'node_type', None) or getattr(s1, 'gate_type', 'gate')
                            t2 = getattr(s2, 'node_type', None) or getattr(s2, 'gate_type', 'gate')
                            print(f"      Junction: {t1}.{n1} <-> {t2}.{n2}")
    
    def trace_value(self, sprite, node_name, gate_outputs, visited=None, depth=0, verbose=False):
        """Trace back to find the value at a specific node."""
        if visited is None:
            visited = set()
        
        key = (sprite, node_name)
        if key in visited:
            return None
        visited.add(key)
        
        indent = "  " * depth
        sprite_type = getattr(sprite, 'node_type', None) or getattr(sprite, 'gate_type', '?')
        
        # Check connections
        if key not in self.connections:
            # Debug: why no connections?
            if verbose:
                print(f"{indent}trace_value: {sprite_type}.{node_name} has NO connections")
            return None
        
        num_connections = len(self.connections[key])
        if verbose:
            print(f"{indent}trace_value: {sprite_type}.{node_name} has {num_connections} connections")
        
        # First pass: check for direct input blocks or ready gate outputs
        for connected_sprite, connected_node in self.connections[key]:
            node_type = getattr(connected_sprite, 'node_type', None)
            conn_gate_type = getattr(connected_sprite, 'gate_type', None)
            
            # If connected to an input block output
            if node_type == 'input' and 'output' in connected_node.lower():
                val = getattr(connected_sprite, 'bit_value', 0)
                if verbose:
                    conn_id = id(connected_sprite)
                    print(f"{indent}  -> found input value = {val} from {node_type}.{connected_node} (id={conn_id})")
                return val
            
            # If connected to a gate output that's ready
            if conn_gate_type and 'output' in connected_node.lower():
                gate_id = id(connected_sprite)
                if gate_id in gate_outputs:
                    val = gate_outputs[gate_id]
                    if verbose:
                        print(f"{indent}  -> found {conn_gate_type} gate output = {val} (id={gate_id})")
                    return val
        
        # Second pass: recurse through other connections if no direct value found
        for connected_sprite, connected_node in self.connections[key]:
            node_type = getattr(connected_sprite, 'node_type', None)
            conn_gate_type = getattr(connected_sprite, 'gate_type', None)
            conn_id = id(connected_sprite)
            
            # Skip input blocks and gate outputs (already checked above)
            if node_type == 'input' and 'output' in connected_node.lower():
                continue
            if conn_gate_type and 'output' in connected_node.lower():
                gate_id = id(connected_sprite)
                if gate_id not in gate_outputs:
                    if verbose:
                        print(f"{indent}  -> {conn_gate_type} gate output not ready yet (id={gate_id})")
                continue
            
            # Recurse through other connections
            if verbose:
                conn_label = f"{node_type or conn_gate_type}.{connected_node} (id={conn_id})"
                print(f"{indent}  -> recursing to {conn_label}")
            value = self.trace_value(connected_sprite, connected_node, gate_outputs, visited, depth+1, verbose)
            if value is not None:
                if verbose:
                    print(f"{indent}  -> got value {value} from recursion")
                return value
        
        if verbose:
            print(f"{indent}trace_value: no value found for {sprite_type}.{node_name}")
        return None
    
    def evaluate(self, input_values):
        """Evaluate circuit for given input values dict {label: value}."""
        print(f"\n=== CircuitEvaluator: Evaluating with {input_values} ===")
        
        # Set input block values
        for sprite in self.circuit_sprites:
            if getattr(sprite, 'node_type', None) == 'input':
                label = getattr(sprite, 'label', None)
                if label in input_values:
                    sprite.bit_value = input_values[label]
                    print(f"  Set input {label} = {input_values[label]}")
        
        # Debug: Show connections
        print(f"  Total connections: {len(self.connections)}")
        
        # Debug: Show what gates we have
        gates = [s for s in self.circuit_sprites if hasattr(s, 'gate_type')]
        print(f"  Gates in circuit: {len(gates)}")
        for gate in gates:
            gate_type = getattr(gate, 'gate_type', '?')
            nodes = getattr(gate, 'nodes', {})
            gate_id = id(gate)
            sprite_info = getattr(gate, 'sprite_info', 'Unknown')
            
            # DEBUG: Show all gate attributes
            print(f"    - {gate_type} gate (id={gate_id})")
            print(f"      sprite_info: '{sprite_info}'")
            print(f"      nodes: {list(nodes.keys())}")
            print(f"      is_cloneable: {getattr(gate, 'is_cloneable', 'N/A')}")
            print(f"      in_tray: {gate in self.tray_sprites}")
            
            # Show what this gate is connected to
            for node_name, node_pos in nodes.items():
                if 'output' in node_name.lower():
                    key = (gate, node_name)
                    if key in self.connections:
                        print(f"      {gate_type}.{node_name} connects to:")
                        for conn_sprite, conn_node in self.connections[key]:
                            conn_type = getattr(conn_sprite, 'node_type', None) or getattr(conn_sprite, 'gate_type', 'gate')
                            conn_id = id(conn_sprite)
                            print(f"        -> {conn_type}.{conn_node} (id={conn_id})")
        
        # Track gate outputs
        gate_outputs = {}  # gate_id -> output_value
        
        # Iteratively evaluate gates until stable
        max_iterations = 100
        for iteration in range(max_iterations):
            changed = False
            evaluated_this_iter = 0
            gates_still_waiting = 0
            
            for sprite in self.circuit_sprites:
                gate_type = getattr(sprite, 'gate_type', None)
                if not gate_type:
                    continue
                
                gate_id = id(sprite)
                
                # Get input node names
                nodes = getattr(sprite, 'nodes', {})
                input_nodes = [n for n in nodes.keys() if 'input' in n.lower()]
                
                # Trace values for each input
                input_vals = []
                for node_name in sorted(input_nodes):
                    # Enable verbose tracing for OR gate in early iterations
                    is_verbose = (gate_type == 'OR' and iteration <= 2)
                    if is_verbose and node_name == sorted(input_nodes)[0]:
                        print(f"\n  === Iteration {iteration+1}: Evaluating {gate_type} gate (id={gate_id}) ===")
                    val = self.trace_value(sprite, node_name, gate_outputs, verbose=is_verbose)
                    if val is not None:
                        input_vals.append(val)
                        if is_verbose:
                            print(f"    {gate_type}.{node_name} = {val}")
                    else:
                        # Debug: why can't we find this value?
                        if iteration == 0:
                            print(f"    - {gate_type} {node_name}: cannot find value yet")
                            # Show what this node is connected to
                            key = (sprite, node_name)
                            if key in self.connections:
                                print(f"      Connected to {len(self.connections[key])} nodes:")
                                for conn_sprite, conn_node in self.connections[key]:
                                    conn_type = getattr(conn_sprite, 'node_type', None) or getattr(conn_sprite, 'gate_type', 'gate')
                                    conn_id = id(conn_sprite)
                                    print(f"        - {conn_type}.{conn_node} (id={conn_id})")
                        if is_verbose:
                            print(f"    {gate_type}.{node_name} = None (not found)")
                            print(f"    Current gate_outputs: {gate_outputs}")
                
                # Evaluate gate if we have enough inputs
                new_output = None
                if gate_type in ['NOT', 'BUF', 'BUFFER'] and len(input_vals) >= 1:
                    new_output = create_gate(gate_type, input_vals[0])
                    if gate_outputs.get(gate_id) != new_output:
                        print(f"  Iter {iteration+1}: {gate_type}({input_vals[0]}) -> {new_output} [gate_id={gate_id}]")
                        evaluated_this_iter += 1
                elif len(input_vals) >= 2:
                    # Debug: show exactly what gate and inputs we're using
                    new_output = create_gate(gate_type, input_vals[0], input_vals[1])
                    if gate_outputs.get(gate_id) != new_output:
                        print(f"  Iter {iteration+1}: {gate_type}({input_vals[0]}, {input_vals[1]}) -> {new_output} [gate_id={gate_id}]")
                        evaluated_this_iter += 1
                    # Always show OR gate inputs for debugging
                    elif gate_type == 'OR' and iteration <= 2:
                        print(f"  Iter {iteration+1}: {gate_type}({input_vals[0]}, {input_vals[1]}) -> {new_output} (unchanged) [gate_id={gate_id}]")
                elif len(input_vals) < 2 and gate_type not in ['NOT', 'BUF', 'BUFFER']:
                    # Two-input gate still waiting for inputs
                    gates_still_waiting += 1
                    if iteration == 0:
                        print(f"    - {gate_type} gate waiting for second input (only has {input_vals})")
                
                # Update if changed
                if new_output is not None and gate_outputs.get(gate_id) != new_output:
                    gate_outputs[gate_id] = new_output
                    changed = True
            
            if not changed and gates_still_waiting == 0:
                print(f"  Circuit stabilized after {iteration+1} iterations ({evaluated_this_iter} gates evaluated)")
                break
            elif not changed and gates_still_waiting > 0:
                # Nothing changed but gates still waiting - likely a circuit issue
                print(f"  WARNING: Circuit did not stabilize - {gates_still_waiting} gates still waiting for inputs after iteration {iteration+1}")
                # Continue for a few more iterations in case values propagate
                if iteration > 2:
                    break
        
        # Get output value
        for sprite in self.circuit_sprites:
            if getattr(sprite, 'node_type', None) == 'output':
                # Trace value from output block's input nodes
                nodes = getattr(sprite, 'nodes', {})
                print(f"\n  Tracing output block connections:")
                for node_name in nodes.keys():
                    if 'input' in node_name.lower():
                        print(f"    Checking output.{node_name}...")
                        value = self.trace_value(sprite, node_name, gate_outputs, verbose=True)
                        if value is not None:
                            print(f"  Final output: {value} (from {node_name})")
                            return value
                print(f"  Output block found but couldn't trace value")
        
        print(f"  Final output: None (no value found)")
        return None


# ===================================================================
#   FULL CIRCUIT TRUTH TABLE GENERATION
# ===================================================================

def generate_circuit_truth_table(input_labels, circuit_evaluator):
    """
    Generates truth table for entire circuit.

    input_labels: ['A','B','C']  (order matters)
    circuit_evaluator: function that takes {"A":0,"B":1,...} -> output_value
    """
    table = []

    for bits in product([0, 1], repeat=len(input_labels)):
        combo = {input_labels[i]: bits[i] for i in range(len(input_labels))}
        out_val = circuit_evaluator(combo)
        table.append((combo, out_val))

    return table


# ===================================================================
#   PYGAME POPUP WINDOW
# ===================================================================

def show_truth_table(table, title="Circuit Truth Table"):
    """Displays the truth table in a pygame popup window."""

    pg.init()
    WIDTH, HEIGHT = 600, 500
    win = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption(title)

    font = pg.font.Font(None, 30)
    title_font = pg.font.Font(None, 42)

    running = True

    # Pre-render table rows
    rendered_rows = []
    for combo, out_val in table:
        row_text = "  ".join(f"{k}={v}" for k, v in combo.items())
        row_text += f"   |   {out_val}"
        rendered_rows.append(font.render(row_text, True, (0, 0, 0)))

    while running:
        win.fill((240, 240, 240))

        # Draw title
        title_surf = title_font.render(title, True, (10, 10, 10))
        win.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 20))

        # Draw rows
        y = 90
        for surf in rendered_rows:
            win.blit(surf, (40, y))
            y += 35

        pg.display.flip()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                running = False

    pg.display.quit()


from logic_truth_tables import generate_circuit_truth_table, show_truth_table

"""
# truth table button next to Undo
self.truth_button_rect = pg.Rect(
    self.undo_button_rect.right - 245,
    self.undo_button_rect.top,
    self.undo_button_rect.width,
    self.undo_button_rect.height
)

# TRUTH TABLE BUTTON
if self.truth_button_rect.collidepoint(mouse_pos):
    self.show_full_circuit_truth_table()
    continue

"""


def show_full_circuit_truth_table(self):
    """Builds and displays truth table for the user's current circuit."""

    # Collect input blocks (A/B/C) 
    inputs = []
    for sprite in self.tray_sprites:
        if getattr(sprite, "node_type", None) == "input":
            inputs.append(sprite.label)

    inputs.sort()

    if not inputs:
        print("No inputs found (A/B/C missing).")
        return

    # Function to evaluate the circuit for one input combo 
    def evaluate_once(bit_dict):
        # Set sprite bit values temporarily
        for sprite in self.tray_sprites:
            if getattr(sprite, "node_type", None) == "input":
                sprite.bit_value = bit_dict[sprite.label]

        # re-evaluate the entire circuit using your built-in logic
        self.evaluate_circuit()

        # read final output block
        for sprite in self.tray_sprites:
            if getattr(sprite, "node_type", None) == "output":
                return sprite.output_value if sprite.output_value is not None else 0

        return 0

    # Build full circuit truth table 
    table = generate_circuit_truth_table(inputs, evaluate_once)

    # Popup display 
    show_truth_table(table, "Circuit Truth Table")
