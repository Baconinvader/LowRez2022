import os
import pygame as p


#obviously
WIDTH = 64
HEIGHT = 64
FPS = 60
screen_rect = p.Rect(0,0,WIDTH,HEIGHT)

#display
screen = None
SCREEN_WIDTH = 64*8
SCREEN_HEIGHT = 64*8
CAPTION = "Invasion of Planet Bacon"
full_screen = None

#res
RES_DIR = "res"
LEVELS_DIR = os.path.join(RES_DIR, "levels")
GFX_DIRS = (os.path.join(RES_DIR, "gfx_new"), os.path.join(RES_DIR, "gfx"))
FONTS_DIR = os.path.join(RES_DIR, "fonts")
SOUNDS_DIR = os.path.join(RES_DIR, "sounds")

#time
game_clock = None
dt = 0

#obj
elements = {}
element_list = []
levels = {}
pipes = {}
pipe_list = []
element_id_number = 0
global_pipe = None
current_level = None
active_states = set()
power_diverted = False
player = None

#input
keys = {}
mx = 0
my = 0
ml, mm, mr = False, False, False
tmx, tmy = 0,0

#debug stuff
# enable "dev mode" commands if there's a gitignore file~
IS_DEV = os.path.exists(".gitignore")
if IS_DEV:
    print("IS_DEV is enabled.")

#graphics
spritesheets = {}
image_cache = {}
reverse_image_cache = {}
mask_cache = {}
fonts = {}

# respect the palette >:(
colour_remaps = {
    # primary colours
    "white": (233, 239, 236),
    "beige": (160, 160, 139),
    "darkslategrey": (85, 85, 104),
    "black": (33, 30, 32),

    # blood
    "red": (128, 51, 30),
    "darkred": (78, 39, 28),

    # accent colours
    "green": (80, 217, 80),
    "yellow": (255, 216, 0),
    "darkyellow": (202, 179, 48)
}
colour_remaps["gray"] = colour_remaps["white"]

_logged_bad_colours = set()


def convert_colour(colour):
    """Converts a colour to its palette version, if possible"""
    if colour in colour_remaps:
        return colour_remaps[colour]
    else:
        if colour not in _logged_bad_colours:
            _logged_bad_colours.add(colour)
            print(f"WARN: non-palette friendly color is being used?!: {colour}")
        return colour


#sounds
sound_dict = {}
channel_list = None