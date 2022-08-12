import pygame as p
import math as m

import global_values as g
import graphics as gfx
import elements
import actions

class Camera(elements.Element):
    def __init__(self, parent, offset):
        self.parent = parent
        self.offset = offset

        self.old_parent_direction = "left"

        self.look_offset = 0
        rect = p.Rect(0, 0, 64, 64)
        super().__init__(rect)

    def update(self):
        if self.old_parent_direction != self.parent.direction:
            self.old_parent_direction = self.parent.direction

        diff_from_center = g.mx - g.WIDTH/2
        
        if not hasattr(self.parent, "control_locks") or not g.player.control_locks:
            self.look_offset = m.sin( diff_from_center/(g.WIDTH/2) )*24
        else:
            self.look_offset = 0
 
        self.x = self.parent.rect.centerx + self.offset[0] + self.look_offset
        self.y = self.parent.rect.centery + self.offset[1]
        super().update()



    def transform_point(self, point):
        new_point = (point[0]-self.x, point[1]-self.y)
        return new_point

    def transform_rect(self, rect):
        """
        Transform a rect from world-space to camera-space
        """
        new_rect = rect.copy()
        new_rect.x -= self.x
        new_rect.y -= self.y
        return new_rect

    def draw_rect(self, colour, rect, border=0):
        p.draw.rect(g.screen, colour, self.transform_rect(rect), border)

    def draw_circle(self, colour, pos, radius, border=0):
        p.draw.circle(g.screen, colour, self.transform_point(pos), radius, border)

    def draw_gfx(self, drawing_gfx, pos, flip_h=False):
        if drawing_gfx:
            surf = gfx.get_surface(drawing_gfx)
            if flip_h:
                surf = p.transform.flip(surf, True, False)
            g.screen.blit(surf, self.transform_point(pos))

    def set_at(self, pos, colour):
        x,y = self.transform_point(pos)
        x = int(x)
        y = int(y)
        g.screen.set_at((x,y), colour)

    def draw_rotated_gfx(self, rotating_gfx, angle, pos, ox=0.5, oy=0.5, xflip=False, yflip=False):
        surf = gfx.get_surface(rotating_gfx)
        if xflip or yflip:
            surf = p.transform.flip(surf, xflip, yflip)
        rotated_surface = p.transform.rotate(surf, m.degrees(-angle))

        #create offset
        rw = rotated_surface.get_width()
        rh = rotated_surface.get_height()

        cx = -(rw/2) #+ (m.cos(angle) * rw * 0.5 )#(m.cos(angle)*(-0.5+ox)*2*(rotated_surface.get_width()/2))
        cy = -(rh/2) #+ (m.sin(angle) * rh * 0.5 )#(m.sin(angle)*(-0.5+oy)*2*(rotated_surface.get_height()/2))

        tx = m.cos(angle)/2 * rw * (-1 + ox*2) 
        ty = m.sin(angle)/2 * rh * (-1 + ox*2) 

        tx += m.cos( angle + (m.pi/2) )/2 * rh * (-1 + oy*2) 
        ty += m.sin( angle + (m.pi/2) )/2 * rw * (-1 + oy*2) 

        g.screen.blit(rotated_surface, self.transform_point((pos[0]+cx-tx, pos[1]+cy-ty)))

        #p.draw.circle(g.screen, "green", self.transform_point((pos[0]+tx, pos[1]+ty)), 1)
        #p.draw.circle(g.screen, "yellow", self.transform_point((pos[0]-tx, pos[1])), 1)
        #p.draw.circle(g.screen, "yellow", self.transform_point((pos[0], pos[1]-ty)), 1)