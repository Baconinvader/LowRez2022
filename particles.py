import global_values as g
import entities

import pygame as p
import math as m
import random as r

class Particles(entities.Entity):
    def __init__(self, level, position, angle, colour, spread, amount, power, timer,
    gravity=1, size=1):
        super().__init__(p.Rect(position[0], position[1], 1, 1), level, solid=False)

        self.position = position
        self.angle = angle
        self.colour = colour
        self.spread = spread
        self.amount = amount
        self.power = power

        self.gravity = gravity
        self.size = size

        self.timer = timer
        self.creation_time = p.time.get_ticks()

        #TODO: do this with numpy
        self.particle_x = []
        self.particle_y = []
        self.particle_vx = []
        self.particle_vy = []

        for _ in range(self.amount):
            angle = self.angle + ((r.random()-0.5)*self.spread)
            power = r.random()*self.power

            vx = m.cos(angle) * power
            vy = m.sin(angle) * power

            self.particle_x.append(0)
            self.particle_y.append(1)
            self.particle_vx.append(vx)
            self.particle_vy.append(vy)

    def update(self):
        for i in range(self.amount):
            self.particle_vx[i] -= self.particle_vx[i]*(1-0.8)*g.dt

            self.particle_vy[i] += 9.8*g.dt*self.gravity
            self.particle_vy[i] -= self.particle_vy[i]*(1-0.8)*g.dt
            
            self.particle_x[i] += self.particle_vx[i]*g.dt
            self.particle_y[i] += self.particle_vy[i]*g.dt

            if (p.time.get_ticks()-self.creation_time)/1000 > self.timer:
                self.delete()
                
    def draw(self):
        for i in range(self.amount):
            if self.size == 1:
                g.camera.set_at( (self.x+self.particle_x[i], self.y+self.particle_y[i]), self.colour) 
            else:
                g.camera.draw_circle(self.colour, (self.x+self.particle_x[i], self.y+self.particle_y[i]), self.size)

def create_blood(level, pos, angle):
    """
    Create blood particle effects at a point
    """
            #level, position, angle, colour, spread, amount, power, timer
    return Particles(level, pos, angle, "red", 1, 10, 10, 10)

def create_smoke(level, pos):
    """
    Create smoke effect particles at a point
    """
            #level, position, angle, colour, spread, amount, power, timer
    return Particles(level, pos, -m.pi/2, "gray", 1, 10, 8, 2, gravity=-0.6, size=1)

def create_flash(level, pos, angle):
    """
    Create muzzle flash effect particles at a point
    """
            #level, position, angle, colour, spread, amount, power, timer
    return Particles(level, pos, angle, "lightyellow", 1, 15, 15, 0.4, gravity=0.5)

def create_stun_flash(level, pos, angle):
    """
    Create muzzle flash effect particles at a point
    """
            #level, position, angle, colour, spread, amount, power, timer
    return Particles(level, pos, angle, "lightblue", 1, 15, 15, 0.2, gravity=0.5)