# EECE 2140 Final Project - Settings
# Written by David Charles

# screen settings 
WIDTH = 1540
HEIGHT = 880
FPS = 60 

# game states
RUNNING = True
PAUSED = False


# colors
BLACK = (0,0,0)
WHITE = (255,255,255)
BLUE = (0,158,219)
RED = (255, 50, 50)
GREEN = (140,200,120)
GRAY = (60,60,60)
LIGHT_GRAY = (200,200,200)


# platforms (leftover from game engine)
PLATFORM_LIST = []

# grid settings
GRID_ORIGIN = (12, 110)
GRID_SIZE = 19
SHOW_GRID = True
GRID_COLOR = LIGHT_GRAY
GRID_BORDER_PADDING = 2
GRID_OFFSET_X = 0
GRID_OFFSET_Y = 0

# block tray settings
TRAY_BOX = (7, 105, 1525, 763, 3)  # (x, y, width, height, border_width)
GRID_TRAY_SHRINK = 400
GRID_TRAY_EXTENSION = 120

# made a stretch factor for gates b/c pngs I used were slightly too small
GATE_STRETCH_PX = 8

# grid snapping adjustment to account for sprite size difference 
GATE_SNAP_OFFSET_X = 7
GATE_SNAP_OFFSET_Y = 0