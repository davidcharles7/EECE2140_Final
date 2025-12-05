# logic_truth_table.py
# ---------------------
# generates truth tables for the user's built circuit.
# Opens a pygame popup window to display the full truth table.

import pygame as pg
from itertools import product


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


# ===================================================================
#   For testing! (COMMENT THIS OUT ONCE IMPLEMENTED)
# ===================================================================

# if __name__ == "__main__":
#     # Example fake circuit evaluator
#     def fake_circuit(bits):
#         return bits["A"] ^ bits["B"]

#     tbl = generate_circuit_truth_table(["A", "B"], fake_circuit)
#     show_truth_table(tbl)


# ===================================================================
#   TO BE IMPLEMENTED IN THE MAIN CODE!
# ===================================================================

from logic_truth_table import generate_circuit_truth_table, show_truth_table

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
