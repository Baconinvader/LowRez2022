import global_values as g
import graphics as gfx
import creatures
import entities
import controls
import actions
import items

import pygame as p
import os
import json

class Level:
    def __init__(self, name):
        path = os.path.join(g.LEVELS_DIR, name)
        print(path+".png")
        self.level_image = gfx.load_image(name, path=g.LEVELS_DIR)
        self.level_image_render_offset = (0, 3)
        self.rect = p.Rect(0, 0, self.level_image.get_width(), self.level_image.get_height() )

        with open(path+".json") as level_file:
            self.level_dat = json.loads(level_file.read())

        self.name = self.level_dat["name"]
        self.world_x, self.world_y = self.level_dat["position"]
        self.show_space = self.level_dat["show_space"]

        self.structures = []
        self.entities = []

        for structure_dat in self.level_dat["structures"]:
            structure_class, *args = structure_dat
            if args[0] is not None and args[0] < 0:
                args[0] = self.rect.w+args[0]
            if args[1] is not None and args[1] < 0:
                args[1] = self.rect.h+args[1]
            args.insert(0, self)

            eval_string =f"{structure_class}(*args)"
            new_structure = eval(eval_string)
            

        g.levels[self.name] = self

    def linkup(self):
        """
        Link this level to all the other levels
        """
        for structure in self.structures:
            if isinstance(structure, Door):
                if type(structure.change_level) == str:
                    structure.change_level = g.levels[structure.change_level]

                if structure.create_exit:
                    structure.create_exit_door()

    def draw(self):
        x = self.rect.x + self.level_image_render_offset[0]
        y = self.rect.y = self.level_image_render_offset[1]
        g.camera.draw_gfx(self.level_image, (x, y))

    def __getstate__(self):
        print("LEVEL")
        return gfx.pickle_state(self.__dict__)

    def __setstate__(self, state):
        self.__dict__ = gfx.unpickle_state(state)

def change_level(new_level):
    if g.current_level:
        for entity in g.current_level.entities:
            entity.level_left()

    g.current_level = new_level
    g.player.set_level(new_level)

    if g.current_level:
        for entity in g.current_level.entities:
            entity.level_entered()

    x = g.screen_rect.centerx
    y = 8
    actions.TextEffectAction(g.global_pipe, 1, "font1_1", new_level.name, (x,y))

class Structure(entities.Entity):
    def __init__(self, level, rect, structure_gfx, solid=False, interaction_enabled=True):
        super().__init__(rect, level, solid=solid)
        self.gfx = structure_gfx

        self.interaction_enabled = interaction_enabled
        self.can_interact = False
        self.level.structures.append(self)
        
    def update(self):
        super().update()
        diff = abs(self.rect.centerx - g.player.rect.centerx)
        if self.interaction_enabled:
            if diff <= (self.rect.w/2)+16:
                self.can_interact = True
            else:
                self.can_interact = False
        else:
            self.can_interact = False

    def draw(self):
        g.camera.draw_gfx(self.gfx, self.rect.topleft)

        if self.can_interact:
            icon_name = "interact_icon" if self.rect.width % 2 == 1 else "interact_icon_large"
            icon_surf = gfx.get_surface(icon_name)
            icon_x = self.rect.centerx - icon_surf.get_width() // 2
            icon_y = self.rect.y - icon_surf.get_height() - 3
            g.camera.draw_gfx(icon_name, (icon_x, icon_y))

class Pickup(Structure):
    """
    Structure of an item that can be picked up
    """
    def __init__(self, level, x, y, item, width=-1, height=-1):
        self.item = item
        if type(self.item) == str:
            self.item = items.create_item(self.item)
        if width == -1:
            width = self.item.surface.get_width() if self.item.surface is not None else 8
        if height == -1:
            height = self.item.surface.get_height() if self.item.surface is not None else 8
        if y is None:
            y = level.rect.height - height  # None means "on floor"
        rect = p.Rect(x, y, width, height)

        super().__init__(level, rect, self.item.surface)

    def draw(self):
        super().draw()
        # disabling this because I don't like it -Ghast
        # if self.interaction_enabled:
        #    outline_rect = self.rect.inflate(2,2)
        #    g.camera.draw_rect("green", outline_rect, 1)

    def interact(self):
        controls.Item_Popup(self.item, pickup=self)

