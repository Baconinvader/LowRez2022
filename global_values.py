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
GFX_DIR = os.path.join(RES_DIR, "gfx")
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
player = None

#input
keys = {}
mx = 0
my = 0
ml, mm, mr = False, False, False
tmx, tmy = 0,0

#graphics
spritesheets = {}
image_cache = {}
reverse_image_cache = {}
mask_cache = {}
fonts = {}

#sounds
sound_dict = {}
channel_list = None