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
LEVEL_PLACEHOLDERS_DIR = os.path.join(RES_DIR, "levels", "placeholders")
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
start_slides_shown = False
player = None
end_screen = None
inv_button = None

#input
keys = {}
mx = 0
my = 0
ml, mm, mr = False, False, False
tmx, tmy = 0,0
player_targeting = False

#debug stuff
# enable "dev mode" commands if there's a gitignore file~
IS_DEV = os.path.exists(".gitignore")
if IS_DEV and False:
    print("IS_DEV is enabled.")
NO_ATTACK = True  # makes enemies not attack

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
    "lightyellow": (255, 216, 0),
    "lightblue": (80, 211, 217),
    "blue": (80, 82, 217),
    "yellow": (202, 179, 48)
}
colour_remaps["gray"] = colour_remaps["white"]
colour_remaps["brown"] = colour_remaps["darkred"]
for cname in list(colour_remaps.keys()):
    colour_remaps[p.color.Color(cname)[0:3]] = colour_remaps[cname]

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