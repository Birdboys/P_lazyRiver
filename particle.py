import pygame
import numpy as np
import os
import random

class Particle():

	#gravity = -0.2
	power = 2
	def __init__(self, x, y, vel_x, vel_y, color,radius = 8, gravity=0):
		self.x = x
		self.y = y
		self.vel_x = Particle.power * vel_x
		self.vel_y = Particle.power * vel_y
		self.radius = radius
		self.gravity = gravity
		self.color = color

	def update(self):
		self.radius -= 0.1
		self.x += self.vel_x
		self.y += self.vel_y + self.gravity

	def render(self, surface):
		pygame.draw.circle(surface, self.color, (self.x,self.y), self.radius)