class LockedPickup(Pickup):
    """
    Base structure of an item that can be picked up, but is locked
    """
    def __init__(self, level, x, y, item, pickup_gfx):
        pickup_gfx = gfx.get_surface(pickup_gfx)

        super().__init__(level, x, y, item, width=pickup_gfx.get_width(), height=pickup_gfx.get_height())
        self.gfx = pickup_gfx

        self.locked = True

    def interact(self):
        super().interact()

    def unlock(self):
        self.locked = False

class KeyPickup(LockedPickup):
    """
    Structure of an item that can be pickup up, but required a key
    """

    def __init__(self, level, x, y, item, pickup_gfx, key_name):
        self.key_name = key_name
        super().__init__(level, x, y, item, pickup_gfx)

    def interact(self):
        if self.locked:
            res = g.player.inventory.check_for_named_item(self.key_name)
            rect = p.Rect(0, 0, 56, 32)
            rect.center = g.screen_rect.center
            if res:
                g.player.inventory.remove(res)

                controls.Popup(rect, "Used", self.key_name, None, set(("main",)), show_accept=False, background_gfx="popup_success_background")
                self.unlock()
            else:
                controls.Popup(rect, "You need", self.key_name, None, set(("main",)), show_accept=False, background_gfx="popup_failure_background")

        elif not self.locked:
            controls.Item_Popup(self.item, pickup=self, delete_pickup=False)

    

class Door(Structure):
    def __init__(self, level, x, y, change_level, create_exit=True):
        if x is None:
            x = 0
            self.auto_place = True
        else:
            self.auto_place = False

        rect = p.Rect(x, y, 16, 32)
        self.open_anim = g.spritesheets["structure_16_32_ss"].create_animation(0, 0.25, repeat=False)
        self.closed_surface = g.spritesheets["structure_16_32_ss"].anims[0][0]

        self.state = "closed"
        
        self.change_level = change_level
        #self.change_pos = change_pos
        self.create_exit = create_exit

        super().__init__(level, rect, self.closed_surface)

    def interact(self):
        print(">",self.state,":",self.change_level.name,"(",self.level.name,")")
        if self.state == "closed":
            self.open()

    def open(self):
        self.state = "open"
        self.open_anim.reset()
        self.gfx = self.open_anim
        actions.OverlayAction(g.global_pipe, 1, (0,0,0))
        actions.LevelChangeAction(g.global_pipe, self.change_level, door=self)
        actions.VarChangeAction(g.global_pipe, 0, g.player, "x", self.change_pos[0], change_type=1)

    def close(self):
        print("closing ",self,">",self.change_level.name,"(",self.level.name,")")
        self.state = "closed"
        self.open_anim.reset()
        self.gfx = self.closed_surface

    def level_entered(self):
        super().level_entered()
        self.close()

    def create_exit_door(self):
        """
        Create exit door
        """
        #automatically place this door based on it's connection
        if self.auto_place:
            #same y, different x
            if self.change_level.world_y == self.level.world_y:
                if self.change_level.world_x > self.level.world_x:
                    self.x = self.level.rect.w-self.rect.w
                else:
                    self.x = 0
            else:
                #different y, maybe different x
                self.x = (self.change_level.world_x - self.level.world_x)*64
                self.x += 32
                if self.change_level.world_y < self.level.world_y:
                    self.x -= (self.rect.w/2)
                else:
                    self.x += (self.rect.w/2)


        if self.change_level.world_y == self.level.world_y:
            #same y, different x
            if self.change_level.world_x < self.level.world_x:
                #left
                x = self.change_level.rect.w - self.rect.w
            else:
                #right
                x = 0
        else:
            #different y, maybe different x
            x = ( (self.level.world_x*64) + self.x) - (self.change_level.world_x*64)
            
        if type(self) == Door:
            self.exit_door = Door(self.change_level, x, self.y, self.level, create_exit=False)
        elif type(self) == KeyDoor:
            self.exit_door = KeyDoor(self.change_level, x, self.y, self.level, self.key_name, create_exit=False)
        elif type(self) == KeypadDoor:
            self.exit_door = KeypadDoor(self.change_level, x, self.y, self.level, self.key_string, create_exit=False)

        self.exit_door.exit_door = self

        self.change_pos = (x, self.exit_door.y)
        self.exit_door.change_pos = (self.x, self.y)

