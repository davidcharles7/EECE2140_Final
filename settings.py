# EECE 2140 Final Project - Settings
# Written by David Charles

#Settings 
WIDTH = 1540
HEIGHT = 880
FPS = 60 

#States
RUNNING = True
PAUSED = False


#Colors
BLACK = (0,0,0)
WHITE = (255,255,255)
BLUE = (0,158,219)
RED = (255, 50, 50)
GREEN = (140,200,120)
GRAY = (60,60,60)


#Platforms
PLATFORM_LIST = []

# Grid snapping settings: origin (x,y) and grid spacing in pixels.
# Adjust these to match the background grid lines.
GRID_ORIGIN = (12, 110)
GRID_SIZE = 19

# Grid visualization: set SHOW_GRID = True to overlay a debug grid on the screen.
# This helps align GRID_ORIGIN and GRID_SIZE with your background grid.
SHOW_GRID = True
GRID_COLOR = (200, 200, 200)  # light gray for visibility

# Tray box: white background with blue outline (x, y, width, height, outline thickness)
# Adjust these to match the entire white rectangle in your background image
# Expanded slightly to give more room
TRAY_BOX = (7, 105, 1525, 763, 3)  # (x, y, width, height, border_width)

# Additional padding to keep grid lines away from the tray border (in pixels)
# Grid will be drawn only inside TRAY_BOX inset by (border + GRID_BORDER_PADDING)
GRID_BORDER_PADDING = 2
# How many pixels to shrink the grid from the bottom when the tray is open
GRID_TRAY_SHRINK = 400
# Additional extension (positive moves the grid down) when tray is open
# Increase extension so the grid extends a bit further when the tray is open.
# User requested "a little more - maybe 50 pixels"; add 50 to the previous 90.
GRID_TRAY_EXTENSION = 120

# Horizontal stretch for gate sprites (in pixels). Stretched image shifts left by half this amount.
GATE_STRETCH_PX = 8

# Global grid offset (pixels) applied to both drawing and snapping
# Negative X shifts grid lines left visually and for snapping
GRID_OFFSET_X = 0
GRID_OFFSET_Y = 0

# Extra per-gate snap offset so gate edges align with grid (usually 0 when GRID_OFFSET_X is used)
GATE_SNAP_OFFSET_X = 7
GATE_SNAP_OFFSET_Y = 0