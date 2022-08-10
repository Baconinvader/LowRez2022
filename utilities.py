import global_values as g
import pygame as p

import math as m

def check_collision(rect, obj=None, mask=None, collision_dict={}, exceptions=[], detail=False):
    """
    Check whether a rect is colliding with an object
    Returns the object if collision occurs, false otherwise
    """
    _collision_dict = {"class_Entity":True, "levels":True}
    _collision_dict.update(collision_dict)
    collision_dict = _collision_dict

    if collision_dict["levels"] and ((obj and rect not in obj.level.rect) or (not obj and rect not in g.current_level.rect)):
        return g.current_level

    if obj:
        for entity in obj.level.entities:
            check_collision = True
            for name in reversed(entity.class_names):
                col_val = collision_dict.get(name, None) 
                if col_val is not None:
                    check_collision = col_val  
            
            if check_collision:
                if entity.solid and entity != obj and entity not in exceptions:
                    if entity.rect.colliderect(rect):
                        if not detail or not mask:
                            return entity
                        else:
                            #more detailed check
                            import graphics as gfx
                            
                            if entity.surface:
                                gfx_mask = gfx.get_mask(entity.surface)
                                #gfx_mask = p.mask.Mask((entity.rect.w, entity.rect.h), fill=True)
                                #print(gfx_mask.count(), mask.count(), (rect.right-entity.rect.right, rect.bottom-entity.rect.bottom))
                                if gfx_mask.overlap(mask, (rect.left-entity.rect.left, rect.top-entity.rect.top)):
                                    return entity


    return False

def interpolate(v1, v2, amount):
    """
    Interpolate between two values
    """
    return v1 + ((v2-v1)*amount)

def get_distance(x1, y1, x2, y2):
    """
    Get distance between two points
    """
    return ( ((x2-x1)**2) + ((y2-y1)**2))**0.5

def get_angle(x1, y1, x2, y2):
    """
    Get angle between two points
    """
    dx = (x2-x1)
    dy = (y2-y1)
    return m.atan2(dy, dx)