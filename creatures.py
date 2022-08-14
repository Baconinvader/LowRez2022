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
    def __init__(self, rect, level, name, max_health=10, solid=True, collision_dict={}, footstep_sound="footstep"):
        
        self.direction = "right"
        self.speed = 15  # units per second
        self.max_health = max_health
        self.health = self.max_health

        self.name = name
        self.anims = g.spritesheets[f"{self.name}_ss"].create_animation_system({"static":0, "moving":1}, 0.25)
        self.flip_h = False
        self.flip_v = False

        self.stunned = 0
        self.stun_effect = False
        self.dead = False

        super().__init__(rect, level, entity_gfx=self.anims, solid=solid, collision_dict=collision_dict)

        
        self.footstep_timer = 0.5
        self.footstep_sound = footstep_sound
        self.footstep_cooldown = actions.Action(self.pipe, self.footstep_timer, blocking=False, blockable=False)

    def set_animation(self):
        if self.change_x:
            self.gfx.set_anim("moving")
        else:
            self.gfx.set_anim("static")

    def update(self):
        self.set_animation()
    
        super().update()

    def change_health(self, amount):
        self.health += amount
        if self.health >= self.max_health:
            self.health = self.max_health

        if self.health <= 0:
            self.health = 0
            if not self.dead:
                self.die()

    def take_damage(self, amount, source=None):
        self.change_health(-amount)

    def die(self):
        self.dead = True

    def stun(self, timer):
        self.stunned += 1
        self.stun_effect = True
        #actions.VarChangeAction(self.pipe, timer, self, "stunned", False, change_type=2, blocking=False, blockable=False)
        actions.FuncCallAction(self.pipe, timer, self, "remove_stun", change_type=1, blocking=False, blockable=False)

    def remove_stun(self):
        self.stunned -= 1
        if self.stunned < 0:
            self.stunned = 0
        if not self.stunned:
            self.stun_effect = False

    def move(self, x, y, detail=False):
        result = super().move(x, y, detail=detail)
        if x > 0:
            self.direction = "right"
        elif x < 0:
            self.direction = "left"

        if x != 0 and not result:
            if not self.footstep_cooldown.active:
                self.footstep_cooldown = actions.Action(self.pipe, self.footstep_timer, blockable=False, blocking=False)
                sounds.play_sound(self.footstep_sound, self.rect.center, self.level)
        return result

    def get_direction_for_rendering(self):
        return self.direction

    def draw(self):
        if self.get_direction_for_rendering() == "right":
            flip_h = False
        else:
            flip_h = True

        surf = gfx.get_surface(self.gfx)
        if flip_h or self.flip_h or self.flip_v:
            self.surface = p.transform.flip(surf, (flip_h or self.flip_h), self.flip_v)
        else:
            self.surface = surf

        #gfx.get_mask(self.surface).to_surface()
        g.camera.draw_gfx( self.surface , self.rect.topleft)

        if self.stun_effect:
            state = r.getstate()

            r.seed(self.x + ( int(p.time.get_ticks()*0.006) %3) )
            for _ in range(10):
                x = self.rect.centerx + (m.sin(r.random())-0.5)*self.rect.w
                y = self.rect.centery + (m.sin(r.random())-0.5)*self.rect.h
                g.camera.draw_circle("blue", (x,y), 1)

            r.setstate(state)

        #g.camera.draw_rect("red", self.rect, 1)

