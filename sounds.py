import global_values as g

import pygame as p
import os

class ChannelList():
    """
    Class for list of channels
    """
    def __init__(self, channel_amount=8):
        self.channel_list = []
        

        self.sound_playing_list = [None for _ in range(channel_amount)]
        p.mixer.set_num_channels(channel_amount)
        for i in range(channel_amount):
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

                    dist = util.get_distance(g.player.rect.centerx, g.player.rect.centery, sound.x, sound.y)

                    #set sound volume (might cause an issue when multiple copies of the same sound play?)
                    vol = min(1, (1/dist)*2)
                    sound.set_volume(vol)

class GameSound():
    """
    Class for 2D sound
    """
    def __init__(self, name, pos):
        self.name = name

        self.sound = g.sound_dict[self.name]
        self.x, self.y = pos


def load_sounds():
    """
    Load all sounds from the sound directory
    """
    path = g.SOUNDS_DIR
    for sound_file in os.listdir(path):
        sound = p.mixer.Sound(os.path.join(g.SOUNDS_DIR, sound_file))

        g.sound_dict[sound_file[:-4]] = sound

        print(sound_file)

def play_sound(name):
    """
    Play a sound without involving the channel list (not 2D)
    """
    sound = g.sound_dict[name]
    sound.play()

    
