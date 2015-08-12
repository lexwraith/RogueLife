from libtcodpy import Color
#############################
# Configuration Variables
#############################
#actual size of the window (tiles are 8 x 8 pixels)
#800 x 600 = 100,75
#1024 x 768 = 128,96
#1366 x 768 = 171, 96
SCREEN_WIDTH = 120
SCREEN_HEIGHT = 90

#actual size of map
MAP_WIDTH = SCREEN_WIDTH
MAP_HEIGHT = SCREEN_HEIGHT - 30 #room for sidebar

LIMIT_FPS = 30

ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30

FOV_ALGO = 0
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 5

MAX_ROOM_MONSTERS = 2


############################
# Aesthetics
############################

color_dark_wall = Color(0, 0, 100)
color_dark_ground = Color(50, 50, 150)
color_light_wall = Color(0, 0, 100)
color_light_ground = Color(200, 180, 50)

