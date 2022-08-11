import pygame as p
import math
import os

import global_values as g

class Spritesheet:
    """
    Class for sheets filled with surfaces
    """
    def __init__(self, name, sx, sy):
        self.name = name
        self.surface = load_image(self.name)
        self.sx = sx
        self.sy = sy

        self.anims = []
        self.masks = []
        for y in range( int(self.surface.get_height()//sy) ):
            self.anims.append([])
            self.masks.append([])
            for x in range( int(self.surface.get_width()//sx) ):
                new_surface = p.Surface((self.sx, self.sy), p.SRCALPHA)
                new_surface.blit(self.surface, (0,0), (x*self.sx, y*self.sy, self.sx, self.sy))
                self.anims[-1].append(new_surface)
                
                new_mask = p.mask.from_surface(new_surface)
                self.masks[-1].append(new_mask)

                cache_name = f"{self.name}_{x}_{y}"

                g.image_cache[cache_name] = new_surface
                g.reverse_image_cache[new_surface] = SurfacePickle(new_surface, cache_name)

        print(self.name,":",int(self.surface.get_width()//sx), int(self.surface.get_height()//sy))

        g.spritesheets[self.name] = self

    def create_animation(self, index, timer, ping_pong=False, global_time=True, repeat=True, reverse=False):
        """
        Create animation from specific index
        """
        anim = Animation(self.anims[index], timer, ping_pong=ping_pong, global_time=global_time, repeat=repeat, reverse=reverse)
        return anim

    def create_animation_system(self, anim_index_dict, timer, ping_pong=False, global_time=True, repeat=True, reverse=False):
        """
        Create animation system from specific index
        """
        anim_dict = {}
        for name, index in anim_index_dict.items():
            anim = Animation(self.anims[index], timer, ping_pong=ping_pong, global_time=global_time, repeat=repeat, reverse=reverse)
            anim_dict[name] = anim

        anim_system = AnimationSystem(anim_dict)

        return anim_system

class Animation:
    """
    Class for holding and showing a collection of sprites over time
    """
    def __init__(self, frames, timer, ping_pong=False, global_time=True, repeat=True, reverse=False):
        self.frames = frames
        self.max_timer = timer
        self.ping_pong = ping_pong
        self.global_time = global_time
        self.repeat = repeat
        self.reverse = reverse

        if not self.repeat:
            self.global_time = False

        self.active = True

        if not global_time:
            self.start_update_time = p.time.get_ticks()

    def reset(self):
        self.start_update_time = p.time.get_ticks()

    def get_frame(self):
        """
        Get the current displayed frame
        """
        if self.ping_pong:
            frame_count = (len(self.frames)*2)-1
        else:
            frame_count = len(self.frames)

        if self.global_time:
            frame_index = ((p.time.get_ticks()/1000)/self.max_timer) % frame_count
        else:
            new_update_time = p.time.get_ticks()
            diff = (new_update_time-self.start_update_time)/1000
            frame_index = (diff/self.max_timer) % frame_count

            if not self.repeat:
                if diff/self.max_timer >= frame_count:
                    if self.ping_pong:
                        frame_index = 0
                    else:
                        frame_index = -1
            

        old_frame_index = frame_index
        if self.ping_pong and frame_index >= len(self.frames):
            if frame_index == len(self.frames):
                frame_index = len(self.frames)-0.001
            else:
                frame_index = len(self.frames)-(frame_index - len(self.frames))

        if self.reverse:
            if frame_index == -1:
                frame_index = 0
            else:
                print(len(self.frames)-int(frame_index+1), ": ", len(self.frames), frame_index)
                frame_index = len(self.frames)-int(frame_index+1)

        #print(old_frame_index, frame_index,"[",len(self.frames),"]")
        return self.frames[int(frame_index)]

    def __getstate__(self):
        print("ANIMATION")
        return pickle_state(self.__dict__)

    def __setstate__(self, state):
        self.__dict__ = unpickle_state(state)

class AnimationSystem:
    """
    Class for playing multiple animations
    """
    def __init__(self, anim_dict):
        self.anim_dict = anim_dict
        for key in self.anim_dict.keys():
            self.playing_anim_name = key
            break
        
        self.playing_anim = self.anim_dict[self.playing_anim_name]

    def set_anim(self, name):
        #reset new anim
        if name != self.playing_anim_name:
            if not self.playing_anim.global_time:
                self.playing_anim.start_update_time = p.time.get_ticks()

        self.playing_anim_name = name
        self.playing_anim = self.anim_dict[self.playing_anim_name]

        #reset anim
        if not self.playing_anim.global_time:
            self.playing_anim.start_update_time = p.time.get_ticks()


    def get_frame(self):
        return self.playing_anim.get_frame()

    def __getstate__(self):
        print("ANIMATION SYSTEM")
        return pickle_state(self.__dict__)

    def __setstate__(self, state):
        self.__dict__ = unpickle_state(state)


def load_image(name, path=g.GFX_DIRS, extension=".png", alpha=True):
    """
    Load image, or take from cache if possible
    """
    if not g.image_cache.get(name, None):
        if not isinstance(path, tuple):
            path = (path,)
        for path_to_try in path:
            filepath = os.path.join(path_to_try, name + extension)
            if os.path.exists(filepath):
                image = p.image.load(filepath)
                if alpha:
                    image = image.convert_alpha()
                else:
                    image = image.convert()

                g.image_cache[name] = image
                g.reverse_image_cache[image] = SurfacePickle(image, name)
                break
        if name not in g.image_cache:
            raise ValueError(f"failed to find image: {name}")

    return g.image_cache[name]


def get_surface(gfx):
    """
    Get the drawable surface from a number of graphical sources
    """
    if type(gfx) == str:
        return load_image(gfx)

    if type(gfx) == p.Surface:
        return gfx

    if isinstance(gfx, (Animation, AnimationSystem)):
        return gfx.get_frame()

    if type(gfx) == list or type(gfx) == tuple:
        return g.spritesheets[gfx[0]].anims[gfx[1]][gfx[2]]

    print("warning, cannot find: ",gfx)
    return None

def get_surface_hash(surface):
    """
    Hash a surface
    """
    surf_hash = hash(surface) + hash(surface.get_width() *0.331 + surface.get_height() * 0.12321)
    return surf_hash

class SurfacePickle():
    def __init__(self, surf, name):
        self.name = name
        self.hash = get_surface_hash(surf)

def get_surface_pickle(surface):
    return g.reverse_image_cache[surface]

def pickle_state(_state_dict):
    """
    Pickle obj state, converting surfaces as required
    """
    state_dict = _state_dict.copy()

    #make pickle work
    for k,v in state_dict.items():
        
        if type(v) == p.Surface:
            surf_pickle = get_surface_pickle(v)
            state_dict[k] = surf_pickle
            #print("conv to [",surf_pickle,"]")

        elif type(v) == list:
            list_pickle = []
            for i,vv in enumerate(v):
                if type(vv) == p.Surface:
                    surf_pickle = get_surface_pickle(vv)
                    #print("conv",i,"to",surf_pickle)
                    list_pickle.append(surf_pickle)
                else:
                    list_pickle.append(vv)
            state_dict[k] = list_pickle

        #print(">:",k,state_dict[k],"",_state_dict[k])

    return state_dict
        
def unpickle_state(_state_dict):
    """
    Unpickle obj state, converting surface names as required
    """
    state_dict = _state_dict.copy()
    #return state_dict

    for k,v in state_dict.items():
        if type(v) == SurfacePickle:
            try:
                surf = g.image_cache[v.hash]
            except:
                surf = g.image_cache[v.name]

            state_dict[k] = surf

        elif type(v) == list:
            list_unpickle = []
            for i,vv in enumerate(v):
                if type(vv) == SurfacePickle:
                    try:
                        surf = g.image_cache[vv.hash]
                    except:
                        surf = g.image_cache[vv.name]
                    #print("conv",i,"to",surf_pickle)
                    list_unpickle.append(surf)
                else:
                    list_unpickle.append(vv)
            state_dict[k] = list_unpickle

    #print( ">>",len(state_dict.values()), state_dict)
    return state_dict


def get_mask(gfx):
    """
    Get the mask from some surface, or create it if it doesn't exist
    """
    surf = get_surface(gfx)
    surf_hash = get_surface_hash(surf)
    res = g.mask_cache.get(surf_hash, None)
    if res:
        return res
    else:
        #create new
        mask = p.mask.from_surface(surf)
        g.mask_cache[surf_hash] = mask
        print("new mask: ",type(gfx),"- ",surf.get_width(),",",surf.get_height(), mask.count())
        return mask

def draw_text(font_name, string, pos, cx=False, cy=False, colour="black", alpha=255):
    """
    Draw some text
    """
    font = g.fonts[font_name]
    
    health_text = font.render(string, False, colour)

    w,h = font.size(string)
    x = pos[0]
    y = pos[1]
    if cx:
        x -= w/2
    if cy:
        y -= h/2

    if alpha != 255:
        health_text.set_alpha(alpha)

    g.screen.blit(health_text, (x, y))

def draw_wrapped_text(font_name, string, rect, colour="black", alpha=255):
    words = string.split(" ")
    font = g.fonts[font_name]
    x = rect.x
    y = rect.y
    line = ""
    for word in words:
        w,h = font.size(line+" "+word)
        if w > rect.w:
            #draw line
            if y+h > rect.y:
                draw_text(font_name, line, (x,y), colour=colour, alpha=alpha)

            line = word
            x = rect.x
            y += h
            #if y > rect.bottom:
            #    return
        else:
            line += " "+word

    if line:
        draw_text(font_name, line, (x,y), colour=colour, alpha=alpha)

