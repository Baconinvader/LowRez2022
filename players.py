import global_values as g
import graphics as gfx
import utilities as util
import creatures
import particles
import items
import actions
import sounds

import pygame as p
import math as m

class Inventory:
    """
    Class for storing player inventory items
    """
    def __init__(self, slots):
        self.slots = [None for slot in range(slots)]
        self.selected_item = None
        self.selected_index = None

        #a way for ammunition to be collected before a gun is picked up
        self.ammunition_reserves = {}

    def add_item(self, item):
        """
        Attempt to add an item to inventory
        """
        #add to existing slot:
        for i,slot in enumerate(self.slots):
            if slot and slot.name == item.name:
                slot.amount += 1
                return True

        #add to new slot
        for i,slot in enumerate(self.slots):
            if not slot:
                self.slots[i] = item
                if isinstance(item, items.Gun):
                    item.change_ammunition(self.ammunition_reserves.get(item.name, 0))
                    self.ammunition_reserves[item.name] = 0

                if not self.selected_item:
                    self.select_index(i)
                return True
        return False

    def check_for_named_item(self, name):
        """
        Attempt to find a named item within the inventory
        Returns the item if it exists, False otherwise
        """
        for slot in self.slots:
            if slot and slot.name == name:
                return slot
        return False

    def select_index(self, index):
        """
        Select an item at an index
        """
        if index is not None and 0 <= index < len(self.slots):
            old_index = self.selected_index

            self.selected_index = index
            self.selected_item = self.slots[self.selected_index]

            if isinstance(self.selected_item, items.Consumable):
                self.selected_item.consume()
                self.remove_index(self.selected_index)
                self.select_index(old_index)

            sounds.play_sound("inventory_select")

            return self.selected_item
        else:
            return None

    def remove_index(self, index):
        """
        Delete an item at an index
        """
        item = self.slots[index]
        if item.amount > 1:
            item.amount -= 1
        else:
            self.slots[index] = None

        if index == self.selected_index:
            self.selected_item = None
            self.selected_index = None

    def remove(self, item):
        """
        Delete an item
        """
        for i, slot in enumerate(self.slots):
            if slot == item:
                self.remove_index(i)

    def clear(self):
        """
        Clear inventory
        """
        for slot in self.slots:
            if slot:
                self.remove(slot)

