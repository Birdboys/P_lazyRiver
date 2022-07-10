import pygame
import numpy as np
import os
import random

class Particle():

	def __init__(self, x, y, vel_x, vel_y):
		self.x = x
		self.y = y
		self.vel_x = vel_x
		self.vel_y = vel_y
		self.frame = 0