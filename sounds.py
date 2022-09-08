import global_values as g
import utilities as util

import pygame as p
import os

class ChannelList():
    """
    Class for list of channels
    """
    def __init__(self, channel_amount=16):
        self.channel_list = [None for _ in range(channel_amount)]
        

        self.sound_playing_list = [None for _ in range(channel_amount)]
        #p.mixer.set_num_channels(channel_amount)
        #for i in range(channel_amount):
        #    channel = p.mixer.Channel(i)
        #    self.channel_list.append(channel)
        self.next_available_channel = 0

    def play(self, sound):
        #channel = self.channel_list[self.next_available_channel]

        self.sound_playing_list[self.next_available_channel] = sound
        if type(sound) == GameSound:
            sound = sound.sound
        elif type(sound) == p.mixer.Sound:
            sound.set_volume(1)


        #channel.play(sound)
        sound.play()
        check_count = 1

        self.next_available_channel = (self.next_available_channel + 1) % len(self.channel_list)
        #while check_count < len(self.channel_list) and self.channel_list[self.next_available_channel].get_busy():
        #    check_count += 1
        #    self.next_available_channel = (self.next_available_channel + 1) % len(self.channel_list)

    def update(self):
        #change sound volume based on distance
        for i, channel in enumerate(self.channel_list):
            if True:
                sound = self.sound_playing_list[i]

                if type(sound) == GameSound:
                    sy = sound.y
                    if sound.level == g.current_level:
                        #we are in the same room
                        sx = sound.x  
                    else:
                        if sound.level in g.current_level.connected_levels:
                            #in adjacent rooms
                            sx = sound.x + ((sound.level.world_x - g.current_level.world_x)*64)
                        else:
                            #too far away
                            sound.sound.set_volume(0)
                            continue

                    dist = util.get_distance(g.player.rect.centerx, g.player.rect.centery, sound.x, sound.y)
                    if dist < 1:
                        dist = 1

                    vol = min(1, (1/dist)*sound.volume)
                    sound.sound.set_volume(vol)

    def stop_sounds(self):
        for sound in g.sound_dict.values():
            sound.stop()
        for i,channel in enumerate(self.channel_list):
            #channel.stop()
            self.sound_playing_list[i] = None


class GameSound():
    """
    Class for 2D sound
    """
    def __init__(self, name, pos, level, volume=3):
        self.name = name
        
        self.sound = g.sound_dict[self.name]
        self.volume = volume
        self.level = level
        self.x, self.y = pos

    def stop(self):
        self.sound.stop()


def load_sounds():
    """
    Load all sounds from the sound directory
    """
    path = g.SOUNDS_DIR
    for sound_file in os.listdir(path):
        if sound_file.endswith(".ogg"):
            sound = p.mixer.Sound(os.path.join(g.SOUNDS_DIR, sound_file))

            g.sound_dict[sound_file[:-4]] = sound

def play_sound(name, pos=None, level=None, volume=3):
    #print(name)
    """
    Play a sound, optional a 2D one
    """
    if pos: #2D sound
        sound = GameSound(name, pos, level, volume=volume)
    else: #non-2D sound
        sound = g.sound_dict[name]
        sound.set_volume(volume)

    g.channel_list.play(sound)
    return sound

def play_main_music():
    """
    Play the main music track for this game
    """
    p.mixer.music.load(os.path.join(g.SOUNDS_DIR,"music.ogg"))
    p.mixer.music.play(-1)
    