class Player(creatures.Creature):
    def __init__(self):
        self.target_x = None
        rect = p.Rect(0,32,16,32)

        super().__init__(rect, None, "player", solid=True)
        self.gfx = g.spritesheets[f"{self.name}_ss"].create_animation_system({"static":0, "moving":1, "hurt_static":2, "hurt_move":3}, 0.25)
        self.z_index = 1

        self.collision_dict = {"class_Entity":False, "class_LargeEnemy":False}

        self.speed = 42  # units per second

        self.inventory = Inventory(8)

        #handgun = items.Gun("handgun", self, 1, 0.5, 200)
        #shotgun = items.Gun("shotgun", self, 0.8, 1, 100, projectiles=5, spread=0.5, max_ammunition=25, recharge=0)
        #stungun = items.Gun("stungun", self, 0.0, 1.5, 64, projectiles=1, spread=0, max_ammunition=3, recharge=0.4, stun=5, fire_effect=2)
        #revolver = items.Gun("revolver", self, 5, 1.5, 300, projectiles=1, spread=0, max_ammunition=15)
        
        self.angle = 0
        self.respawn_time = None

        self.arm = gfx.load_image("player_arm", alpha=True)
        self.hand = gfx.load_image("player_hand", alpha=True)
        self.smoke_effect = None
        self.flash_effect = None

        self.control_locks = 0
        self.hurt = 0
        self.fully_dead = False

    def debug_set_inventory(self):
        """
        Debug method for setting up player inventory
        """
        self.inventory.add_item(items.Handgun())
        self.inventory.add_item(items.Shotgun())
        self.inventory.add_item(items.Stungun())
        self.inventory.add_item(items.Revolver())
        self.inventory.select_index(0)

    def set_target_x(self, x):
        """
        Set the point the player tries to walk through
        """
        if x is not None:
            self.target_x = x-(self.rect.w/2)
        else:
            self.target_x = None

    def set_animation(self):
        if self.health < self.max_health/2:
            if self.change_x:
                self.gfx.set_anim("hurt_move")
            else:
                self.gfx.set_anim("hurt_static")

        elif self.change_x:
            self.gfx.set_anim("moving")
        else:
            self.gfx.set_anim("static")

    def update(self):
        super().update()
        if self.target_x is not None:
            result = self.move_towards(self.target_x, self.y, self.speed * g.dt)
            if result:
                self.target_x = None
            if self.x == self.target_x:
                self.target_x = None

        self.angle = util.get_angle(self.rect.centerx, self.rect.centery, g.tmx, g.tmy)

        item = self.inventory.selected_item
        #position arm
        self.shoulder_pos = self.rect.move(0, -4).center
        if item:
            if True:#item.name == "handgun" or item.name == "stungun" or item.name == "revolver" or item.name == "shotgun"
                if g.tmx > self.rect.centerx:
                    self.arm_angle = util.get_angle(self.shoulder_pos[0], self.shoulder_pos[1], g.tmx, g.tmy) + (m.pi/4)
                    self.elbow_angle = self.arm_angle - (m.pi/2)
                else:
                    self.arm_angle = util.get_angle(self.shoulder_pos[0], self.shoulder_pos[1], g.tmx, g.tmy) - (m.pi/4)
                    self.elbow_angle = self.arm_angle + (m.pi/2)

            else:
                self.arm_angle = util.get_angle(self.shoulder_pos[0], self.shoulder_pos[1], g.tmx, g.tmy) + (m.pi/4)
                self.elbow_angle = self.arm_angle - (m.pi/2)
        else:
            if g.tmx > self.rect.centerx:
                self.arm_angle = util.get_angle(self.shoulder_pos[0], self.shoulder_pos[1], g.tmx, g.tmy) + (m.pi/4)
                self.elbow_angle = self.arm_angle - (m.pi*.25)
            else:
                self.arm_angle = util.get_angle(self.shoulder_pos[0], self.shoulder_pos[1], g.tmx, g.tmy) - (m.pi/4)
                self.elbow_angle = self.arm_angle + (m.pi*0.25)

        if item:
            if isinstance(item, items.Gun) and item.recharge:
                item.change_ammunition(item.recharge * g.dt)
                

        #split_size = (m.pi*2/8)
        #self.arm_angle = arm_angle - ( arm_angle % split_size)

    def attack(self):
        item = self.inventory.selected_item
        if isinstance(item, items.Gun) and not g.elements.get("class_Popup", False):
            res = item.attempt_fire()

            #show effect
            if res:
                if item.fire_effect == 1:
                    self.smoke_effect = particles.create_smoke(self.level, (0,0))
                    self.flash_effect = particles.create_flash(self.level, (0,0), self.angle)

                elif item.fire_effect == 2:
                    self.flash_effect = particles.create_stun_flash(self.level, (0,0), self.angle)

                #recoil
                recoil_magnitude = min(item.damage*item.projectiles, 4)
                if self.direction == "left":
                    self.move(recoil_magnitude, 0)
                    self.direction = "left"
                elif self.direction == "right":
                    self.move(-recoil_magnitude, 0)
                    self.direction = "right"

    def get_direction_for_rendering(self):
        # player should always appear to face the mouse, regardless of their true direction.
        return "right" if g.tmx > self.rect.centerx else "left"

    def take_damage(self, amount):
        if self.health:
            super().take_damage(amount)
            overlay_strength = min(96*amount, 255)
            
            actions.OverlayAction(self.pipe, 1, g.colour_remaps["red"], fade_type=1, full_alpha=overlay_strength, blockable=False, blocking=False)

            #self.hurt += 1
            #actions.VarChangeAction(self.pipe, 1, self, "hurt", self.hurt-1, change_type=2, revert=False, blocking=False, blockable=False, force=False)

    def die(self):
        self.visible_override = False
        timer = 1
        actions.OverlayAction(self.pipe, timer, g.colour_remaps["darkred"], blocking=False, blockable=False)
        actions.FuncCallAction(self.pipe, timer, self, "set_gameover", change_type=1, blocking=False, blockable=False)
        g.player.control_locks += 1
        creatures.Corpse(self, self.x, self.y, self.level)
        

    def set_gameover(self):
        """
        Actually end the game after player death
        """
        self.fully_dead = True
        

    def draw(self):
        super().draw()

        #arm
        g.camera.draw_rotated_gfx(self.arm, self.arm_angle, self.shoulder_pos, ox=0, oy=0.5)

        
        #hand
        elbow_x = self.shoulder_pos[0] + m.cos(self.arm_angle)*self.arm.get_width()
        elbow_y = self.shoulder_pos[1] + m.sin(self.arm_angle)*self.arm.get_width()
        g.camera.draw_rotated_gfx(self.hand, self.elbow_angle, (elbow_x,elbow_y), ox=0, oy=0.5, yflip=g.tmx > self.rect.centerx)

        #weapon
        hand_x = elbow_x + m.cos(self.elbow_angle)*self.hand.get_width()
        hand_y = elbow_y + m.sin(self.elbow_angle)*self.hand.get_width()
        
        if self.inventory.selected_item:
            if g.tmx > self.rect.centerx:
                item_surf = p.transform.flip(self.inventory.selected_item.surface, False, True)
                item_angle = self.arm_angle  - (m.pi/4)
            else:
                item_surf = p.transform.flip(self.inventory.selected_item.surface, False, True)
                item_angle = self.arm_angle + (m.pi/4)
    
            g.camera.draw_rotated_gfx(item_surf, item_angle, (hand_x, hand_y), ox=0.5, oy=0.5, yflip=g.tmx > self.rect.centerx)

            #weapon end
            weapon_x = hand_x + m.cos(item_angle)*(item_surf.get_width()/2)
            weapon_y = hand_y + m.sin(item_angle)*(item_surf.get_width()/2)
            if self.smoke_effect and not self.smoke_effect.x and not self.smoke_effect.y:
                self.smoke_effect.x = weapon_x
                self.smoke_effect.y = weapon_y-2

            if self.flash_effect and not self.flash_effect.x and not self.flash_effect.y:
                self.flash_effect.x = weapon_x
                self.flash_effect.y = weapon_y-2
    


