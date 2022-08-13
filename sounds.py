import global_values as g
import utilities as util

import pygame as p
import os

class ChannelList():
    """
    Class for list of channels
    """
    def __init__(self, channel_amount=16):
        self.channel_list = []
        

        self.sound_playing_list = [None for _ in range(channel_amount)]
        p.mixer.set_num_channels(channel_amount)
        for i in range(channel_amount):
            channel = p.mixer.Channel(i)
            self.channel_list.append(channel)
            self.next_available_channel = 0

    def play(self, sound):
        channel = self.channel_list[self.next_available_channel]

        self.sound_playing_list[self.next_available_channel] = sound
        if type(sound) == GameSound:
            sound = sound.sound
        elif type(sound) == p.mixer.Sound:
            channel.set_volume(1)


        channel.play(sound)
        self.next_available_channel = (self.next_available_channel + 1) % len(self.channel_list)

    def update(self):
        #change sound volume based on distance
        for i, channel in enumerate(self.channel_list):
            if channel.get_busy():
                sound = self.sound_playing_list[i]

                if type(sound) == GameSound:

                    dist = util.get_distance(g.player.rect.centerx, g.player.rect.centery, sound.x, sound.y)
                    if dist < 1:
                        dist = 1

                    vol = min(1, (1/dist)*sound.volume)
                    channel.set_volume(vol)

    def stop_sounds(self):
        for i,channel in enumerate(self.channel_list):
            channel.stop()
            self.sound_playing_list[i] = None


class GameSound():
    """
    Class for 2D sound
    """
    def __init__(self, name, pos, volume=3):
        self.name = name

        self.sound = g.sound_dict[self.name]
        self.volume = volume
        self.x, self.y = pos

    def stop(self):
        self.sound.stop()


def load_sounds():
    """
    Load all sounds from the sound directory
    """
    path = g.SOUNDS_DIR
    for sound_file in os.listdir(path):
        if sound_file.endswith(".wav"):
            sound = p.mixer.Sound(os.path.join(g.SOUNDS_DIR, sound_file))

            g.sound_dict[sound_file[:-4]] = sound

            print(sound_file)

def play_sound(name, pos=None, volume=3):
    #print(name)
    """
    Play a sound, optional a 2D one
    """
    if pos: #2D sound
        sound = GameSound(name, pos, volume=volume)
    else: #non-2D sound
        sound = g.sound_dict[name]
        sound.set_volume(volume)
    g.channel_list.play(sound)
    return sound

    
