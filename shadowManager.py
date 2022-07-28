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
			surface.blit(pygame.transform.scale(self.shadow, (obstacle.rect.width, obstacle.rect.height)), obstacle.rect)

		for coin in self.game.obsManager.coin_list: 
			surface.blit(pygame.transform.scale(self.shadow, (coin.rect.width, coin.rect.height)), coin.rect)

		#for snorkle in self.game.obsManager.snorkle_list: 
			#surface.blit(pygame.transform.scale(self.shadow, (snorkle.rect.width, snorkle.rect.height)), snorkle.rect) 

	def render_player(self, surface):
		surface.blit(pygame.transform.scale(self.shadow,  self.game.player.dooby), self.game.player.rect)
