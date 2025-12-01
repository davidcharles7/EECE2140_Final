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
        # delete button placed next to the reset button
        self.delete_button_rect = pg.Rect(self.reset_button_rect.right - 245, self.reset_button_rect.top, self.reset_button_rect.width, self.reset_button_rect.height)
        # info button placed next to delete button
        self.info_button_rect = pg.Rect(self.delete_button_rect.right -245, self.delete_button_rect.top, self.delete_button_rect.width, self.delete_button_rect.height)
        # undo button placed next to info button
        self.undo_button_rect = pg.Rect(self.info_button_rect.right - 245, self.info_button_rect.top, self.info_button_rect.width, self.info_button_rect.height)
        # info display state
        self.show_info = False
        self.info_sprite = None
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
                (800, 630), (920, 630), (1040, 630), (1160, 630)
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
                s = pg.Surface((94, 94), pg.SRCALPHA)
                s.fill(BLUE)
                txt = font.render(letter, True, WHITE)
                tr = txt.get_rect(center=(47, 47))
                s.blit(txt, tr)
                imgs.append(s)
            
            

            # Output bit sprites
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

            # create Draggable instances for all images, but do NOT add to sprite groups yet
            self.tray_sprites = []
            sprite_names = ['AND Gate', 'NAND Gate', 'OR Gate', 'NOR Gate', 'XOR Gate', 'XNOR Gate', 'NOT Gate', 'Buffer', 'Input A', 'Input B', 'Input C', 'Output']
            for idx, (pos, img) in enumerate(zip(tray_positions, imgs)):
                # Apply horizontal stretch and snap offset only to gates/buffer (indices 0-7)
                is_gate = (idx < 8)
                stretch = GATE_STRETCH_PX if is_gate else 0
                snap_off = (GATE_SNAP_OFFSET_X, GATE_SNAP_OFFSET_Y) if is_gate else (0, 0)
                dr = Draggable(img, pos=pos, scale=0.8, stretch_px=stretch, snap_offset=snap_off)
                # Mark whether this sprite should be cloned when dragged out
                # Gates and buffer (indices 0-7) can be cloned; letter blocks (8-11) cannot
                dr.is_cloneable = (idx < 8)
                # Add info text placeholder
                dr.sprite_info = f"{sprite_names[idx]}\n\n[Placeholder description for {sprite_names[idx]}]\n\nAdd detailed information here."
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
            # apply global grid offset so drawn grid matches snapping
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
        # buttons
        try:
            pg.draw.rect(self.screen, BLUE, self.tray_button_rect)
            self.draw_text("Blocks", 28, WHITE, self.tray_button_rect.centerx, self.tray_button_rect.centery - 18)
            # draw reset button to the right of the blocks button
            pg.draw.rect(self.screen, RED, self.reset_button_rect)
            self.draw_text("Reset", 28, WHITE, self.reset_button_rect.centerx, self.reset_button_rect.centery - 18)
            # draw delete button
            pg.draw.rect(self.screen, (255, 100, 0), self.delete_button_rect)  # Orange color
            self.draw_text("Delete", 28, WHITE, self.delete_button_rect.centerx, self.delete_button_rect.centery - 18)
            # draw info button
            pg.draw.rect(self.screen, (100, 200, 100), self.info_button_rect)  # Green color
            self.draw_text("Info", 28, WHITE, self.info_button_rect.centerx, self.info_button_rect.centery - 18)
            # draw undo button
            pg.draw.rect(self.screen, (150, 100, 200), self.undo_button_rect)  # Purple color
            self.draw_text("Undo", 28, WHITE, self.undo_button_rect.centerx, self.undo_button_rect.centery - 18)
        except Exception:
            pass
        
        # Draw info box if info is being shown
        if self.show_info and self.info_sprite:
            self.draw_info_box()
        
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

    def draw_info_box(self):
        """Draw information box in top-right corner of grid area."""
        try:
            # Get grid bounds
            tx, ty, tw, th, border = TRAY_BOX
            pad = int(GRID_BORDER_PADDING)
            inset = border + pad
            
            # Info box dimensions and position (top-right corner of grid)
            box_width = 300
            box_height = 200
            box_x = tx + tw - inset - box_width - 20
            box_y = ty + inset + 20
            
            # Draw white background with blue outline
            info_rect = pg.Rect(box_x, box_y, box_width, box_height)
            pg.draw.rect(self.screen, WHITE, info_rect)
            pg.draw.rect(self.screen, BLUE, info_rect, 3)
            
            # Get info text from sprite
            info_text = getattr(self.info_sprite, 'sprite_info', 'No information available.')
            
            # Draw text (split by newlines for multi-line display)
            font = pg.font.Font(None, 24)
            y_offset = box_y + 15
            line_height = 25
            
            for line in info_text.split('\n'):
                if y_offset + line_height > box_y + box_height - 10:
                    break  # Don't draw beyond box bounds
                text_surface = font.render(line, True, BLACK)
                self.screen.blit(text_surface, (box_x + 10, y_offset))
                y_offset += line_height
                
        except Exception:
            pass

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
                        # Remove only sprites at default position (compare rect.topleft accounting for stretch)
                        for sprite in self.tray_sprites:
                            try:
                                dp = getattr(sprite, 'default_pos', None)
                                if dp is None:
                                    continue
                                sp = int(getattr(sprite, 'stretch_px', 0))
                                expected = (int(dp[0]) - (max(0, sp) // 2), int(dp[1]))
                                if sprite.rect.topleft == expected:
                                    self.all_sprites.remove(sprite)
                                    self.gates.remove(sprite)
                            except Exception:
                                pass
                    continue

                if self.reset_button_rect.collidepoint(mouse_pos):
                    # Save all sprite positions before reset
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
                        self.undo_stack.append({
                            'type': 'reset',
                            'tray_open': self.tray_open,
                            'sprites_state': reset_state
                        })
                    except Exception:
                        pass
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

                # check if delete button was clicked
                if self.delete_button_rect.collidepoint(mouse_pos):
                    # Delete the selected sprite if it's cloneable (not A,B,C,OUT)
                    if self.selected_sprite and getattr(self.selected_sprite, 'is_cloneable', True):
                        try:
                            # Save delete action to undo stack
                            was_in_all = self.selected_sprite in self.all_sprites
                            was_in_gates = self.selected_sprite in self.gates
                            was_in_tray = self.selected_sprite in self.tray_sprites
                            self.undo_stack.append({
                                'type': 'delete',
                                'sprite': self.selected_sprite,
                                'was_in_all': was_in_all,
                                'was_in_gates': was_in_gates,
                                'was_in_tray': was_in_tray,
                                'was_selected': True
                            })
                            # Remove from all groups
                            if was_in_all:
                                self.all_sprites.remove(self.selected_sprite)
                            if was_in_gates:
                                self.gates.remove(self.selected_sprite)
                            # Remove from tray_sprites if present
                            if was_in_tray:
                                self.tray_sprites.remove(self.selected_sprite)
                            # Clear selection
                            self.selected_sprite = None
                        except Exception:
                            pass
                    continue

                # check if info button was clicked
                if self.info_button_rect.collidepoint(mouse_pos):
                    # Toggle info display if a sprite is selected
                    if self.selected_sprite:
                        if self.show_info and self.info_sprite == self.selected_sprite:
                            # Hide info if clicking info again for same sprite
                            self.show_info = False
                            self.info_sprite = None
                        else:
                            # Show info for selected sprite
                            self.show_info = True
                            self.info_sprite = self.selected_sprite
                    else:
                        # Hide info if no sprite selected
                        self.show_info = False
                        self.info_sprite = None
                    continue

                # check if undo button was clicked
                if self.undo_button_rect.collidepoint(mouse_pos):
                    self.undo_last_action()
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
                    # Store starting position BEFORE selecting (before any potential snap)
                    try:
                        self.selected_sprite._drag_start_pos = self.selected_sprite.rect.topleft
                    except Exception:
                        pass
                    self.selected_sprite.select(mouse_pos)
                else:
                    # Clicked empty space: deselect any selected sprite
                    if self.selected_sprite:
                        self.selected_sprite.deselect()
                        self.selected_sprite = None

            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if self.selected_sprite:
                    # Save move action to undo stack if sprite moved
                    try:
                        if hasattr(self.selected_sprite, '_drag_start_pos'):
                            old_pos = self.selected_sprite._drag_start_pos
                            new_pos = self.selected_sprite.rect.topleft
                            if old_pos != new_pos:
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
                    # Clear pending clone tracking when sprite is released
                    try:
                        if self.selected_sprite in self.pending_clones:
                            self.pending_clones.remove(self.selected_sprite)
                    except Exception:
                        pass

            elif event.type == pg.MOUSEMOTION:
                # Apply a small drag threshold so clicks don't move sprites
                if self.selected_sprite and getattr(self.selected_sprite, 'selected', False):
                    # determine if left button is down
                    left_down = False
                    try:
                        # pygame 2.x provides event.buttons
                        left_down = bool(getattr(event, 'buttons', (0,0,0))[0])
                    except Exception:
                        pass
                    if not left_down:
                        # fallback to global mouse state
                        try:
                            left_down = pg.mouse.get_pressed()[0]
                        except Exception:
                            left_down = False

                    if left_down:
                        # if not yet dragging, check threshold from press_pos
                        if not getattr(self.selected_sprite, 'dragging', False):
                            try:
                                px, py = getattr(self.selected_sprite, 'press_pos', event.pos)
                                cx, cy = event.pos
                                if abs(cx - px) >= 8 or abs(cy - py) >= 8:
                                    self.selected_sprite.dragging = True
                            except Exception:
                                pass
                        # move only when dragging is active
                        if getattr(self.selected_sprite, 'dragging', False) and hasattr(self.selected_sprite, 'move'):
                            self.selected_sprite.move(event.pos)

    def update(self):
        self.all_sprites.update()
        
        # Clone tray items only after a meaningful upward move from their default tray position
        # This prevents accidental cloning on simple clicks inside the tray.
        if self.tray_open:
            try:
                for sprite in list(self.tray_sprites):
                    if not getattr(sprite, 'dragging', False):
                        continue
                    if not getattr(sprite, 'is_cloneable', False):
                        continue
                    # Require an upward movement of at least 40 pixels from the sprite's default tray Y
                    try:
                        default_y = int(sprite.default_pos[1])
                    except Exception:
                        default_y = sprite.rect.y
                    moved_up_enough = sprite.rect.y < (default_y - 40)
                    if moved_up_enough and sprite not in self.pending_clones:
                        self.pending_clones.append(sprite)
                        clone = sprite.clone()
                        if clone:
                            clone.is_cloneable = True
                            self.tray_sprites.append(clone)
                            if self.tray_open:
                                self.all_sprites.add(clone)
                                self.gates.add(clone)
            except Exception:
                pass

    def undo_last_action(self):
        """Undo the last move, delete, or reset action."""
        if not self.undo_stack:
            return
        
        action = self.undo_stack.pop()
        
        try:
            if action['type'] == 'move':
                # Restore sprite to old position
                sprite = action['sprite']
                sprite.rect.topleft = action['old_pos']
                # Update moved_from_default flag
                try:
                    sp = int(getattr(sprite, 'stretch_px', 0))
                    expected = (int(sprite.default_pos[0]) - (max(0, sp) // 2), int(sprite.default_pos[1]))
                    sprite.moved_from_default = (sprite.rect.topleft != expected)
                    sprite.in_tray = (sprite.rect.topleft == expected)
                except Exception:
                    pass
            
            elif action['type'] == 'delete':
                # Restore deleted sprite
                sprite = action['sprite']
                if action['was_in_all'] and sprite not in self.all_sprites:
                    self.all_sprites.add(sprite)
                if action['was_in_gates'] and sprite not in self.gates:
                    self.gates.add(sprite)
                if action['was_in_tray'] and sprite not in self.tray_sprites:
                    self.tray_sprites.append(sprite)
                if action.get('was_selected'):
                    self.selected_sprite = sprite
            
            elif action['type'] == 'reset':
                # Restore all sprite states before reset
                for sprite_state in action['sprites_state']:
                    sprite = sprite_state['sprite']
                    sprite.rect.topleft = sprite_state['old_pos']
                    
                    # Restore group membership
                    if sprite_state['was_in_all'] and sprite not in self.all_sprites:
                        self.all_sprites.add(sprite)
                    elif not sprite_state['was_in_all'] and sprite in self.all_sprites:
                        self.all_sprites.remove(sprite)
                    
                    if sprite_state['was_in_gates'] and sprite not in self.gates:
                        self.gates.add(sprite)
                    elif not sprite_state['was_in_gates'] and sprite in self.gates:
                        self.gates.remove(sprite)
                    
                    # Restore sprite flags
                    if hasattr(sprite, 'selected'):
                        sprite.selected = sprite_state['selected']
                    if hasattr(sprite, 'dragging'):
                        sprite.dragging = sprite_state['dragging']
                    if hasattr(sprite, 'moved_from_default'):
                        sprite.moved_from_default = sprite_state['moved_from_default']
                    if hasattr(sprite, 'snap_enabled'):
                        sprite.snap_enabled = sprite_state['snap_enabled']
        
        except Exception as e:
            # If undo fails, skip silently
            pass

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
                # if sprite not at default, move it back (account for horizontal stretch)
                sp = int(getattr(sprite, 'stretch_px', 0))
                expected = (int(dp[0]) - (max(0, sp) // 2), int(dp[1]))
                if sprite.rect.topleft != expected:
                    sprite.rect.topleft = expected
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