class Enemy(Creature):
    """
    Base class for all enemies
    """
    def __init__(self, rect, level, name, respawn_time=0, speed=16, damage=1, attack_time=0.85, max_health=10, footstep_sound="footstep_enemy", collision_dict={"class_Enemy":False}):
        super().__init__(rect, level, name, max_health=max_health, collision_dict=collision_dict, footstep_sound=footstep_sound)
        self.z_index = 0.5
        self.gfx = g.spritesheets[f"{self.name}_ss"].create_animation_system({"static":0, "moving":1, "attacking":2}, 0.25)

        self.attacking = False
        self.speed = speed
        self.attack_time = attack_time
        self.damage = damage
        self.respawn_time = respawn_time

        self.played_encounter_sound = False

    def level_entered(self):
        super().level_entered()
        self.played_encounter_sound = False

        #type_string = self.class_names[0]
        #enemies_of_type = g.elements[type_string]
        #print(self, type_string, len(enemies_of_type) )

        #find closest enemy of type
        #closest_enemy = None
        #closest_dist = 512
        #for enemy in enemies_of_type:
        #    if enemy.level == self.level:
        #        dist = abs(g.player.rect.centerx - enemy.rect.centerx)
        #        if not closest_enemy or dist < closest_dist:
        #            closest_enemy = enemy
        #            closest_dist = dist
        
        #make sound if we are that enemy
        #if closest_enemy == self:
        #    sounds.play_sound(type_string[6:]+"_level_noise", self.rect.center)

    def update(self):
        super().update()
        self.update_ai()

        #print(self.attacking)
        if self.attacking:
            self.gfx.set_anim("attacking")
        else:
            if self.change_x:
                self.gfx.set_anim("moving")
            else:
                self.gfx.set_anim("static")

        if not self.played_encounter_sound:
            dist_from_camera = abs(g.camera.rect.centerx - self.rect.centerx)
            if dist_from_camera <= 32:
                type_string = self.class_names[0]
                print("play",type_string)
                self.played_encounter_sound = sounds.play_sound(type_string[6:]+"_level_noise", self.rect.center, self.level, volume=5)
        else:
            self.played_encounter_sound.x = self.rect.centerx
            self.played_encounter_sound.y = self.rect.centery


    def level_entered(self):
        super().level_entered()
        self.attacking = False

    def move_towards(self, x, y):
        result_x = super().move_towards(x, self.y, self.speed * g.dt)
        result_y = super().move_towards(self.x, y, self.speed * g.dt)

        result = None
        if result_x:
            result = result_x
        elif result_y:
            result = result_y
        return result

    def take_damage(self, amount, source=None):
        super().take_damage(amount)
        stun_timer = amount*0.8

        self.stunned += 1
        actions.FuncCallAction(self.pipe, stun_timer, self, "remove_stun", change_type=1, blocking=False, blockable=False)

        sounds.play_sound("enemy_damage", pos=self.rect.center, level=self.level, volume=6)
 

    def attack(self):
        """
        Finish attack on the player
        """
        if g.IS_DEV and g.NO_ATTACK:
            self.attacking = False
        elif "main" in g.active_states and self.level == g.current_level:
            self.attacking = False
            sounds.play_sound("enemy_attack", self.rect.center, level=self.level, volume=7)

            if util.get_distance(self.rect.centerx, self.rect.centery, g.player.rect.centerx, g.player.rect.centery) <= self.rect.w/2 + g.player.rect.w/2 + 4:
                g.player.take_damage(self.damage)
        else:
            self.attacking = False

    def update_ai(self):
        pass

    def die(self):
        Corpse(self, self.x, self.y, self.level)
        if self.played_encounter_sound:
            self.played_encounter_sound.stop()
        self.delete()

class Corpse(entities.Entity):
    """
    Corpse of an creature
    """
    def __init__(self, enemy, x, y, level):
        corpse_ss_dict = {"player":2, "basic_enemy":0, "large_enemy":0, "recover_enemy":1, "spider_enemy":3}
        self.enemy = enemy
        self.corpse_anim_index = corpse_ss_dict[enemy.name]

        rect = p.Rect(x, y, 32, 32)
        corpse_gfx = g.spritesheets["corpse_ss"].create_animation(self.corpse_anim_index, 0.25, global_time=False, repeat=False)
        super().__init__(rect, level, entity_gfx=corpse_gfx, solid=False, collision_dict={"class_Entity":False})


        if self.enemy.respawn_time:
            actions.FuncCallAction(self.pipe, 10, self, "recover", change_type=1, blocking=False, blockable=False)

    def update(self):
        super().update()
        #move to bottom
        if self.rect.bottom != self.level.rect.bottom:
            self.move(0, 9.8*2*g.dt)

    def recover(self):
        """
        Reverse corpse anim and prepare to respawn
        """
        timer = self.gfx.max_timer * len(self.gfx.frames)
        self.gfx.reverse = True
        self.gfx.reset()
        actions.FuncCallAction(self.pipe, timer, self, "respawn", change_type=1, blocking=False, blockable=False)

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
                actions.FuncCallAction(self.pipe, self.attack_time, self, "attack", change_type=1, blocking=False, blockable=False)

