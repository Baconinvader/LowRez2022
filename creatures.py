import math as m
import pygame as p
import random as r

import global_values as g
import utilities as util
import graphics as gfx
import entities
import particles
import actions
import sounds

class Creature(entities.Entity):
    def __init__(self, rect, level, name, max_health=10, solid=True):
        
        self.direction = "right"
        self.speed = 0.02
        self.max_health = max_health
        self.health = self.max_health

        self.name = name
        self.anims = g.spritesheets[f"{self.name}_ss"].create_animation_system({"static":0, "moving":1}, 0.25)

        self.stunned = False

        super().__init__(rect, level, entity_gfx=self.anims, solid=solid)

    def update(self):
        if self.change_x:
            self.gfx.set_anim("moving")
        else:
            self.gfx.set_anim("static")
    
        super().update()

    def change_health(self, amount):
        self.health += amount
        if self.health >= self.max_health:
            self.health = self.max_health

        if self.health <= 0:
            self.die()

    def take_damage(self, amount):
        self.change_health(-amount)

    def die(self):
        pass

    def stun(self, timer):
        self.stunned = True
        actions.VarChangeAction(self.pipe, timer, self, "stunned", False, change_type=2, blocking=False, blockable=False)

    def move(self, x, y, detail=False):
        result = super().move(x, y, detail=detail)
        if x > 0:
            self.direction = "right"
        elif x < 0:
            self.direction = "left"

        return result

    def draw(self):
        if self.direction == "right":
            flip_h = False
        else:
            flip_h = True


        surf = gfx.get_surface(self.gfx)
        if flip_h:
            self.surface = p.transform.flip(surf, True, False)
        else:
            self.surface = surf
        #gfx.get_mask(self.surface).to_surface()
        g.camera.draw_gfx( self.surface , self.rect.topleft)

        if self.stunned:
            state = r.getstate()

            r.seed(self.x + ( int(p.time.get_ticks()*0.006) %3) )
            for _ in range(10):
                x = self.rect.centerx + (m.sin(r.random())-0.5)*self.rect.w
                y = self.rect.centery + (m.sin(r.random())-0.5)*self.rect.h
                g.camera.draw_circle("blue", (x,y), 1)

            r.setstate(state)

class Enemy(Creature):
    """
    Base class for all enemies
    """
    def __init__(self, rect, level, name, respawn_time=0, speed=0.006, damage=1, attack_time=2, max_health=10):
        super().__init__(rect, level, name, max_health=max_health)
        self.gfx = g.spritesheets[f"{self.name}_ss"].create_animation_system({"static":0, "moving":1, "attacking":2}, 0.25)

        self.attacking = False
        self.speed = speed
        self.attack_time = attack_time
        self.damage = damage
        self.respawn_time = respawn_time

    def update(self):
        super().update()
        self.update_ai()

        if self.attacking:
            self.gfx.set_anim("attacking")
        else:
            if self.change_x:
                self.gfx.set_anim("moving")
            else:
                self.gfx.set_anim("static")

    def move_towards(self, x, y):
        result_x = super().move_towards(x, self.y, self.speed)
        result_y = super().move_towards(self.x, y, self.speed)

        result = None
        if result_x:
            result = result_x
        elif result_y:
            result = result_y
        return result

    def attack(self):
        """
        Finish attack on the player
        """
        self.attacking = False

    def update_ai(self):
        pass

    def die(self):
        Corpse(self, self.x, self.y, self.level)
        self.delete()

class Corpse(entities.Entity):
    """
    Corpse of an creature
    """
    def __init__(self, enemy, x, y, level):
        corpse_ss_dict = {"basic_enemy":0, "large_enemy":0, "recover_enemy":1}
        self.enemy = enemy
        self.corpse_anim_index = corpse_ss_dict[enemy.name]

        rect = p.Rect(x, y, 32, 32)
        corpse_gfx = g.spritesheets["corpse_ss"].create_animation(self.corpse_anim_index, 0.25, global_time=False, repeat=False)
        super().__init__(rect, level, entity_gfx=corpse_gfx, solid=False)


        if self.enemy.respawn_time:
            actions.FuncCallEffect(self.pipe, 10, self, "recover", change_type=1)

    def update(self):
        super().update()

    def recover(self):
        """
        Reverse corpse anim and prepare to respawn
        """
        timer = self.gfx.max_timer * len(self.gfx.frames)
        self.gfx.reverse = True
        self.gfx.reset()
        actions.FuncCallEffect(self.pipe, timer, self, "respawn", change_type=1)

    def respawn(self):
        """
        Respawn enemy
        """
        x = self.enemy.x + (self.enemy.rect.w/4)
        y = self.enemy.y
        level = self.enemy.level

        self.enemy.__class__(x, y, level)
        self.delete()




class BasicEnemy(Enemy):
    """
    Basic melee enemy
    """
    def __init__(self, x, y, level):
        rect = p.Rect(x, y, 16, 32)
        super().__init__(rect, level, "basic_enemy", max_health=5)

    def update_ai(self):
        super().update_ai()

        if not self.stunned and not self.attacking:
            result = self.move_towards(g.player.x, g.player.y)
            if result == g.player:
                self.attacking = True
                actions.FuncCallEffect(self.pipe, self.attack_time, self, "attack", change_type=1)
                print("ATTACK")

                

    def attack(self):
        super().attack()
        sounds.play_sound("bleep1", self.rect.center)

        if util.get_distance(self.rect.centerx, self.rect.centery, g.player.rect.centerx, g.player.rect.centery) <= 20:
            g.player.take_damage(self.damage)

class RecoverEnemy(Enemy):
    """
    Melee enemy which cannot dies
    """
    def __init__(self, x, y, level):
        rect = p.Rect(x, y, 16, 32)
        super().__init__(rect, level, "recover_enemy", max_health=4, respawn_time=20)

    def update_ai(self):
        super().update_ai()

        if not self.stunned and not self.attacking:
            result = self.move_towards(g.player.x, g.player.y)
            if result == g.player:
                self.attacking = True
                actions.FuncCallEffect(self.pipe, self.attack_time, self, "attack", change_type=1)

    def attack(self):
        super().attack()
        if util.get_distance(self.rect.centerx, self.rect.centery, g.player.rect.centerx, g.player.rect.centery) <= 20:
            g.player.take_damage(self.damage)

class LargeEnemy(Enemy):
    """
    Large melee enemy
    """
    def __init__(self, x, y, level):
        rect = p.Rect(x, y, 32, 60)
        super().__init__(rect, level, "large_enemy", max_health=50, speed=0.01)
        self.regen = 1

    def update(self):
        super().update()
        self.change_health(self.regen * g.dt)

    def update_inactive(self):
        super().update_inactive()

        #move
        result = None
        if self.direction == "left":
            result = self.move(-self.speed, 0)
        elif self.direction == "right":
            result = self.move(self.speed, 0)

        #switch
        if result:
            if self.direction == "left":
                self.direction = "right"
            elif self.direction == "right":
                self.direction = "left"


    def update_ai(self):
        super().update_ai()

        if not self.stunned and not self.attacking:
            result = self.move_towards(g.player.x, g.player.y)

    def attack(self):
        super().attack()
        if util.get_distance(self.rect.centerx, self.rect.centery, g.player.rect.centerx, g.player.rect.centery) <= 20:
            g.player.take_damage(self.damage)
        
        

def spawn_enemy(name, x, y, level):
    """
    Spawn an enemy at a given level and location
    """
    eval_string = f"{name}({x}, {y}, level)"
    new_enemy = eval(eval_string)
    return new_enemy