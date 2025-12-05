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
from logic_truth_tables import *

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
        # another selection: currently selected wire (for deletion)
        self.selected_wire = None
        # tray state (false = main background only, true = tray open and sprites visible)
        self.tray_open = False
        # button rectangle for toggling tray (placed inside header, next to title)
        self.tray_button_rect = pg.Rect(WIDTH//2 + 628, 26, 115, 60)
        # reset button placed next to the 'Blocks' button with same dimensions
        self.reset_button_rect = pg.Rect(self.tray_button_rect.right - 245, self.tray_button_rect.top, self.tray_button_rect.width, self.tray_button_rect.height)
        # play button placed next to the reset button (in delete button's old position)
        self.play_button_rect = pg.Rect(self.reset_button_rect.right - 245, self.reset_button_rect.top, self.reset_button_rect.width, self.reset_button_rect.height)
        # info button placed next to play button
        self.info_button_rect = pg.Rect(self.play_button_rect.right - 245, self.play_button_rect.top, self.play_button_rect.width, self.play_button_rect.height)
        # undo button placed next to info button
        self.undo_button_rect = pg.Rect(self.info_button_rect.right - 245, self.info_button_rect.top, self.info_button_rect.width, self.info_button_rect.height)
        # wire button placed in tray area (bottom left)
        self.wire_button_rect = pg.Rect(800, 750, 115, 60)
        # info display state
        self.show_info = False
        self.info_sprite = None
        # wire drawing mode
        self.wire_mode = False
        self.current_wire = None  # Wire being drawn
        # will hold draggable sprites for the tray (created in load_data)
        self.tray_sprites = []
        # tray sprite background (created in load_data, added/removed from group on toggle)
        self.tray_sprite = None
        # track which tray sprites need cloning when dragged outside tray
        self.pending_clones = []
        # undo stack: stores actions as dicts with type and necessary state to reverse
        self.undo_stack = []
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
        
        # Load truth table images
        self.and_table_img = pg.image.load(path.join(img_folder, "AND_TABLE.png")).convert_alpha()
        self.nand_table_img = pg.image.load(path.join(img_folder, "NAND_TABLE.png")).convert_alpha()
        self.or_table_img = pg.image.load(path.join(img_folder, "OR_TABLE.png")).convert_alpha()
        self.nor_table_img = pg.image.load(path.join(img_folder, "NOR_TABLE.png")).convert_alpha()
        self.xor_table_img = pg.image.load(path.join(img_folder, "XOR_TABLE.png")).convert_alpha()
        self.xnor_table_img = pg.image.load(path.join(img_folder, "XNOR_TABLE.png")).convert_alpha()
        self.not_table_img = pg.image.load(path.join(img_folder, "NOT_TABLE.png")).convert_alpha()
        self.buf_table_img = pg.image.load(path.join(img_folder, "BUF_TABLE.png")).convert_alpha()
        
        #backgrounds & statics
        self.background_main_img = pg.image.load(path.join(img_folder, "Background_main.png")).convert()
        print("Sprites loaded")
        # try to load a tray background; if missing, fall back to main background
        try:
            self.background_tray_img = pg.image.load(path.join(img_folder, "Background_tray.png")).convert()
        except Exception:
            self.background_tray_img = self.background_main_img
        # create a TraySprite that will be shown/hidden when tray opens/closes
        self.tray_sprite = TraySprite(self.background_tray_img, pos=(0, 0))
        print("Sprites loaded")
        # Create Draggable instances for the tray palette but do NOT add to groups.
        try:
            # positions inside the tray area (add more slots for letter sprites)
            tray_positions = [
                (40, 630), (230, 630), (420, 630), (610, 630),
                (40, 750), (230, 750), (610, 750), (420, 750),
                (800, 630), (920, 630), (1040, 630), (1160, 630)
            ]

            # start with the loaded gate images
            imgs = [
                self.and2_img, self.nand2_img, self.or2_img, self.nor2_img,
                self.xor2_img, self.xnor2_img, self.buffer_img, self.not1_img
            ]

            # input bit sprites (A, B, C)
            try:
                font = pg.font.Font(None, 36)
            except Exception:
                pg.font.init()
                font = pg.font.Font(None, 36)

            input_labels = ['A', 'B', 'C']
            for letter in input_labels:
                s = pg.Surface((94, 94), pg.SRCALPHA)
                s.fill(BLUE)
                txt = font.render(letter, True, WHITE)
                tr = txt.get_rect(center=(47, 47))
                s.blit(txt, tr)
                imgs.append(s)
            
            # Output bit sprite (OUT)
            try:
                out_font = pg.font.Font(None, 36)
            except Exception:
                pg.font.init()
                out_font = pg.font.Font(None, 36)
            s_out = pg.Surface((140, 94), pg.SRCALPHA)
            s_out.fill(BLUE)
            txt_out = out_font.render('OUT', True, WHITE)
            tr_out = txt_out.get_rect(center=(70, 47))
            s_out.blit(txt_out, tr_out)
            imgs.append(s_out)

            self.tray_sprites = []
            sprite_names = ['AND Gate', 'NAND Gate', 'OR Gate', 'NOR Gate',
                            'XOR Gate', 'XNOR Gate', 'Buffer', 'NOT Gate',
                            'Input A', 'Input B', 'Input C', 'Output']
            truth_tables = [self.and_table_img, self.nand_table_img, self.or_table_img, self.nor_table_img, 
                            self.xor_table_img, self.xnor_table_img, self.buf_table_img, self.not_table_img,
                            None, None, None, None]  # No truth tables for I/O blocks
            gate_types = ['AND', 'NAND', 'OR', 'NOR', 'XOR', 'XNOR', 'BUF', 'NOT']

            for idx, (pos, img) in enumerate(zip(tray_positions, imgs)):
                # Apply horizontal stretch and snap offset only to gates/buffer (indices 0-7)
                is_gate = (idx < 8)
                stretch = GATE_STRETCH_PX if is_gate else 0
                snap_off = (GATE_SNAP_OFFSET_X, GATE_SNAP_OFFSET_Y) if is_gate else (0, 0)
                dr = Draggable(img, pos=pos, scale=0.8, stretch_px=stretch, snap_offset=snap_off)

                # Cloning disabled - each gate can only be used once
                dr.is_cloneable = False
                dr.sprite_info = sprite_names[idx]
                dr.truth_table = truth_tables[idx] if idx < len(truth_tables) else None
                # Store original tray position for delete functionality
                dr.tray_position = pos

                # ---- LOGIC METADATA ----
                if idx < 8:
                    # gates
                    dr.node_type = 'gate'
                    dr.gate_type = gate_types[idx]
                    if idx < 6:  # two-input gates
                        dr.nodes = {
                            'input1': (0, int(dr.image.get_height() * 0.35)),
                            'input2': (0, int(dr.image.get_height() * 0.65)),
                            'output': (dr.image.get_width(), int(dr.image.get_height() * 0.5))
                        }
                    else:  # NOT and BUF
                        dr.nodes = {
                            'input1': (0, int(dr.image.get_height() * 0.5)),
                            'output': (dr.image.get_width(), int(dr.image.get_height() * 0.5))
                        }
                elif 8 <= idx <= 10:
                    # inputs A, B, C
                    dr.node_type = 'input'
                    dr.label = sprite_names[idx][-1]  # 'A','B','C'
                    dr.bit_value = 0
                    dr.nodes = {
                        'output_center': (int(dr.image.get_width() * 0.5), int(dr.image.get_height() * 0.5)),
                        'output_top': (int(dr.image.get_width() * 0.5), 0),
                        'output_bottom': (int(dr.image.get_width() * 0.5), dr.image.get_height()),
                        'output_left': (0, int(dr.image.get_height() * 0.5)),
                        'output_right': (dr.image.get_width(), int(dr.image.get_height() * 0.5))
                    }
                else:
                    # output block
                    dr.node_type = 'output'
                    dr.output_value = None
                    dr.nodes = {
                        'input_center': (int(dr.image.get_width() * 0.5), int(dr.image.get_height() * 0.5)),
                        'input_top': (int(dr.image.get_width() * 0.5), 0),
                        'input_bottom': (int(dr.image.get_width() * 0.5), dr.image.get_height()),
                        'input_left': (0, int(dr.image.get_height() * 0.5)),
                        'input_right': (dr.image.get_width(), int(dr.image.get_height() * 0.5))
                    }

                self.tray_sprites.append(dr)
        except Exception:
            self.tray_sprites = []
        
        # Safety check: ensure all tray sprites have correct gate_type
        # This fixes any clones that were created before the clone() method was fixed
        gate_types = ['AND', 'NAND', 'OR', 'NOR', 'XOR', 'XNOR', 'NOT', 'BUF']
        for sprite in self.tray_sprites:
            if hasattr(sprite, 'node_type') and sprite.node_type == 'gate':
                # Find which gate this should be based on sprite_info
                sprite_info = getattr(sprite, 'sprite_info', '')
                for idx, gate_name in enumerate(['AND Gate', 'NAND Gate', 'OR Gate', 'NOR Gate', 
                                                   'XOR Gate', 'XNOR Gate', 'NOT Gate', 'Buffer']):
                    if sprite_info == gate_name:
                        sprite.gate_type = gate_types[idx]
                        break

    def new(self):
        # starting a new game
        self.load_data()

        # sprite groups
        self.all_sprites = pg.sprite.Group()
        self.gates = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        self.tray_ui = pg.sprite.Group()
        self.wires = pg.sprite.Group()

        for plat in PLATFORM_LIST:
            p = Platform(*plat)
            self.all_sprites.add(p)
            self.platforms.add(p)
        
        if self.tray_open:
            self.tray_ui.add(self.tray_sprite)
            for dr in self.tray_sprites:
                self.all_sprites.add(dr)
                self.gates.add(dr)

        self.run()

    def draw_grid_overlay(self):
        if not SHOW_GRID:
            return
        try:
            gx, gy = GRID_ORIGIN
            try:
                gx = int(gx) + int(GRID_OFFSET_X)
            except Exception:
                gx = int(gx)
            try:
                gy = int(gy) + int(GRID_OFFSET_Y)
            except Exception:
                gy = int(gy)
            gs = int(GRID_SIZE)
            color = GRID_COLOR
            tx, ty, tw, th, border = TRAY_BOX
        except Exception:
            return
        
        try:
            pad = int(GRID_BORDER_PADDING)
        except Exception:
            pad = 0
        inset = border + pad
        box_left = tx + inset
        box_top = ty + inset
        box_right = tx + tw - inset
        box_bottom = ty + th - inset

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

        x = gx
        while x < box_right:
            if x >= box_left:
                pg.draw.line(self.screen, color, (x, box_top), (x, box_bottom), 1)
            x += gs

        y = gy
        while y < box_bottom:
            if y >= box_top:
                pg.draw.line(self.screen, color, (box_left, y), (box_right, y), 1)
            y += gs

    def draw(self):
        # background
        self.screen.blit(self.background_main_img, (0,0))
        try:
            self.tray_ui.draw(self.screen)
        except Exception:
            pass

        self.draw_grid_overlay()

        # draw sprites
        try:
            self.all_sprites.draw(self.screen)
            for sprite in self.all_sprites:
                if getattr(sprite, 'selected', False):
                    pg.draw.rect(self.screen, RED, sprite.rect, 3)
        except Exception:
            pass
        
        # draw wires
        try:
            for wire in self.wires:
                wire.draw(self.screen)
                if wire == self.selected_wire:
                    x1, y1 = wire.start_pos
                    x2, y2 = wire.end_pos
                    mid_point = (x2, y1)
                    pg.draw.line(self.screen, RED, (x1, y1), mid_point, wire.wire_width + 4)
                    pg.draw.line(self.screen, RED, mid_point, (x2, y2), wire.wire_width + 4)
            if self.current_wire:
                self.current_wire.draw(self.screen)
        except Exception:
            pass

        # buttons
        try:
            pg.draw.rect(self.screen, BLUE, self.tray_button_rect)
            self.draw_text("Blocks", 28, WHITE, self.tray_button_rect.centerx, self.tray_button_rect.centery - 18)

            pg.draw.rect(self.screen, RED, self.reset_button_rect)
            self.draw_text("Reset", 28, WHITE, self.reset_button_rect.centerx, self.reset_button_rect.centery - 18)

            pg.draw.rect(self.screen, (0, 200, 0), self.play_button_rect)
            self.draw_text("Play", 28, WHITE, self.play_button_rect.centerx, self.play_button_rect.centery - 18)

            pg.draw.rect(self.screen, (100, 200, 100), self.info_button_rect)
            self.draw_text("Info", 28, WHITE, self.info_button_rect.centerx, self.info_button_rect.centery - 18)

            pg.draw.rect(self.screen, (150, 100, 200), self.undo_button_rect)
            self.draw_text("Undo", 28, WHITE, self.undo_button_rect.centerx, self.undo_button_rect.centery - 18)
        except Exception:
            pass
        
        # wire button
        if self.tray_open:
            try:
                wire_color = (0, 200, 200) if self.wire_mode else (100, 180, 180)
                pg.draw.rect(self.screen, wire_color, self.wire_button_rect)
                self.draw_text("Wire", 28, WHITE, self.wire_button_rect.centerx, self.wire_button_rect.centery - 18)
            except Exception:
                pass

        # overlay input/output values (option C)
        self.draw_logic_overlays()

        if self.show_info and self.info_sprite:
            self.draw_info_box()
        
        pg.display.flip()

    def validate_circuit(self):
        """Check if circuit is fully connected. Returns (is_valid, error_message)."""
        try:
            # Check if there are any input and output blocks (exclude sprites still in tray)
            inputs = [s for s in self.all_sprites if getattr(s, 'node_type', None) == 'input' and s not in self.tray_sprites]
            outputs = [s for s in self.all_sprites if getattr(s, 'node_type', None) == 'output' and s not in self.tray_sprites]
            
            if not inputs:
                return False, "No input blocks found! Please add at least one input (A, B, or C) to the circuit."
            if not outputs:
                return False, "No output blocks found! Please add an output block to the circuit."
            
            # Check if output block is connected
            output_connected = False
            for sprite in outputs:
                if hasattr(sprite, 'nodes') and sprite.nodes:
                    for node_name in sprite.nodes.keys():
                        for wire in self.wires:
                            if wire.start_connection and wire.start_connection[0] == sprite:
                                output_connected = True
                                break
                            if wire.end_connection and wire.end_connection[0] == sprite:
                                output_connected = True
                                break
                        if output_connected:
                            break
                if output_connected:
                    break
            
            if not output_connected:
                return False, "Output block is not connected to the circuit!"
            
            # Check if inputs are connected (only for inputs actually placed in circuit)
            for sprite in inputs:
                input_connected = False
                if hasattr(sprite, 'nodes') and sprite.nodes:
                    for node_name in sprite.nodes.keys():
                        for wire in self.wires:
                            if wire.start_connection and wire.start_connection[0] == sprite:
                                input_connected = True
                                break
                            if wire.end_connection and wire.end_connection[0] == sprite:
                                input_connected = True
                                break
                        if input_connected:
                            break
                
                if not input_connected:
                    label = getattr(sprite, 'label', '?')
                    return False, f"Input {label} is not connected to the circuit!"
            
            return True, ""
        except Exception as e:
            print(f"Validation error: {e}")
            import traceback
            traceback.print_exc()
            return False, f"Validation error: {str(e)}"
    
    def evaluate_circuit(self, input_values):
        """Evaluate circuit for given input values dict {label: value}."""
        try:
            # Use the CircuitEvaluator class for proper gate dependency handling
            from logic_truth_tables import CircuitEvaluator
            
            print(f"Evaluating circuit with inputs: {input_values}")
            
            evaluator = CircuitEvaluator(self.all_sprites, self.tray_sprites, self.wires)
            result = evaluator.evaluate(input_values)
            
            print(f"Final output: {result}")
            if result is None:
                print("WARNING: Circuit returned None - check terminal output above for errors")
            return result
        except Exception as e:
            print(f"ERROR in evaluate_circuit: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_gate_inputs(self, gate_sprite):
        """Get input values for a gate sprite from connected wires."""
        try:
            inputs = []
            # Check input nodes
            if hasattr(gate_sprite, 'nodes'):
                input_nodes = [n for n in gate_sprite.nodes.keys() if 'input' in n.lower()]
                for node_name in sorted(input_nodes):  # Sort to ensure consistent order
                    value = self.get_node_value(gate_sprite, node_name)
                    if value is not None:
                        inputs.append(value)
            return inputs if inputs else None
        except Exception as e:
            print(f"Error getting gate inputs: {e}")
            return None
    
    def get_node_value(self, sprite, node_name):
        """Get the value at a specific node from connected wires."""
        try:
            # Find ALL wires connected to this node
            for wire in self.wires:
                # Check if this wire's end connects to our node
                if wire.end_connection and wire.end_connection == (sprite, node_name):
                    # Trace back through the wire's start
                    value = self.trace_from_connection(wire.start_connection, wire)
                    if value is not None:
                        return value
                # Check if this wire's start connects to our node  
                elif wire.start_connection and wire.start_connection == (sprite, node_name):
                    # Trace forward through the wire's end
                    value = self.trace_from_connection(wire.end_connection, wire)
                    if value is not None:
                        return value
                        
                # Check wire-to-wire connections at this wire
                for other_wire, intersection in wire.wire_connections:
                    # See if our sprite's node is near this intersection
                    if hasattr(sprite, 'nodes') and node_name in sprite.nodes:
                        node_x, node_y = sprite.nodes[node_name]
                        node_world_pos = (sprite.rect.x + node_x, sprite.rect.y + node_y)
                        ix, iy = intersection
                        # If node is near intersection, trace through connected wires
                        if abs(node_world_pos[0] - ix) < 15 and abs(node_world_pos[1] - iy) < 15:
                            value = self.trace_from_connection(wire.start_connection, wire)
                            if value is not None:
                                return value
                            value = self.trace_from_connection(other_wire.start_connection, other_wire)
                            if value is not None:
                                return value
            return None
        except Exception as e:
            print(f"Error getting node value: {e}")
            return None
    
    def trace_from_connection(self, connection, source_wire, visited=None):
        """Trace value from a wire connection point."""
        try:
            if visited is None:
                visited = set()
            if source_wire in visited:
                return None
            visited.add(source_wire)
            
            if not connection:
                return None
                
            sprite, node = connection
            node_type = getattr(sprite, 'node_type', None)
            
            # If it's an input block, return its value
            if node_type == 'input':
                value = getattr(sprite, 'bit_value', 0)
                return value
            
            # If it's a gate with an output value, return it (even if None for now)
            if hasattr(sprite, 'gate_type'):
                if 'output' in node.lower():
                    value = getattr(sprite, 'output_value', None)
                    return value
            
            # Otherwise, trace through wire-to-wire connections
            for other_wire, intersection in source_wire.wire_connections:
                if other_wire not in visited:
                    # Try start connection
                    value = self.trace_from_connection(other_wire.start_connection, other_wire, visited)
                    if value is not None:
                        return value
                    # Try end connection  
                    value = self.trace_from_connection(other_wire.end_connection, other_wire, visited)
                    if value is not None:
                        return value
                        
            return None
        except Exception as e:
            print(f"Error tracing connection: {e}")
            return None
    
    def propagate_gate_output(self, gate_sprite):
        """Propagate gate output to connected output blocks through wires."""
        try:
            output_value = getattr(gate_sprite, 'output_value', None)
            if output_value is None:
                return
            
            # Find all output blocks and check if they're connected to this gate
            for output_sprite in self.all_sprites:
                if getattr(output_sprite, 'node_type', None) == 'output':
                    # Check if this output block can trace back to our gate
                    if hasattr(output_sprite, 'nodes'):
                        for node_name in output_sprite.nodes.keys():
                            if 'input' in node_name.lower():
                                # Get the value at this output block's input node
                                value = self.get_node_value(output_sprite, node_name)
                                if value is not None:
                                    output_sprite.output_value = value
        except Exception as e:
            print(f"Error propagating output: {e}")
    
    def generate_truth_table(self):
        """Generate truth table for the circuit."""
        try:
            # Get input blocks (exclude those still in tray)
            inputs = [(s, getattr(s, 'label', '?')) for s in self.all_sprites 
                      if getattr(s, 'node_type', None) == 'input' and s not in self.tray_sprites]
            inputs.sort(key=lambda x: x[1])  # Sort by label
            input_labels = [label for sprite, label in inputs]
            
            if not input_labels:
                return None, "No input blocks found in the circuit!"
            
            # Generate all combinations
            from itertools import product
            table = []
            for bits in product([0, 1], repeat=len(input_labels)):
                input_dict = {input_labels[i]: bits[i] for i in range(len(input_labels))}
                output = self.evaluate_circuit(input_dict)
                table.append((input_dict, output if output is not None else '?'))
            
            return (input_labels, table), None
        except Exception as e:
            return None, f"Error generating truth table: {e}"
    
    def show_truth_table_popup(self, input_labels, table):
        """Display truth table in a pygame popup overlay."""
        try:
            print(f"Showing truth table with {len(input_labels)} inputs and {len(table)} rows")
            
            # Create a semi-transparent overlay
            overlay = pg.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            
            # Create table box
            box_width = min(800, (len(input_labels) + 1) * 120 + 100)
            box_height = min(700, len(table) * 40 + 200)
            box_x = (WIDTH - box_width) // 2
            box_y = (HEIGHT - box_height) // 2
            
            scroll_offset = 0
            max_scroll = max(0, len(table) * 40 - (box_height - 200))
            
            # Capture current screen as background (freeze frame)
            background = self.screen.copy()
            
            showing_table = True
            while showing_table:
                # Handle events - consume ALL events to prevent background processing
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        showing_table = False
                        self.playing = False
                        self.running = False
                    elif event.type == pg.KEYDOWN:
                        if event.key == pg.K_ESCAPE:
                            showing_table = False
                        elif event.key == pg.K_UP:
                            scroll_offset = max(0, scroll_offset - 40)
                        elif event.key == pg.K_DOWN:
                            scroll_offset = min(max_scroll, scroll_offset + 40)
                    elif event.type == pg.MOUSEWHEEL:
                        scroll_offset = max(0, min(max_scroll, scroll_offset - event.y * 40))
                    elif event.type == pg.MOUSEBUTTONDOWN:
                        mouse_pos = event.pos
                        # Check if Close button clicked
                        close_button = pg.Rect(box_x + box_width//2 - 60, box_y + box_height - 60, 120, 40)
                        if close_button.collidepoint(mouse_pos):
                            showing_table = False
                        # Consume all other clicks to prevent background interaction
                
                # Redraw from frozen background
                self.screen.blit(background, (0, 0))
                
                # Draw overlay
                self.screen.blit(overlay, (0, 0))
                
                # Draw table box
                box_rect = pg.Rect(box_x, box_y, box_width, box_height)
                pg.draw.rect(self.screen, WHITE, box_rect)
                pg.draw.rect(self.screen, BLUE, box_rect, 5)
                
                # Draw title
                title_font = pg.font.Font(None, 48)
                title_surf = title_font.render("Truth Table", True, BLUE)
                title_rect = title_surf.get_rect(center=(box_x + box_width//2, box_y + 40))
                self.screen.blit(title_surf, title_rect)
                
                # Create clipping area for table content
                content_rect = pg.Rect(box_x + 20, box_y + 80, box_width - 40, box_height - 160)
                clip_surface = pg.Surface((content_rect.width, content_rect.height))
                clip_surface.fill(WHITE)
                
                # Draw headers
                header_font = pg.font.Font(None, 32)
                col_width = (content_rect.width - 20) // (len(input_labels) + 1)
                header_y = 10
                
                for i, label in enumerate(input_labels):
                    header_surf = header_font.render(label, True, BLACK)
                    header_x = i * col_width + col_width // 2
                    header_rect = header_surf.get_rect(center=(header_x, header_y))
                    clip_surface.blit(header_surf, header_rect)
                
                output_surf = header_font.render("OUT", True, BLACK)
                output_x = len(input_labels) * col_width + col_width // 2
                output_rect = output_surf.get_rect(center=(output_x, header_y))
                clip_surface.blit(output_surf, output_rect)
                
                # Draw separator line
                pg.draw.line(clip_surface, BLACK, (10, 40), (content_rect.width - 10, 40), 2)
                
                # Draw table rows
                row_font = pg.font.Font(None, 28)
                row_y = 50 - scroll_offset
                
                for input_dict, output in table:
                    if row_y > -30 and row_y < content_rect.height:
                        # Draw input values
                        for i, label in enumerate(input_labels):
                            value = str(input_dict[label])
                            value_surf = row_font.render(value, True, BLACK)
                            value_x = i * col_width + col_width // 2
                            value_rect = value_surf.get_rect(center=(value_x, row_y))
                            clip_surface.blit(value_surf, value_rect)
                        
                        # Draw output value
                        output_surf = row_font.render(str(output), True, BLACK)
                        output_x = len(input_labels) * col_width + col_width // 2
                        output_rect = output_surf.get_rect(center=(output_x, row_y))
                        clip_surface.blit(output_surf, output_rect)
                    
                    row_y += 35
                
                # Blit clipped content
                self.screen.blit(clip_surface, (content_rect.x, content_rect.y))
                
                # Draw scroll indicator if needed
                if max_scroll > 0:
                    scroll_text = f"Scroll: {scroll_offset}/{max_scroll}"
                    scroll_font = pg.font.Font(None, 20)
                    scroll_surf = scroll_font.render(scroll_text, True, BLACK)
                    self.screen.blit(scroll_surf, (box_x + box_width - 150, box_y + box_height - 90))
                
                # Draw Close button
                close_button = pg.Rect(box_x + box_width//2 - 60, box_y + box_height - 60, 120, 40)
                pg.draw.rect(self.screen, GREEN, close_button)
                pg.draw.rect(self.screen, BLACK, close_button, 2)
                close_font = pg.font.Font(None, 32)
                close_surf = close_font.render("Close", True, WHITE)
                close_rect = close_surf.get_rect(center=close_button.center)
                self.screen.blit(close_surf, close_rect)
                
                pg.display.flip()
                self.clock.tick(30)
                
            print("Truth table closed")
        except Exception as e:
            print(f"Error showing truth table: {e}")
            import traceback
            traceback.print_exc()
    
    def show_error_message(self, message):
        """Display error message popup using pygame."""
        try:
            # Create a semi-transparent overlay
            overlay = pg.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            
            # Create message box
            box_width = 600
            box_height = 250
            box_x = (WIDTH - box_width) // 2
            box_y = (HEIGHT - box_height) // 2
            
            # Capture current screen as background (freeze frame)
            background = self.screen.copy()
            
            # Draw the popup
            showing_error = True
            while showing_error:
                # Handle events - consume ALL events to prevent background processing
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        showing_error = False
                        self.playing = False
                        self.running = False
                    elif event.type == pg.KEYDOWN:
                        if event.key == pg.K_ESCAPE or event.key == pg.K_RETURN:
                            showing_error = False
                    elif event.type == pg.MOUSEBUTTONDOWN:
                        mouse_pos = event.pos
                        # Check if OK button clicked
                        ok_button = pg.Rect(box_x + box_width//2 - 50, box_y + box_height - 60, 100, 40)
                        if ok_button.collidepoint(mouse_pos):
                            showing_error = False
                        # Consume all other clicks to prevent background interaction
                
                # Redraw from frozen background
                self.screen.blit(background, (0, 0))
                
                # Draw overlay
                self.screen.blit(overlay, (0, 0))
                
                # Draw message box
                box_rect = pg.Rect(box_x, box_y, box_width, box_height)
                pg.draw.rect(self.screen, WHITE, box_rect)
                pg.draw.rect(self.screen, RED, box_rect, 5)
                
                # Draw title
                title_font = pg.font.Font(None, 42)
                title_surf = title_font.render("Error", True, RED)
                title_rect = title_surf.get_rect(center=(box_x + box_width//2, box_y + 40))
                self.screen.blit(title_surf, title_rect)
                
                # Draw message (word wrap)
                message_font = pg.font.Font(None, 28)
                words = message.split(' ')
                lines = []
                current_line = ""
                
                for word in words:
                    test_line = current_line + word + " "
                    if message_font.size(test_line)[0] < box_width - 40:
                        current_line = test_line
                    else:
                        if current_line:
                            lines.append(current_line)
                        current_line = word + " "
                if current_line:
                    lines.append(current_line)
                
                y_offset = box_y + 90
                for line in lines:
                    msg_surf = message_font.render(line.strip(), True, BLACK)
                    msg_rect = msg_surf.get_rect(center=(box_x + box_width//2, y_offset))
                    self.screen.blit(msg_surf, msg_rect)
                    y_offset += 35
                
                # Draw OK button
                ok_button = pg.Rect(box_x + box_width//2 - 50, box_y + box_height - 60, 100, 40)
                pg.draw.rect(self.screen, BLUE, ok_button)
                pg.draw.rect(self.screen, BLACK, ok_button, 2)
                ok_font = pg.font.Font(None, 32)
                ok_surf = ok_font.render("OK", True, WHITE)
                ok_rect = ok_surf.get_rect(center=ok_button.center)
                self.screen.blit(ok_surf, ok_rect)
                
                pg.display.flip()
                self.clock.tick(30)
                
        except Exception as e:
            print(f"Error showing message: {e}")
            import traceback
            traceback.print_exc()
            print(f"Message was: {message}")
    
    def draw_logic_overlays(self):
        """Draw value indicators on input and output blocks."""
        for sprite in self.all_sprites:
            node_type = getattr(sprite, 'node_type', None)
            if node_type == 'input':
                bit = int(getattr(sprite, 'bit_value', 0))
                color = GREEN if bit == 1 else RED
                cx, cy = sprite.rect.center
                # Draw circle below the letter
                pg.draw.circle(self.screen, color, (cx, cy + 25), 8)
            elif node_type == 'output':
                val = getattr(sprite, 'output_value', None)
                if val is None:
                    color = LIGHT_GRAY
                else:
                    v = int(val)
                    color = GREEN if v == 1 else RED
                cx, cy = sprite.rect.center
                # Draw circle below "OUT" text
                pg.draw.circle(self.screen, color, (cx, cy + 25), 8)

    def run(self):
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def draw_text(self, text, size, color, x, y):
        font_name = pg.font.match_font('arial')
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x,y)
        self.screen.blit(text_surface, text_rect)

    def draw_info_box(self):
        """Draw gate truth table or simple text info."""
        try:
            tx, ty, tw, th, border = TRAY_BOX
            pad = int(GRID_BORDER_PADDING)
            inset = border + pad
            truth_table = getattr(self.info_sprite, 'truth_table', None)
            
            if truth_table:
                table_width = truth_table.get_width()
                table_height = truth_table.get_height()
                box_width = min(table_width + 20, 400)
                box_height = min(table_height + 60, 300)
                if table_width > box_width - 20 or table_height > box_height - 60:
                    scale_factor = min((box_width - 20) / table_width, (box_height - 60) / table_height)
                    scaled_width = int(table_width * scale_factor)
                    scaled_height = int(table_height * scale_factor)
                    scaled_table = pg.transform.smoothscale(truth_table, (scaled_width, scaled_height))
                else:
                    scaled_table = truth_table
                    scaled_width = table_width
                    scaled_height = table_height
                
                box_x = tx + tw - inset - box_width - 20
                box_y = ty + inset + 20
                
                info_rect = pg.Rect(box_x, box_y, box_width, box_height)
                pg.draw.rect(self.screen, WHITE, info_rect)
                pg.draw.rect(self.screen, BLUE, info_rect, 3)
                
                sprite_name = getattr(self.info_sprite, 'sprite_info', 'Gate')
                font = pg.font.Font(None, 28)
                title_surface = font.render(sprite_name, True, BLACK)
                self.screen.blit(title_surface, (box_x + 10, box_y + 10))
                
                img_x = box_x + (box_width - scaled_width) // 2
                img_y = box_y + 45
                self.screen.blit(scaled_table, (img_x, img_y))
            else:
                box_width = 300
                box_height = 200
                box_x = tx + tw - inset - box_width - 20
                box_y = ty + inset + 20
                
                info_rect = pg.Rect(box_x, box_y, box_width, box_height)
                pg.draw.rect(self.screen, WHITE, info_rect)
                pg.draw.rect(self.screen, BLUE, info_rect, 3)
                
                info_text = getattr(self.info_sprite, 'sprite_info', 'No information available.')
                font = pg.font.Font(None, 24)
                y_offset = box_y + 15
                text_surface = font.render(info_text, True, BLACK)
                self.screen.blit(text_surface, (box_x + 10, y_offset))
        except Exception:
            pass

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False

            # LEFT CLICK
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos

                # tray open/close
                if self.tray_button_rect.collidepoint(mouse_pos):
                    self.tray_open = not self.tray_open
                    if self.tray_open:
                        for sprite in self.tray_sprites:
                            if sprite not in self.all_sprites:
                                self.all_sprites.add(sprite)
                            if sprite not in self.gates:
                                self.gates.add(sprite)
                        if self.tray_sprite not in self.tray_ui:
                            self.tray_ui.add(self.tray_sprite)
                    else:
                        for sprite in self.tray_sprites:
                            try:
                                dp = getattr(sprite, 'default_pos', None)
                                if dp is None:
                                    continue
                                sp = int(getattr(sprite, 'stretch_px', 0))
                                expected = (int(dp[0]) - (max(0, sp) // 2), int(dp[1]))
                                if sprite.rect.topleft == expected:
                                    if sprite in self.all_sprites:
                                        self.all_sprites.remove(sprite)
                                    if sprite in self.gates:
                                        self.gates.remove(sprite)
                            except Exception:
                                pass
                        if self.tray_sprite in self.tray_ui:
                            self.tray_ui.remove(self.tray_sprite)
                    continue

                # reset
                if self.reset_button_rect.collidepoint(mouse_pos):
                    try:
                        reset_state = []
                        for sprite in self.tray_sprites:
                            reset_state.append({
                                'sprite': sprite,
                                'old_pos': sprite.rect.topleft,
                                'was_in_all': sprite in self.all_sprites,
                                'was_in_gates': sprite in self.gates,
                                'selected': sprite.selected if hasattr(sprite, 'selected') else False,
                                'dragging': sprite.dragging if hasattr(sprite, 'dragging') else False,
                                'moved_from_default': sprite.moved_from_default if hasattr(sprite, 'moved_from_default') else False,
                                'snap_enabled': sprite.snap_enabled if hasattr(sprite, 'snap_enabled') else False
                            })
                        
                        # Save all wires for reset undo
                        saved_wires = list(self.wires)
                        
                        self.undo_stack.append({
                            'type': 'reset',
                            'tray_open': self.tray_open,
                            'sprites_state': reset_state,
                            'wires': saved_wires
                        })
                    except Exception:
                        pass
                    
                    # Reset sprite positions
                    self.reset_tray_positions()
                    
                    # Clear all wires
                    try:
                        self.wires.empty()
                        self.selected_wire = None
                        self.current_wire = None
                    except Exception:
                        pass
                    
                    if not self.tray_open:
                        for sprite in list(self.tray_sprites):
                            try:
                                if sprite in self.all_sprites:
                                    self.all_sprites.remove(sprite)
                                if sprite in self.gates:
                                    self.gates.remove(sprite)
                            except Exception:
                                pass
                        try:
                            if self.selected_sprite and self.selected_sprite in self.tray_sprites:
                                self.selected_sprite = None
                        except Exception:
                            pass
                    continue

                # info
                if self.info_button_rect.collidepoint(mouse_pos):
                    if self.selected_sprite:
                        if self.show_info and self.info_sprite == self.selected_sprite:
                            self.show_info = False
                            self.info_sprite = None
                        else:
                            self.show_info = True
                            self.info_sprite = self.selected_sprite
                    else:
                        self.show_info = False
                        self.info_sprite = None
                    continue

                # undo
                if self.undo_button_rect.collidepoint(mouse_pos):
                    self.undo_last_action()
                    continue
                
                # Play button - generate and show truth table
                if self.play_button_rect.collidepoint(mouse_pos):
                    print(f"\n{'='*50}")
                    print("PLAY BUTTON CLICKED!")
                    print(f"{'='*50}")
                    print("Generating truth table...")
                    
                    try:
                        # Debug: Check all sprites
                        print(f"\nTotal sprites in all_sprites: {len(self.all_sprites)}")
                    except Exception as e:
                        print(f"Error getting all_sprites length: {e}")
                    
                    try:
                        print(f"Total sprites in tray_sprites: {len(self.tray_sprites)}")
                    except Exception as e:
                        print(f"Error getting tray_sprites length: {e}")
                    
                    try:
                        for sprite in self.all_sprites:
                            node_type = getattr(sprite, 'node_type', None)
                            label = getattr(sprite, 'label', '?')
                            in_tray = sprite in self.tray_sprites
                            print(f"  Sprite: node_type={node_type}, label={label}, in_tray={in_tray}")
                    except Exception as e:
                        print(f"Error iterating sprites: {e}")
                        import traceback
                        traceback.print_exc()
                    
                    try:
                        # Get inputs that are in circuit (not in tray)
                        circuit_inputs = [s for s in self.all_sprites 
                                        if getattr(s, 'node_type', None) == 'input' 
                                        and s not in self.tray_sprites]
                        print(f"\nFound {len(circuit_inputs)} inputs in circuit")
                        for inp in circuit_inputs:
                            print(f"  - Input {getattr(inp, 'label', '?')}")
                        
                        result, error = self.generate_truth_table()
                        print(f"\nTruth table result: {result is not None}, error: {error}")
                        
                        if error:
                            print(f"ERROR: {error}")
                            self.show_error_message(error)
                        elif result:
                            try:
                                input_labels, table = result
                                print(f"Success! Truth table has {len(input_labels)} inputs and {len(table)} rows")
                                print(f"Input labels: {input_labels}")
                                print("Displaying truth table popup...")
                                self.show_truth_table_popup(input_labels, table)
                                print("Truth table popup closed")
                            except (TypeError, ValueError) as e:
                                print(f"ERROR unpacking truth table result: {e}")
                                self.show_error_message(f"Error displaying truth table: {e}")
                        else:
                            print("No result returned from generate_truth_table")
                            self.show_error_message("Failed to generate truth table")
                    except Exception as e:
                        print(f"EXCEPTION in play button handler: {e}")
                        import traceback
                        traceback.print_exc()
                    print(f"{'='*50}\n")
                    continue

                # wire mode toggle
                if self.tray_open and self.wire_button_rect.collidepoint(mouse_pos):
                    self.wire_mode = not self.wire_mode
                    if not self.wire_mode and self.current_wire:
                        self.current_wire = None
                    continue

                # wire drawing
                if self.wire_mode:
                    snapped_pos = self.snap_position_to_grid(mouse_pos)
                    self.current_wire = Wire(snapped_pos, snapped_pos)
                    continue

                # select wire (when NOT in wire mode)
                if not self.wire_mode:
                    clicked_wire = None
                    for wire in self.wires:
                        if self.is_point_near_wire(mouse_pos, wire):
                            clicked_wire = wire
                            break
                    if clicked_wire:
                        self.selected_wire = clicked_wire
                        if self.selected_sprite:
                            self.selected_sprite.deselect()
                            self.selected_sprite = None
                        continue
                    else:
                        self.selected_wire = None

                # select sprites - check all_sprites to include both tray and grid sprites
                clicked_sprite = None
                for sprite in reversed(list(self.all_sprites)):
                    if sprite.rect.collidepoint(mouse_pos):
                        clicked_sprite = sprite
                        break

                if clicked_sprite:
                    if self.selected_sprite and self.selected_sprite != clicked_sprite:
                        self.selected_sprite.deselect()
                    self.selected_sprite = clicked_sprite
                    self.selected_wire = None
                    try:
                        self.selected_sprite._drag_start_pos = self.selected_sprite.rect.topleft
                    except Exception:
                        pass
                    self.selected_sprite.select(mouse_pos)
                else:
                    if self.selected_sprite:
                        self.selected_sprite.deselect()
                        self.selected_sprite = None

            # RIGHT CLICK -> toggle input bits
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 3:
                mouse_pos = event.pos
                # find topmost input sprite under mouse
                for sprite in reversed(self.tray_sprites):
                    if sprite.rect.collidepoint(mouse_pos) and getattr(sprite, 'node_type', None) == 'input':
                        current = int(getattr(sprite, 'bit_value', 0))
                        sprite.bit_value = 0 if current else 1
                        break

            # LEFT BUTTON UP
            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if self.wire_mode and self.current_wire:
                    self.current_wire.finalize()
                    self.detect_wire_connections(self.current_wire)
                    self.wires.add(self.current_wire)
                    try:
                        self.undo_stack.append({
                            'type': 'wire',
                            'wire': self.current_wire
                        })
                    except Exception:
                        pass
                    self.current_wire = None
                    continue
                
                if self.selected_sprite:
                    try:
                        if hasattr(self.selected_sprite, '_drag_start_pos'):
                            old_pos = self.selected_sprite._drag_start_pos
                            new_pos = self.selected_sprite.rect.topleft
                            if old_pos != new_pos:
                                # Remove sprite from tray_sprites if it's been moved away from the tray
                                try:
                                    if hasattr(self.selected_sprite, 'in_tray') and not self.selected_sprite.in_tray:
                                        if self.selected_sprite in self.tray_sprites:
                                            self.tray_sprites.remove(self.selected_sprite)
                                except Exception:
                                    pass
                                
                                # Revalidate all wire connections and detect new ones
                                self.revalidate_all_wire_connections()
                                self.detect_sprite_to_wire_connections(self.selected_sprite)
                                self.undo_stack.append({
                                    'type': 'move',
                                    'sprite': self.selected_sprite,
                                    'old_pos': old_pos,
                                    'new_pos': new_pos
                                })
                            delattr(self.selected_sprite, '_drag_start_pos')
                    except Exception:
                        pass
                    self.selected_sprite.dragging = False
                    
                    try:
                        if self.selected_sprite in self.pending_clones:
                            self.pending_clones.remove(self.selected_sprite)
                    except Exception:
                        pass

            # MOUSE MOVE
            elif event.type == pg.MOUSEMOTION:
                if self.wire_mode and self.current_wire:
                    snapped_pos = self.snap_position_to_grid(event.pos)
                    self.current_wire.update_end(snapped_pos)
                    continue
                
                if self.selected_sprite and getattr(self.selected_sprite, 'selected', False):
                    left_down = False
                    try:
                        left_down = bool(getattr(event, 'buttons', (0,0,0))[0])
                    except Exception:
                        pass
                    if not left_down:
                        try:
                            left_down = pg.mouse.get_pressed()[0]
                        except Exception:
                            left_down = False

                    if left_down:
                        if not getattr(self.selected_sprite, 'dragging', False):
                            try:
                                px, py = getattr(self.selected_sprite, 'press_pos', event.pos)
                                cx, cy = event.pos
                                if abs(cx - px) >= 8 or abs(cy - py) >= 8:
                                    self.selected_sprite.dragging = True
                            except Exception:
                                pass
                        if getattr(self.selected_sprite, 'dragging', False) and hasattr(self.selected_sprite, 'move'):
                            self.selected_sprite.move(event.pos)

    def update(self):
        self.all_sprites.update()

        # handle cloning
        if self.tray_open:
            try:
                for sprite in list(self.tray_sprites):
                    if not getattr(sprite, 'dragging', False):
                        continue
                    if not getattr(sprite, 'is_cloneable', False):
                        continue
                    try:
                        default_y = int(sprite.default_pos[1])
                    except Exception:
                        default_y = sprite.rect.y
                    moved_up_enough = sprite.rect.y < (default_y - 40)
                    # Cloning disabled - each sprite is unique and can only be used once
                    # if moved_up_enough and sprite not in self.pending_clones:
                    #     self.pending_clones.append(sprite)
                    #     clone = sprite.clone()
                    #     if clone:
                    #         clone.is_cloneable = True
                    #         self.tray_sprites.append(clone)
                    #         if self.tray_open:
                    #             self.all_sprites.add(clone)
                    #             self.gates.add(clone)
            except Exception:
                pass

        # evaluate logic network every frame
        self.evaluate_circuit_old()

    # --------- UNDO / RESET / GRID HELPERS (unchanged logic, plus wire cases) ---------

    def undo_last_action(self):
        if not self.undo_stack:
            return
        
        action = self.undo_stack.pop()
        
        try:
            if action['type'] == 'move':
                sprite = action['sprite']
                sprite.rect.topleft = action['old_pos']
                try:
                    sp = int(getattr(sprite, 'stretch_px', 0))
                    expected = (int(sprite.default_pos[0]) - (max(0, sp) // 2), int(sprite.default_pos[1]))
                    sprite.moved_from_default = (sprite.rect.topleft != expected)
                    sprite.in_tray = (sprite.rect.topleft == expected)
                    
                    # Add sprite back to tray_sprites if it's back in tray position
                    if sprite.in_tray and sprite not in self.tray_sprites:
                        self.tray_sprites.append(sprite)
                    # Remove from tray_sprites if it's moved out
                    elif not sprite.in_tray and sprite in self.tray_sprites:
                        self.tray_sprites.remove(sprite)
                except Exception:
                    pass
                
                # Clear selection state to prevent blocking button clicks
                if hasattr(sprite, 'selected'):
                    sprite.selected = False
                if hasattr(sprite, 'dragging'):
                    sprite.dragging = False
            
            elif action['type'] == 'delete':
                sprite = action['sprite']
                if action['was_in_all'] and sprite not in self.all_sprites:
                    self.all_sprites.add(sprite)
                if action['was_in_gates'] and sprite not in self.gates:
                    self.gates.add(sprite)
                if action['was_in_tray'] and sprite not in self.tray_sprites:
                    self.tray_sprites.append(sprite)
                    # Update in_tray attribute when restoring to tray
                    if hasattr(sprite, 'in_tray'):
                        sprite.in_tray = True
                
                # Don't restore selection - clear sprite reference to prevent blocking
                self.selected_sprite = None
                if hasattr(sprite, 'selected'):
                    sprite.selected = False
                if hasattr(sprite, 'dragging'):
                    sprite.dragging = False
            
            elif action['type'] == 'reset':
                # Restore sprite states
                for sprite_state in action['sprites_state']:
                    sprite = sprite_state['sprite']
                    sprite.rect.topleft = sprite_state['old_pos']
                    if sprite_state['was_in_all'] and sprite not in self.all_sprites:
                        self.all_sprites.add(sprite)
                    elif not sprite_state['was_in_all'] and sprite in self.all_sprites:
                        self.all_sprites.remove(sprite)
                    
                    if sprite_state['was_in_gates'] and sprite not in self.gates:
                        self.gates.add(sprite)
                    elif not sprite_state['was_in_gates'] and sprite in self.gates:
                        self.gates.remove(sprite)
                    
                    # Restore sprite state but force selection off to prevent button blocking
                    if hasattr(sprite, 'selected'):
                        sprite.selected = False  # Always clear selection
                    if hasattr(sprite, 'dragging'):
                        sprite.dragging = False  # Always clear dragging
                    if hasattr(sprite, 'moved_from_default'):
                        sprite.moved_from_default = sprite_state['moved_from_default']
                    if hasattr(sprite, 'snap_enabled'):
                        sprite.snap_enabled = sprite_state['snap_enabled']
                    if hasattr(sprite, 'in_tray'):
                        sprite.in_tray = sprite_state.get('in_tray', True)
                
                # Clear selected sprite reference
                self.selected_sprite = None
                
                # Restore wires
                try:
                    saved_wires = action.get('wires', [])
                    self.wires.empty()
                    for wire in saved_wires:
                        self.wires.add(wire)
                except Exception:
                    pass
            
            elif action['type'] == 'wire':
                wire = action['wire']
                if wire in self.wires:
                    self.wires.remove(wire)
            
            elif action['type'] == 'wire_delete':
                wire = action['wire']
                if wire not in self.wires:
                    self.wires.add(wire)
                    try:
                        saved_connections = action.get('wire_connections', [])
                        for other_wire, intersection in saved_connections:
                            if other_wire in self.wires:
                                if (wire, intersection) not in other_wire.wire_connections:
                                    other_wire.wire_connections.append((wire, intersection))
                    except Exception:
                        pass
        
        except Exception:
            pass

    def revalidate_all_wire_connections(self):
        """Remove invalid wire connections when sprites have moved."""
        try:
            for wire in self.wires:
                # Check start connection
                if wire.start_connection:
                    sprite, node_name = wire.start_connection
                    node_name_check, node_pos = sprite.get_closest_node(wire.start_pos)
                    if node_name_check != node_name:
                        wire.start_connection = None
                
                # Check end connection
                if wire.end_connection:
                    sprite, node_name = wire.end_connection
                    node_name_check, node_pos = sprite.get_closest_node(wire.end_pos)
                    if node_name_check != node_name:
                        wire.end_connection = None
        except Exception:
            pass
    
    def detect_sprite_to_wire_connections(self, sprite):
        """Detect if a moved sprite's nodes connect to existing wires."""
        try:
            if not hasattr(sprite, 'nodes'):
                return
            
            for node_name, (node_x, node_y) in sprite.nodes.items():
                node_world_pos = (sprite.rect.x + node_x, sprite.rect.y + node_y)
                
                # Check each wire to see if this node connects
                for wire in self.wires:
                    # Check if node is near wire start
                    if not wire.start_connection:
                        node_name_check, node_pos = sprite.get_closest_node(wire.start_pos)
                        if node_name_check == node_name:
                            wire.start_connection = (sprite, node_name)
                    
                    # Check if node is near wire end
                    if not wire.end_connection:
                        node_name_check, node_pos = sprite.get_closest_node(wire.end_pos)
                        if node_name_check == node_name:
                            wire.end_connection = (sprite, node_name)
        except Exception:
            pass

    def detect_wire_connections(self, wire):
        try:
            # sprite connections at start
            for sprite in self.all_sprites:
                node_name, node_pos = sprite.get_closest_node(wire.start_pos)
                if node_name:
                    wire.start_connection = (sprite, node_name)
                    break
            # sprite connections at end
            for sprite in self.all_sprites:
                node_name, node_pos = sprite.get_closest_node(wire.end_pos)
                if node_name:
                    wire.end_connection = (sprite, node_name)
                    break
            # wire-to-wire connections
            for other_wire in self.wires:
                if other_wire != wire and not other_wire.is_preview:
                    intersection = wire.get_intersection_point(other_wire)
                    if intersection:
                        wire.wire_connections.append((other_wire, intersection))
                        other_wire.wire_connections.append((wire, intersection))
        except Exception:
            pass
    
    def get_connections(self, sprite, node_name=None):
        connections = []
        try:
            for wire in self.wires:
                if wire.start_connection and wire.start_connection[0] == sprite:
                    conn_node = wire.start_connection[1]
                    if node_name is None or conn_node == node_name:
                        connections.append((wire, conn_node, 'start'))
                if wire.end_connection and wire.end_connection[0] == sprite:
                    conn_node = wire.end_connection[1]
                    if node_name is None or conn_node == node_name:
                        connections.append((wire, conn_node, 'end'))
        except Exception:
            pass
        return connections
    
    def get_connected_wires(self, wire, visited=None):
        if visited is None:
            visited = set()
        if wire in visited:
            return visited
        visited.add(wire)
        try:
            for other_wire, intersection in wire.wire_connections:
                if other_wire not in visited:
                    self.get_connected_wires(other_wire, visited)
        except Exception:
            pass
        return visited

    def is_point_near_wire(self, point, wire, threshold=10):
        try:
            px, py = point
            x1, y1 = wire.start_pos
            x2, y2 = wire.end_pos
            mid_x, mid_y = x2, y1
            
            min_x, max_x = min(x1, mid_x), max(x1, mid_x)
            if min_x - threshold <= px <= max_x + threshold:
                if abs(py - y1) <= threshold:
                    return True
            
            min_y, max_y = min(mid_y, y2), max(mid_y, y2)
            if min_y - threshold <= py <= max_y + threshold:
                if abs(px - x2) <= threshold:
                    return True
            
            return False
        except Exception:
            return False

    def snap_position_to_grid(self, pos):
        try:
            gx, gy = GRID_ORIGIN
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
            
            x, y = pos
            snapped_x = gx + round((x - gx) / gs) * gs
            snapped_y = gy + round((y - gy) / gs) * gs
            return (int(snapped_x), int(snapped_y))
        except Exception:
            return pos

    def reset_tray_positions(self):
        if not hasattr(self, 'all_sprites') or not self.all_sprites:
            return
        for sprite in self.all_sprites:
            try:
                dp = getattr(sprite, 'default_pos', None)
                if dp is None:
                    continue
                sp = int(getattr(sprite, 'stretch_px', 0))
                expected = (int(dp[0]) - (max(0, sp) // 2), int(dp[1]))
                if sprite.rect.topleft != expected:
                    sprite.rect.topleft = expected
                sprite.selected = False
                if hasattr(sprite, 'dragging'):
                    sprite.dragging = False
                if hasattr(sprite, 'moved_from_default'):
                    sprite.moved_from_default = False
                if hasattr(sprite, 'snap_enabled'):
                    sprite.snap_enabled = False
                if hasattr(sprite, 'in_tray'):
                    sprite.in_tray = True
                # Reset input blocks to 0 (red circle)
                if getattr(sprite, 'node_type', None) == 'input':
                    sprite.bit_value = 0
                # Reset output blocks to None (gray circle)
                if getattr(sprite, 'node_type', None) == 'output':
                    sprite.output_value = None
                # Add sprite back to tray_sprites if it's not already there
                if sprite not in self.tray_sprites:
                    self.tray_sprites.append(sprite)
            except Exception:
                pass

    def get_mouse_now(self):
        x,y = pg.mouse.get_pos()
        return (x,y)

    # --------- LOGIC EVALUATION ---------

    def evaluate_circuit_old(self):
        """Compute logic values on all nets and update output block(s). [DEPRECATED - old method]"""
        # 1) Build nets (clusters of wires connected together)
        wire_to_net = {}
        nets = []  # each is dict: {'wires': set, 'drivers': [], 'sinks': []}
        node_to_net = {}

        visited_wires = set()
        for wire in self.wires:
            if wire in visited_wires:
                continue
            cluster = self.get_connected_wires(wire, visited=set())
            visited_wires |= cluster
            net_index = len(nets)
            for w in cluster:
                wire_to_net[w] = net_index

            drivers = []
            sinks = []
            for w in cluster:
                for conn in (w.start_connection, w.end_connection):
                    if not conn:
                        continue
                    sprite, node_name = conn
                    key = (sprite, node_name)
                    node_to_net[key] = net_index
                    node_type = getattr(sprite, 'node_type', None)
                    # classify driver vs sink
                    if node_type == 'input' and node_name.startswith('output'):
                        drivers.append((sprite, node_name))
                    elif node_type == 'gate' and node_name.startswith('output'):
                        drivers.append((sprite, node_name))
                    else:
                        sinks.append((sprite, node_name))
            nets.append({'wires': cluster, 'drivers': drivers, 'sinks': sinks})

        # 2) Initialize net values
        net_values = {i: None for i in range(len(nets))}

        # 3) Iteratively propagate logic (simple fixed point)
        MAX_ITERS = 10
        for _ in range(MAX_ITERS):
            changed = False

            # Inputs drive nets
            for sprite in self.tray_sprites:
                if getattr(sprite, 'node_type', None) != 'input':
                    continue
                bit = int(getattr(sprite, 'bit_value', 0))
                for node_name in getattr(sprite, 'nodes', {}).keys():
                    if not node_name.startswith('output'):
                        continue
                    key = (sprite, node_name)
                    if key in node_to_net:
                        nid = node_to_net[key]
                        if net_values[nid] is None:
                            net_values[nid] = bit
                            changed = True

            # Gates read input nets and drive output nets
            for sprite in self.tray_sprites:
                if getattr(sprite, 'node_type', None) != 'gate':
                    continue
                gate_type = getattr(sprite, 'gate_type', None)
                if not gate_type:
                    continue
                nodes = getattr(sprite, 'nodes', {})
                in1_val = None
                in2_val = None

                if 'input1' in nodes:
                    key = (sprite, 'input1')
                    if key in node_to_net:
                        in1_val = net_values[node_to_net[key]]
                if 'input2' in nodes:
                    key = (sprite, 'input2')
                    if key in node_to_net:
                        in2_val = net_values[node_to_net[key]]

                # Only evaluate when needed inputs are known
                if gate_type in ('NOT', 'BUF'):
                    if in1_val is None:
                        continue
                    try:
                        out_val = create_gate(gate_type, in1_val)
                    except Exception:
                        out_val = in1_val
                else:
                    if in1_val is None or in2_val is None:
                        continue
                    try:
                        out_val = create_gate(gate_type, in1_val, in2_val)
                    except Exception:
                        # fallback local truth
                        if gate_type == 'AND':
                            out_val = int(in1_val and in2_val)
                        elif gate_type == 'OR':
                            out_val = int(in1_val or in2_val)
                        elif gate_type == 'NAND':
                            out_val = int(not (in1_val and in2_val))
                        elif gate_type == 'NOR':
                            out_val = int(not (in1_val or in2_val))
                        elif gate_type == 'XOR':
                            out_val = int(in1_val ^ in2_val)
                        elif gate_type == 'XNOR':
                            out_val = int(not (in1_val ^ in2_val))
                        else:
                            out_val = 0

                # drive output net
                key = (sprite, 'output')
                if key in node_to_net:
                    nid = node_to_net[key]
                    if net_values[nid] is None:
                        net_values[nid] = int(out_val)
                        changed = True

            if not changed:
                break

        # 4) Update output block(s)
        for sprite in self.tray_sprites:
            if getattr(sprite, 'node_type', None) != 'output':
                continue
            val = None
            for node_name in getattr(sprite, 'nodes', {}).keys():
                if not node_name.startswith('input'):
                    continue
                key = (sprite, node_name)
                if key in node_to_net:
                    nid = node_to_net[key]
                    v = net_values.get(nid, None)
                    if v is None:
                        continue
                    if val is None:
                        val = v
                    else:
                        # if multiple inputs, treat as OR for display
                        val = int(val or v)
            sprite.output_value = val

if __name__ == "__main__":
    # instantiates game class
    g = Game()

    # kick off the game loop (run once)
    g.new()

    pg.quit()