class SpiderEnemy(Enemy):
    """
    Crawling spider enemy
    """
    def __init__(self, x, y, level):
        rect = p.Rect(x, y, 32, 16)
        super().__init__(rect, level, "spider_enemy", max_health=3, speed=25)

        self.on_ceiling = True

    def update_ai(self):
        super().update_ai()

        if not self.stunned and not self.attacking:
            #fall
            if self.on_ceiling:
                if abs(g.player.rect.centerx - self.rect.centerx) < 30:
                    self.on_ceiling = False
                    actions.VarChangeAction(self.pipe, 0.5, self, "y", self.level.rect.h-self.rect.h, blocking=False, blockable=False, force=False)

            result = self.move_towards(g.player.x, self.y)


            if result == g.player:
                self.attacking = True
                actions.FuncCallAction(self.pipe, self.attack_time, self, "attack", change_type=1, blocking=False, blockable=False)

    def draw(self):
        if self.on_ceiling:
            self.flip_v = True
        else:
            self.flip_v = False

        super().draw()

class RecoverEnemy(Enemy):
    """
    Melee enemy which cannot dies
    """
    def __init__(self, x, y, level):
        rect = p.Rect(x, y, 16, 32)
        super().__init__(rect, level, "recover_enemy", max_health=3, respawn_time=20)

    def update_ai(self):
        super().update_ai()

        if not self.stunned and not self.attacking:
            result = self.move_towards(g.player.x, g.player.y)
            if result == g.player:
                self.attacking = True
                actions.FuncCallAction(self.pipe, self.attack_time, self, "attack", change_type=1, blocking=False, blockable=False)


class LargeEnemy(Enemy):
    """
    Large melee enemy
    """
    def __init__(self, x, y, level):
        rect = p.Rect(x, y, 48, 48)
        super().__init__(rect, level, "large_enemy", max_health=50, speed=10, damage=5, collision_dict={"class_Enemy":False, "class_Player":False})
        self.regen = 0.2
        self.direction = "left"

    def update(self):
        super().update()
        self.change_health(self.regen * g.dt)

    def update_inactive(self):
        super().update_inactive()

        #move
        result = None
        if self.direction == "left":
            result = self.move(-self.speed * g.dt, 0)
        elif self.direction == "right":
            result = self.move(self.speed * g.dt, 0)

        #switch
        if result:
            if self.direction == "left":
                self.direction = "right"
            elif self.direction == "right":
                self.direction = "left"

        self.update_rect()


    def update_ai(self):
        super().update_ai()

        if not self.stunned:
            #move
            result = None
            if self.direction == "left":
                result = self.move(-self.speed * g.dt, 0)
            elif self.direction == "right":
                result = self.move(self.speed * g.dt, 0)

            if abs(g.player.rect.centerx-self.rect.centerx) <= (g.player.rect.w/2)+(self.rect.w/2):
                if (self.direction == "left" and g.player.rect.centerx < self.rect.centerx) or (self.direction == "right" and g.player.rect.centerx > self.rect.centerx):
                    if not self.attacking:
                        self.attacking = True
                        actions.FuncCallAction(self.pipe, self.attack_time, self, "attack", change_type=1, blocking=False, blockable=False)

            #switch
            if result:
                if self.direction == "left":
                    self.direction = "right"
                elif self.direction == "right":
                    self.direction = "left"
                

def spawn_enemy(name, x, y, level):
    """
    Spawn an enemy at a given level and location
    """
    eval_string = f"{name}({x}, {y}, level)"
    new_enemy = eval(eval_string)
    return new_enemy