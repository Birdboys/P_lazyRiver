import pygame
import numpy as np
import os
from particle import Particle
import random 

class ShadowManager():
	def __init__(self, game):
		self.game = game
		self.shadow = pygame.image.load("Assets\\shadow.png").convert_alpha()

	def render(self, surface):
		for obstacle in self.game.obsManager.obstacle_list: 
			surface.blit(pygame.transform.scale(self.shadow, (obstacle.rect.width, obstacle.rect.height)), self.shift_rect(obstacle.rect, 7))

		for coin in self.game.obsManager.coin_list: 
			surface.blit(pygame.transform.scale(self.shadow, (coin.rect.width, coin.rect.height)), self.shift_rect(coin.rect, 5))

		#for snorkle in self.game.obsManager.snorkle_list: 
			#surface.blit(pygame.transform.scale(self.shadow, (snorkle.rect.width, snorkle.rect.height)), snorkle.rect) 

	def shift_rect(self, rect, shift):
		new_rect = rect.copy()
		new_rect.x = new_rect.x - shift 
		new_rect.y = new_rect.y - shift * 1.25
		return new_rect
	
	def render_player(self, surface):
		surface.blit(pygame.transform.scale(self.shadow,  self.game.player.dooby), self.shift_rect(self.game.player.rect, 7))

	def render_shadow(self, surface, rect):
		new_rect = self.shift_rect(rect, 7)
		surface.blit(pygame.transform.scale(self.shadow, (rect.width, rect.height)), new_rect)