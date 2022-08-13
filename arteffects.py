import pygame
import random


def melt(surf, n_frames, blood_colors=((128, 51, 30), (78, 39, 28)), blood_rate=0.2, compression_factor=0.8, decay_rate=0.1, xshift_rate=0.15):
    res = []

    for i in range(0, n_frames):
        frame = pygame.Surface(surf.get_size(), 0, surf)
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

                    if 0 <= new_x < frame.get_width() and 0 <= new_y <= frame.get_height():
                        frame.set_at((new_x, new_y), color_at)
        res.append(frame)
        surf = frame
    return res


def shift_down(surf):
    heights = [0] * surf.get_width()
    res = pygame.Surface(surf.get_size(), 0, surf)
    for x in range(0, surf.get_width()):
        for y in range(surf.get_height() - 1, -1, -1):
            color_at = color_at = surf.get_at((x, y))
            if color_at[3] == 255:
                new_y = surf.get_height() - 1 - heights[x]
                heights[x] += 1
                res.set_at((x, new_y), color_at)
    return res


def gen_melted_basic_enemy(outfile):
    sheet = pygame.image.load("res/gfx_new/basic_enemy_ss.png")
    surf = sheet.subsurface((32, 0, 16, 32))
    frames = melt(surf, 4)
    frames[-1] = shift_down(frames[-1])
    outsurf = pygame.Surface((sum(f.get_width() for f in frames),
                              max(f.get_height() for f in frames)))
    x = 0
    for f in frames:
        outsurf.blit(f, (x, 0))
        x += f.get_width()

    pygame.image.save(outsurf, outfile)


if __name__ == "__main__":
    # pygame.display.set_mode((50, 50), 0, 32)
    gen_melted_basic_enemy("enemy_death_seq.png")

