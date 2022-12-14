import global_values as g
import utilities as util
import graphics as gfx
import levels

import pygame as p

class Pipe:
    """
    Class for holding lists of actions
    """
    def __init__(self, name):
        self.name = name
        self.actions = []

        g.pipes[self.name] = self
        g.pipe_list.append(self)

    def update_action(self, action):
        """
        Update action and return if this action was blocking
        """
        if not action.active:
            action.start()
        action.update()
        return action.blocking


    def update(self):
        ran_action = False
        for action in self.actions:
            if not action.blockable:
                ran_action = self.update_action(action) or ran_action

            else:
                if ran_action:
                    continue
                else:
                    ran_action = self.update_action(action) or ran_action

        #if self.actions:
        #    if not self.actions[0].active:
        #        self.actions[0].start()

        #    self.actions[0].update()

    def add_action(self, action):
        """
        Add a new action to a pipe
        """
        self.actions.append(action)
        action.pipe = self

    def clear_actions(self, finish=False):
        """
        Remove all actions from this pipe
        """
        while self.actions:
            if finish:
                self.actions[0].finish()
            else:
                del self.actions[0]
                

    def delete(self):
        del g.pipes[self.name]
        g.pipe_list.remove(self)

    def draw(self):
        if self.actions:
            self.actions[0].draw()

    def __getstate__(self):
        print("PIPE")
        return gfx.pickle_state(self.__dict__)

    def __setstate__(self, state):
        self.__dict__ = gfx.unpickle_state(state)

class Action:
    """
    Base class for actions
    """
    def __init__(self, pipe, timer, blocking=True, blockable=True):
        self.max_timer = timer
        self.timer = self.max_timer
        self.progress = 0
        self.active = False

        self.blocking = blocking
        self.blockable = blockable

        pipe.add_action(self)

    def start(self):
        """
        Called when the action starts
        """
        self.active = True

    def update(self):
        """
        Called every frame when the action is active
        """
        if self.max_timer:
            self.timer -= g.dt
            self.progress = 1-(max(self.timer,0)/self.max_timer)
            if self.timer <= 0:
                self.finish()
        else:
            self.finish()

    def finish(self):
        """
        Called when an action finished
        """
        self.active = False
        self.pipe.actions.remove(self)

    def draw(self):
        pass

    def __getstate__(self):
        print("ACTION ",self.__class__)
        return gfx.pickle_state(self.__dict__)

    def __setstate__(self, state):
        self.__dict__ = gfx.unpickle_state(state)

class VarChangeAction(Action):
    def __init__(self, pipe, timer, obj, prop, val, change_type=0, revert=False, blocking=True, blockable=True, force=True, min_val=None, max_val=None):
        super().__init__(pipe, timer, blocking=blocking, blockable=blockable)
        self.obj = obj
        self.prop = prop
        self.val = val

        self.min_val = min_val
        self.max_val = max_val

        #can be continuous (0), start (1) or end (2)
        self.change_type = change_type
        #if true, interpolate between start value and end value
        #if false, add change value each frame
        self.force = force

        self.revert = revert

    def start(self):
        super().start()
        self.start_val = getattr(self.obj, self.prop)
        if self.change_type == 1:
            self.set_var(self.val)

        if self.change_type == 0 and not self.force:
            self.changed = 0

        if not self.force:
            self.change = (self.val-self.start_val)/self.timer

    def finish(self):
        super().finish()
        if self.change_type == 0 or self.change_type == 2:
            

            if not self.force and self.change_type == 2:
                current_value = getattr(self.obj, self.prop)
                new_value = current_value + self.change*self.max_timer
                self.set_var(new_value)

            elif self.force or self.change_type == 2:
                self.set_var(self.val)

        if self.revert:
            self.set_var(self.start_val)

    def update(self):
        super().update()
        if self.timer < 0:
            dt = g.dt+self.timer
        else:
            dt = g.dt

        if self.change_type == 0:
            if self.force:
                new_value = util.interpolate(self.start_val, self.val, self.progress)
            else:
                current_value = getattr(self.obj, self.prop)
                new_value = current_value + (self.change*dt)
                
                self.changed = self.changed + (self.change*dt)
                
            self.set_var(new_value)
            

    def set_var(self, val):
        try:
            if self.min_val is not None and val < self.min_val:
                val = self.min_val
            elif self.max_val is not None and val > self.max_val:
                val = self.max_val
        except:
            pass

        setattr(self.obj, self.prop, val)

class FuncCallAction(Action):
    """
    Action for calling a function/subroutine/method
    """
    def __init__(self, pipe, timer, obj, proc, args=[], kwargs={}, change_type=0, blocking=True, blockable=True):
        super().__init__(pipe, timer, blocking=blocking, blockable=blockable)
        self.obj = obj
        self.proc = proc
        self.args = args
        self.kwargs = kwargs

        #can be start (0) or end (1)
        self.change_type = change_type

    def call(self):
        getattr(self.obj, self.proc)(*self.args, **self.kwargs)

    def start(self):
        super().start()
        if self.change_type == 0:
            self.call()

    def finish(self):
        super().finish()
        if self.change_type == 1:
            self.call()

class OverlayAction(Action):
    """
    Action for showing a coloured screen overlay
    """
    def __init__(self, pipe, timer, colour, blocking=True, blockable=True, fade_type=0, full_alpha=255):
        super().__init__(pipe, timer, blocking=blocking, blockable=blockable)

        self.alpha = 0
        self.full_alpha = full_alpha
        self.colour = g.convert_colour(colour)

        #0: get more intense, 1: get lass intense
        self.fade_type = fade_type

        self.surface = p.Surface((g.SCREEN_WIDTH, g.SCREEN_HEIGHT))
        self.surface.fill(self.colour)
    
    def update(self):
        super().update()
        if self.fade_type == 0:
            self.alpha = util.interpolate(0, self.full_alpha, self.progress)
        elif self.fade_type == 1:
            self.alpha = util.interpolate(self.full_alpha, 0, self.progress)

    def draw(self):
        self.surface.set_alpha(self.alpha)
        g.screen.blit(self.surface, (0,0))

class TextEffectAction(Action):
    """
    Action for showing fading text
    """
    def __init__(self, pipe, timer, font, text, pos, blocking=True, blockable=True, colour=g.convert_colour("black")):
        super().__init__(pipe, timer, blocking=blocking, blockable=blockable)

        self.font = font
        self.text = text
        self.pos = pos
        self.colour = colour
        self.alpha = 255

    def update(self):
        super().update()
        self.alpha = util.interpolate(255, 0, self.progress)

    def draw(self):
        gfx.draw_text(self.font, self.text, self.pos, cx=True, cy=False, colour=self.colour, alpha=self.alpha)

class LevelChangeAction(Action):
    """
    Action for changing a level
    """
    def __init__(self, pipe, new_level, door=None, blocking=True, blockable=True):
        if type(new_level) == str:
            new_level = g.levels[new_level]

        self.new_level = new_level
        super().__init__(pipe, 0, blocking=blocking, blockable=blockable)

        self.door = door
        
    def start(self):
        super().start()
        print(f"DEBUG: entering level: {self.new_level.name}")
        levels.change_level(self.new_level)
        g.player.set_target_x(None)

        if self.door:
            g.player.x = self.door.change_pos[0]
            g.player.y = self.door.change_pos[1]


