import pygame

import os
import random

import global_values as g


def melt(surf, n_frames, blood_colors=((128, 51, 30), (78, 39, 28)), blood_rate=0.2, compression_factor=0.8, decay_rate=0.1, xshift_rate=0.15):
    res = []

    for i in range(0, n_frames):
        frame = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        frame.fill((0, 0, 0, 0))
        x_list = list(range(0, surf.get_width()))
        random.shuffle(x_list)
        for x in x_list:
            y_list = list(range(0, surf.get_height()))
            random.shuffle(y_list)
            for y in y_list:
                color_at = surf.get_at((x, y))
                if color_at[3] == 255 and random.random() > decay_rate:
                    h = surf.get_height() - y
                    new_h = int((1 - compression_factor / n_frames) * h)
                    if random.random() < (blood_rate / n_frames):
                        color_at = random.choice(blood_colors)
                    new_y = surf.get_height() - new_h

                    if random.random() < xshift_rate:
                        new_x = x + (1 if random.random() < 0.5 else -1)
                    else:
                        new_x = x

                    if is_valid_pos((new_x, new_y), frame):
                        frame.set_at((new_x, new_y), color_at)
        res.append(frame)
        surf = frame
    return res


def shift_down(surf):
    heights = [0] * surf.get_width()
    res = pygame.Surface(surf.get_size(), 0, surf)
    for x in range(0, surf.get_width()):
        for y in range(surf.get_height() - 1, -1, -1):
            color_at = surf.get_at((x, y))
            if color_at[3] == 255:
                new_y = surf.get_height() - 1 - heights[x]
                heights[x] += 1
                res.set_at((x, new_y), color_at)
    return res


def is_valid_pos(xy, surf):
    return 0 <= xy[0] < surf.get_width() and 0 <= xy[1] < surf.get_height()


def add_outline(surf, outline_color):
    res = surf.copy()
    neighbors = [(-1, 0), (0, 1), (0, -1), (0, 1)]
    for x in range(0, surf.get_width()):
        for y in range(0, surf.get_height()):
            color_at = surf.get_at((x, y))
            if color_at[3] == 255 and color_at[0:3] != outline_color[0:3]:
                for n in neighbors:
                    px_to_color = (x + n[0], y + n[1])
                    if is_valid_pos(px_to_color, res) and surf.get_at(px_to_color)[3] < 255:
                        res.set_at(px_to_color, outline_color)
    return res


def gen_death_animation(infile, outfile, n_frames=4,
                        compression=0.666, xshift_rate=0.05, decay_rate=0.1,
                        blood_colors=((128, 51, 30), (78, 39, 28)), blood_rate=0.2,
                        outline_color=g.colour_remaps["black"]):

    if isinstance(infile, str):
        surf = pygame.image.load(infile)
    elif isinstance(infile, pygame.Surface):
        surf = infile
    elif isinstance(infile, tuple):
        filepath, rect = infile
        sheet = pygame.image.load(filepath)
        surf = sheet.subsurface(rect).copy()
    else:
        raise ValueError(f"Unexpected infile type: {infile}")

    frames = melt(surf, n_frames, compression_factor=compression, xshift_rate=xshift_rate, decay_rate=decay_rate,
                  blood_colors=blood_colors, blood_rate=blood_rate)
    frames[-1] = shift_down(frames[-1])
    if outline_color is not None:
        frames = [add_outline(f, outline_color) for f in frames]
    total_width = sum(f.get_width() for f in frames)
    total_height = max(f.get_height() for f in frames)
    outsurf = pygame.Surface((total_width, total_height), pygame.SRCALPHA)
    outsurf.fill((0, 0, 0, 0))

    x = 0
    for f in frames:
        outsurf.blit(f, (x, 0))
        x += f.get_width()

    pygame.image.save(outsurf, outfile)


if __name__ == "__main__":
    if not os.path.exists("gen/"):
        os.mkdir("gen/")

    gen_death_animation(("res/gfx_new/basic_enemy_ss.png", (32, 0, 16, 32)), "gen/enemy_death_seq.png")
    gen_death_animation("res/gfx_new/player_single.png", "gen/player_corpse_ss.png", compression=0.5, blood_rate=0.3, xshift_rate=0, decay_rate=0)
    gen_death_animation(("res/gfx_new/large_enemy_ss.png", (0, 0, 48, 48)), "gen/large_enemy_corpse_ss.png", compression=0.6, xshift_rate=0.05)
    gen_death_animation(("res/gfx_new/spider_enemy_ss.png", (0, 0, 32, 16)), "gen/spider_enemy_corpse_ss.png", compression=0.3)

