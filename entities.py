import global_values as g
import utilities as util
import graphics as gfx
import elements

import math as m

class Entity(elements.Element):
    """
    Base class for all entities (world objects)
    """
    def __init__(self, rect, level, entity_gfx=None, solid=True, mask=None, collision_exceptions=[], collision_dict={}):
        super().__init__(rect)
        self.level = None
        self.set_level(level)
        self.gfx = entity_gfx
        self.surface = None

        self.solid = solid
        self.last_collision = None
        self.collision_exceptions = collision_exceptions
        self.collision_dict = collision_dict
        self.mask = mask

        self.old_vx = self.x
        self.old_vy = self.y
        self.change_x = self.x-self.old_vx
        self.change_y = self.y-self.old_vy

    def update(self):
        super().update()
        self.change_x = self.x-self.old_vx
        self.change_y = self.y-self.old_vy
        self.old_vx = self.x
        self.old_vy = self.y

    def update_inactive(self):
        """
        Update this entity when it's not in the same level as the player
        """
        pass

    def set_level(self, level):
        """
        Set the level this entity is in
        """
        #remove from old level
        if self.level:
            self.level.entities.remove(self)

        if level:
            self.level = level

            #add to new level
            self.level.entities.append(self)

    def move_towards(self, x, y, speed, detail=False):
        """
        Move some distance towards a point, accounting for collision
        """
        if util.get_distance(self.x, self.y, x, y) <= speed:
            dx = x-self.x
            dy = y-self.y
        else:
            angle = util.get_angle(self.x, self.y, x, y)
            dx = round(m.cos(angle)*speed, 6)
            dy = round(m.sin(angle)*speed, 6)

        result = self.move(dx, dy, detail=detail)
        return result

    def move(self, x, y, detail=False):
        """
        Move some distance, accounting for collision
        """
        steps = m.ceil(max(abs(x), abs(y)))
        nx = self.x
        ny = self.y
        new_rect = self.rect.copy()
        if not steps:
            return
            
        ax = x/steps
        ay = y/steps
        
        result = None
        for _ in range(steps):
            nx += ax
            ny += ay
            new_rect.x = nx
            new_rect.y = ny
            result = util.check_collision(new_rect, obj=self, _collision_dict=self.collision_dict, exceptions=self.collision_exceptions, detail=detail, mask=self.mask)

            if result:
                nx -= ax
                ny -= ay

                new_rect.x = nx
                new_rect.y = ny

                self.last_collision = result
                break

        self.x = nx
        self.y = ny

        if result:
            return result

    def delete(self):
        if not self.deleted:
            if self.level:
                self.level.entities.remove(self)
        super().delete()

    def level_left(self):
        """
        Called when the player leaves a level with this entity in it
        """
        pass

    def level_entered(self):
        """
        Called when a player enters a level with this entity in it
        """
        pass
                
    def draw(self):
        #g.camera.draw_rect("red", self.rect, 1)
        if self.gfx:
            self.surface = gfx.get_surface(self.gfx)
            g.camera.draw_gfx(self.surface, self.rect.topleft)