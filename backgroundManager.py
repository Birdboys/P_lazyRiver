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
		self.right_shore = [ShorePiece(self.left_img, self.game.WIDTH-16, 0)]
		self.water_effects = []


	def update(self):

		self.make_water_effect()
		for effect in self.water_effects:
			effect.update()
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

		for thing in self.water_effects:
			thing.render(surface)

		




	def fill_shores(self):
		pass
		#for x in range(5):
			#self.left_shore.append()

	def make_water_effect(self):
		coord = random.randint(5,750)
		self.water_effects.append(WaterBoy(coord, self.game.HEIGHT))



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

class WaterBoy():

	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.get_type()

	def update(self):
		self.y += self.vel * 2

	def render(self, surface):
		pygame.draw.rect(surface, self.color, pygame.Rect(self.x, self.y, self.width, self.height))


	def get_type(self):

		t = random.randint(0,2)
		match t:
			case 0:
				self.color = (18,78,137)
				self.vel = -1
			case 1:
				self.color = (44,232,245)
				self.vel = -2
			case 2:
				self.color = (255,255,255)
				self.vel = -3
		self.width = (t+1)
		self.height = 10*(t+1)


	def reached_end(self):

		if self.y+self.height <= 0:
			return True
		else:
			return False 

