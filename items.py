import global_values as g
import graphics as gfx
import entities
import particles
import creatures
import levels

import pygame as p
import random as r
import math as m

class Item:
    def __init__(self, name):
        self.name = name

        try:
            self.icon = gfx.load_image(name+"_icon")
        except:
            self.icon = None

        try:
            self.surface = gfx.load_image(name)
        except:
            self.surface = None

        self.amount = 1

    def pickup(self):
        pass

    def __getstate__(self):
        return gfx.pickle_state(self.__dict__)

    def __setstate__(self, state):
        self.__dict__ = gfx.unpickle_state(state)

class Consumable(Item):
    def __init__(self, name):
        super().__init__(name)
        
    def consume(self):
        pass

class Medkit(Consumable):
    def __init__(self):
        super().__init__("medkit")

    def consume(self):
        super().consume()
        g.player.change_health(3)

class Ammunition(Item):
    def __init__(self, name, gun_name, ammunition_amount):
        self.gun_name = gun_name
        self.ammunition_amount = ammunition_amount
        super().__init__(name)

    def pickup(self):
        super().pickup()
        gun = g.player.inventory.check_for_named_item(self.gun_name)
        gun.change_ammunition(self.ammunition_amount)
        print(">>",self.ammunition_amount)

        g.player.inventory.remove(self)

class HandgunAmmunition(Ammunition):
    def __init__(self):
        super().__init__("H. ammo", "handgun", 10)
class ShotgunAmmunition(Ammunition):
    def __init__(self):
        super().__init__("S. ammo", "shotgun", 5)
class RevolverAmmunition(Ammunition):
    def __init__(self):
        super().__init__("R. ammo", "revolver", 3)
         
        

class Gun(Item):
    def __init__(self, name, holder, damage, cooldown, fire_range, projectiles=1, spread=0, max_ammunition=50, recharge=0, stun=0, fire_effect=1):
        super().__init__(name)
        
        self.damage = damage
        self.max_cooldown = cooldown
        self.range = fire_range

        self.last_fire_time = None
        self.max_ammunition = max_ammunition
        self.ammunition = self.max_ammunition
        self.recharge = recharge
        self.stun = stun
        self.fire_effect = fire_effect

        self.projectiles = projectiles
        self.spread = spread

        self.holder = holder

    def attempt_fire(self):
        if self.ammunition >= 1:

            if not self.last_fire_time or (p.time.get_ticks()-self.last_fire_time)/1000 >= self.max_cooldown:
                self.fire()
                self.change_ammunition(-1)
                self.ammunition = int(self.ammunition)
                self.last_fire_time = p.time.get_ticks()
                return True
        return False

    def change_ammunition(self, amount):
        self.ammunition += amount
        if self.ammunition < 0:
            self.ammunition = 0

        if self.ammunition >= self.max_ammunition:
            self.ammunition = self.max_ammunition

    def fire(self):
        for _ in range(self.projectiles):
            angle = self.holder.angle + ((r.random()-0.5)*self.spread)

            bullet_rect = p.Rect(self.holder.rect.centerx, self.holder.rect.centery, 1, 1)
            bullet_mask = p.mask.Mask((bullet_rect.w, bullet_rect.h), fill=True)
            bullet_mask.fill()

            bullet = entities.Entity(bullet_rect,
            self.holder.level, collision_exceptions=[self.holder], solid=False, mask=bullet_mask)
            target_x = self.holder.rect.centerx + m.cos(angle)*self.range
            target_y = self.holder.rect.centery + m.sin(angle)*self.range

            result = bullet.move_towards(target_x, target_y, self.range, detail=True)

            if result:
                #level, pos, angle)
                if isinstance(result, creatures.Creature):
                    if self.damage > 0:
                        particles.create_blood(bullet.level, (bullet.x, bullet.y), self.holder.angle + m.pi )
                    result.take_damage(self.damage)
                    if self.stun:
                        result.stun(self.stun)

                if isinstance(result, levels.Level):
                                                                #level, position, angle, colour, spread, amount, power, timer
                    particles.Particles(bullet.level, (bullet.x, bullet.y), self.holder.angle + m.pi, "brown", 1, 5, 5, 10)

            else:
                pass
            bullet.delete()

def create_item(name):
    """
    Create item from name
    """
    new_item = eval(f"{name}()")
    return new_item