class LockedDoor(Door):
    """
    Base class for doors that are locked for whatever reason
    """
    def __init__(self, level, x, y, change_level, create_exit=True):
        super().__init__(level, x, y, change_level, create_exit=create_exit)
        self.state = "locked"

    def attempt_unlock(self, value=None):
        """
        Check if we can unlock door
        """
        pass

    def unlock(self, item=None):
        self.state = "closed"
        self.exit_door.state = "closed"
        if item:
            g.player.inventory.remove(item)

    def interact(self):
        if self.state == "locked":
            self.attempt_unlock()

        elif self.state == "closed":
            self.open()

    def close(self):
        if not self.state == "locked":
            super().close()

class KeyDoor(LockedDoor):
    def __init__(self, level, x, y, change_level, key_name, create_exit=True):
        super().__init__(level, x, y, change_level, create_exit=create_exit)
        self.key_name = key_name

    def attempt_unlock(self, value=None):
        res = g.player.inventory.check_for_named_item(self.key_name)
        rect = p.Rect(0, 0, 56, 32)
        rect.center = g.screen_rect.center
        if res:
            controls.Popup(rect, "Used", self.key_name, None, set(("main",)), show_accept=False, background_gfx="popup_success_background")
            self.unlock(item=res)  
        else:
            controls.Popup(rect, "You need", self.key_name, None, set(("main",)), show_accept=False, background_gfx="popup_failure_background")

class KeypadDoor(LockedDoor):
    def __init__(self, level, x, y, change_level, key_string, create_exit=True):
        super().__init__(level, x, y, change_level, create_exit=create_exit)
        self.key_string = key_string

    def interact(self):
        if self.state == "locked":
            controls.Keypad_Popup(self)
        else:
            super().interact()

    def attempt_unlock(self, value=None):
        rect = p.Rect(0, 0, 56, 32)
        rect.center = g.screen_rect.center
        if value == self.key_string or (g.IS_DEV and p.key.get_pressed()[p.K_u]):
            controls.Popup(rect, "Unlocked", "Door", None, set(("main",)), show_accept=False, background_gfx="popup_success_background")
            self.unlock()  
        else:
            controls.Popup(rect, "Incorrect", "Code", None, set(("main",)), show_accept=False, background_gfx="popup_failure_background")

class TextInformation(Structure):
    """
    A structure containing text information which displays when interacted with
    """
    def __init__(self, level, x, y, structure_gfx, font_name, text, background_gfx):
        self.font_name = font_name
        self.text = text
        self.background_gfx = background_gfx

        structure_gfx = gfx.get_surface(structure_gfx)

        w, h = structure_gfx.get_size()
        rect = p.Rect(x, y, w, h)
        super().__init__(level, rect, structure_gfx)
        

    def interact(self):
        controls.TextScreenControl(g.screen_rect.copy(), self.font_name, self.text, set(("main",)), background_gfx=self.background_gfx)


class EnemySpawn(Structure):
    """
    A location at which to spawn an enemy
    """
    def __init__(self, level, x, y, enemy_name):
        rect = p.Rect(0,0,1,1)
        super().__init__(level, rect, None)
        creatures.spawn_enemy(enemy_name, x, y, level)