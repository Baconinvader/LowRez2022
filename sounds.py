import global_values as g

import pygame as p
import os

class ChannelList():
    """
    Class for list of channels
    """
    def __init__(self):
        self.channel_list = []
        self.sound_playing_list = [None for _ in range(10)]
        for i in range(10):
            channel = p.mixer.Channel(i)
            self.channel_list.append(channel)
            self.next_available_channel = 0

    def play(self, sound):
        channel = self.channel_list[self.next_available_channel]

        if type(sound) == GameSound:
            sound = GameSound.sound

        channel.play(sound)
        self.next_available_channel = (self.next_available_channel + 1) % len(self.channel_list)

    def update(self):
        #change sound volume based on distance
        for i, channel in enumerate(self.channel_list):
            if channel.get_busy():
                sound = self.sound_playing_list[i]

                if type(sound) == GameSound:
                    sound = GameSound.sound
                    #TODO

class GameSound():
    """
    Class for 2D sound
    """
    def __init__(self, name, pos):
        self.name = name

        self.sound = g.sound_dict[self.name]
        self.pos = pos


def load_sounds():
    path = g.SOUNDS_DIR
    for sound_file in os.listdir(path):
        sound = p.mixer.Sound(os.path.join(g.SOUNDS_DIR, file_name))

        g.sound_dict[sound_file[:-4]] = sound

        game_sound = GameSound(sound_file[:-4])
        print(sound_file)

    
