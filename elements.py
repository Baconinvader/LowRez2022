import pygame as p
import inspect

import global_values as g
import graphics as gfx
import actions

class Element:
    """
    Base class for all game objects
    """
    def __init__(self, rect, z_index=0):
        self.rect = rect
        self.set_from_rect()
        self.z_index = z_index

        self.class_names = []

        self.deleted = False

        #add to lists of game elements
        for base_class in inspect.getmro(self.__class__):
            name = "class_"+base_class.__name__
            self.class_names.append(name)

            if g.elements.get(name, False):
                g.elements[name].append(self)
            else:
                g.elements[name] = [self]
    
        pipe_name = self.__class__.__name__+str(g.element_id_number)
        self.pipe = actions.Pipe(pipe_name)
        g.element_id_number += 1

        g.element_list.append(self)

    def set_from_rect(self):
        """
        Update this rectangle's position from their rectangular position
        """
        self.x = self.rect.x
        self.y = self.rect.y

    def update_rect(self):
        """
        Update's this element's rect based on it's position
        """
        self.rect.x = self.x
        self.rect.y = self.y

    def update(self):
        """
        Update this element
        """
        self.update_rect()

    def draw(self):
        g.camera.draw_rect("green", self.rect, 1)

    def delete(self):
        if not self.deleted:
            self.deleted = True
            self.pipe.delete()
            for class_name in self.class_names:
                g.elements[class_name].remove(self)
            g.element_list.remove(self)

    def __getstate__(self):
        print("ELEMENT")
        state = gfx.pickle_state(self.__dict__)
        return state
    
    def __setstate__(self, state):
        self.__dict__ = gfx.unpickle_state(state)

    