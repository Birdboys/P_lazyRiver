import pygame
import numpy as np
import os
import random

class BackgroundManager():

	def __init__(self, game):
		self.game = game
		self.left_img = pygame.transform.scale(pygame.image.load('Assets\\Background\\pool_side.png').convert_alpha(), (16,64))
		self.right_img = pygame.transform.flip(self.left_img, True, False)
		self.left_shore = [ShorePiece(self.left_img, 0, 0)]
		self.right_shore = [ShorePiece(self.left_img, self.game.WIDTH-32, 0)]
		self.water_effects = []


	def update(self):

		#self.make_water_effect()
		for effect in self.water_effects:
			if effect.reached_end():
				self.water_effects.remove(effect)

		for thing in self.left_shore + self.right_shore:
			thing.update()

		left_boy = self.left_shore[-1]
		if left_boy.img_rect.y + left_boy.img_rect.height < self.game.HEIGHT:
			self.left_shore.append(ShorePiece(self.left_img, 0, left_boy.img_rect.y + left_boy.img_rect.height))

		right_boy = self.right_shore[-1]
		if right_boy.img_rect.y + right_boy.img_rect.height < self.game.HEIGHT:
			self.right_shore.append(ShorePiece(self.right_img, self.game.WIDTH - right_boy.img_rect.width, right_boy.img_rect.y + right_boy.img_rect.height))

	def render(self, surface):

		for thing in self.left_shore + self.right_shore:
			thing.render(surface)

		




	def fill_shores(self):
		pass
		#for x in range(5):
			#self.left_shore.append()

	"""def make_water_effect(self):
		for x in range(0,3):
			coord = random.randint(5,750)
			self.water_effects.append(WaterBoy(coord, self.game.HEIGHT))"""



class ShorePiece():

	vel = -3
	def __init__(self, img, x, y):
		self.img = img
		self.img_rect = self.img.get_rect()
		self.img_rect.x = x
		self.img_rect.y = y

	def render(self, surface):
		surface.blit(self.img, self.img_rect)

	def update(self):
		self.img_rect.y += ShorePiece.vel
"""
class WaterBoy():

	def __init__(self, x, y):
		self.vel = 0
		self.img = self.get_type()
		self.rect = self.img.get_rect()
		self.rect.x, self.rect.y = x,y

	def update(self):
		self.rect.y += self.vel

	def render(self, surface):
		surface.blit(self.img, self.rect)


	def get_type(self):

		t = random.randint(0,2)
		match t:
			case 0:
				surf = pygame.Surface((6, 20))
				surf.fill((0,153,219))
				self.vel = -8
			case 1:
				surf = pygame.Surface((4, 20))
				surf.fill((44,232,245))
				self.vel = -12
			case 2:
				print('bippy')
				surf = pygame.Surface((1000, 20))
				surf.fill((255,255,255))
				self.vel = -1
		return surf

	def reached_end(self):

		if self.rect.y+self.rect.height <= 0:
			return True
		else:
			return False 
"""
