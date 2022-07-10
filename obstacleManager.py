import pygame
import os
import random
import numpy as np
from obstacle import *

class ObstacleManager:

	def __init__(self, screen, WIDTH, HEIGHT):
		self.obstacle_list = []
		self.coin_list = []
		self.snorkle_list = []
		self.screen = screen
		self.screen_width = WIDTH
		self.screen_height = HEIGHT
		self.hit = False
		self.spawn_list = []
		self.spawn_prob = [0, 0, 1]#[0.4, 0.3, 0.3]
		self.obstacle_hit = pygame.image.load('Assets\\Obstacle\\obstacle_1_hit_sprites.png').convert_alpha()
		self.obstacle_bounced = pygame.image.load('Assets\\Obstacle\\obstacle_1_bounced_sprites.png').convert_alpha()
		self.obstacle_swim = pygame.image.load('Assets\\Obstacle\\obstacle_1_swimming_sprites.png').convert_alpha()
		self.obstacle_sheets = {'SWIMMING':self.obstacle_swim, 'HIT':self.obstacle_hit, 'BOUNCED':self.obstacle_bounced, 'DEAD':self.obstacle_hit}
	def update(self, surface):

		for obstacle in self.obstacle_list:
			obstacle.frame += 1
			obstacle.update()
			if obstacle.get_end_screen() or obstacle.state == 'DEAD':
				self.obstacle_list.remove(obstacle)
		for coin in self.coin_list:
			coin.update()
			if coin.get_end_screen():
				self.coin_list.remove(coin)

		for snorkle in self.snorkle_list:
			remove = snorkle.update()

			if snorkle.get_end_screen():
				self.snorkle_list.remove(snorkle)
			if remove:
				self.snorkle_list.remove(snorkle)
			
	def render(self, surface):
		self.render_obstacles(surface)
		self.render_coins(surface)
		self.render_snorkle(surface)

	def add_obstacle(self):
		obx = random.randint(0,350)
		return Obstacle(obx, 820 + (random.randint(-20,20)))

	def add_coin(self):
		obx = random.randint(25, 350)
		return Coin(obx, 820 + (random.randint(-20,20)))

	def add_snorkle(self):
		obx = random.randint(50, 300)
		return Snorkle(obx, 820 + (random.randint(-20,20)))

	def render_obstacles(self, surface):
		for obstacle in self.obstacle_list:
			surface.blit(self.get_obs_sprite(obstacle), obstacle.rect)


	def render_coins(self, surface):
		for coin in self.coin_list:
			surface.blit(coin.img, coin.rect)

	def render_snorkle(self, surface):
		for snorkle in self.snorkle_list:
			surface.blit(snorkle.images[snorkle.state], snorkle.rect)

	def spawn_obstacle(self, num, event, timer):


		self.spawn_list = [self.add_obstacle(), self.add_coin()]
		num_ob = 0
		while len(self.spawn_list) < num:
			works = True
			match np.random.choice(3, 1, p=self.spawn_prob):
				case 0: #ADDING AN OBSTACLE
					thing = self.add_obstacle()
					num_ob += 1
				case 1:
					thing = self.add_coin()
				case 2:
					thing = self.add_snorkle()

			for item in self.spawn_list:
				if pygame.Rect.colliderect(item.rect, thing.rect):
					works = False

			if works:
				self.spawn_list.append(thing)
			#print("WORK")
		for guy in self.spawn_list:
			if guy.type == 'Obstacle':
				self.obstacle_list.append(guy)
			elif guy.type == 'Coin':
				self.coin_list.append(guy)
			elif guy.type == 'Snorkle':
				self.snorkle_list.append(guy)
			

		pygame.time.set_timer(event, timer, 1)

	def get_obstacles(self):
		return self.obstacle_list

	def get_coins(self):
		return self.coin_list

	def get_snorkle(self):
		return self.snorkle_list

	def reset(self):
		self.obstacle_list = []
		self.coin_list = []
		self.snorkle_list = []

	def get_obs_sprite(self, obs):

		surf = pygame.Surface((128, 128)).convert_alpha()

		temp = obs.frame//4
		surf.blit(self.obstacle_sheets[obs.state], (0,0), ((obs.preset * self.obstacle_sheets[obs.state].get_width()/2) + (temp * 128),0, (obs.preset * self.obstacle_sheets[obs.state].get_width()/2) + ((1+temp) * 128),128))
		surf = pygame.transform.scale(surf, (obs.OBSTACLE_WITDH, obs.OBSTACLE_HEIGHT))
		surf.set_colorkey((0,0,0))

		return surf


