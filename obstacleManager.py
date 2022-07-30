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
		self.spawn_prob = [0.6, 0.4]#[0.4, 0.3, 0.3]

		self.obstacle_hit = pygame.image.load('Assets\\Obstacle\\obstacle_1_hit_sprites.png').convert_alpha()
		self.obstacle_bounced = pygame.image.load('Assets\\Obstacle\\obstacle_1_bounced_sprites.png').convert_alpha()
		self.obstacle_swim = pygame.image.load('Assets\\Obstacle\\obstacle_1_swimming_sprites.png').convert_alpha()

		self.obstacle_young_hit = pygame.image.load('Assets\\Obstacle\\obstacle_3_hit_sprites.png').convert_alpha()
		#self.obstacle_young_bounced = pygame.image.load('Assets\\Obstacle\\obstacle_3_bounced_sprites.png').convert_alpha()
		self.obstacle_young_swim = pygame.image.load('Assets\\Obstacle\\obstacle_3_swimming_sprites.png').convert_alpha()

		self.obstacle_sheets = {'SWIMMING':self.obstacle_swim, 'HIT':self.obstacle_hit, 'BOUNCED':self.obstacle_bounced, 'DEAD':self.obstacle_hit}
		self.obstacle_young_sheets = {'SWIMMING':self.obstacle_young_swim, 'HIT':self.obstacle_young_hit, 'BOUNCED':self.obstacle_young_hit, 'DEAD':self.obstacle_young_hit}
		self.snorkle_stomped = pygame.image.load('Assets\\Snorkler\\snorkle_stomped_sprites.png').convert_alpha()
		self.snorkle_activated = pygame.image.load('Assets\\Snorkler\\snorkle_activated_sprites.png').convert_alpha()
		self.snorkle_swim = pygame.image.load('Assets\\Snorkler\\snorkle_swimming_sprites.png').convert_alpha()
		self.snorkle_sheets = {'SWIMMING':self.snorkle_swim, 'ACTIVATED':self.snorkle_activated, 'STOMPED':self.snorkle_stomped}
		self.coin_idle = pygame.image.load('Assets\\Coin\\coin_idle_sprites.png').convert_alpha()
	
	def update(self, surface, delta):

		for obstacle in self.obstacle_list:
			obstacle.frame += 1
			obstacle.update(delta)
			if obstacle.get_end_screen() or obstacle.state == 'DEAD':
				self.obstacle_list.remove(obstacle)

		for coin in self.coin_list:
			coin.frame += 1
			coin.update(delta)
			if coin.get_end_screen():
				self.coin_list.remove(coin)

		for snorkle in self.snorkle_list:
			snorkle.frame += 1
			snorkle.update(delta)

			if snorkle.get_end_screen():
				self.snorkle_list.remove(snorkle)
			if snorkle.state == 'GONE':
				self.snorkle_list.remove(snorkle)
			
	def render(self, surface):
		self.render_obstacles(surface)
		self.render_coins(surface)
		self.render_snorkle(surface)

	def add_obstacle(self):
		obx = random.randint(16,400 - Obstacle.OBSTACLE_WIDTH - 16)
		return Obstacle(obx, 820 + (random.randint(-50,50)), random.randint(0,360))

	def add_coin(self):
		obx = random.randint(16,400 - Coin.COIN_WIDTH - 16)
		return Coin(obx, 820 + (random.randint(-50,50)))

	def add_snorkle(self):
		obx = random.randint(16,400 - Snorkle.SNORKLE_WIDTH - 16)
		return Snorkle(obx, 820 + (random.randint(-50,50)))

	def render_obstacles(self, surface):
		for obstacle in self.obstacle_list:
			surface.blit(self.get_obs_sprite(obstacle), obstacle.rect)


	def render_coins(self, surface):
		for coin in self.coin_list:
			surface.blit(self.get_coin_sprite(coin), coin.rect)

	def render_snorkle(self, surface):
		for snorkle in self.snorkle_list:
			surface.blit(self.get_snork_sprite(snorkle), snorkle.rect)

	def spawn_obstacle(self, num, event, timer):
		self.spawn_list = [self.add_obstacle()]
		num_ob = 0
		while len(self.spawn_list) < num:
			works = True
			match np.random.choice(2, 1, p=self.spawn_prob):
				case 0: #ADDING AN OBSTACLE
					thing = self.add_obstacle()
					num_ob += 1
				case 1:
					thing = self.add_snorkle()
					

			for item in self.spawn_list:
				if pygame.Rect.colliderect(item.rect, thing.rect):
					works = False

			if works:
				self.spawn_list.append(thing)
				
		for guy in self.spawn_list:
			if guy.type == 'Obstacle':
				self.obstacle_list.append(guy)
			else:
				self.snorkle_list.append(guy)
		self.spawn_list = []

		self.spawn_coins(num)
		pygame.time.set_timer(event, timer, 1)

	def spawn_coins(self, num):

		num = num + random.randint(0,10)//10 - 1
		for x in range(num):
			thing = self.add_coin()
			self.coin_list.append(thing)

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
		if obs.preset == 2:
			surf.blit(self.obstacle_young_sheets[obs.state], (0,0), (temp * 128,0,(1+temp) * 128,128))
		else:
			surf.blit(self.obstacle_sheets[obs.state], (0,0), ((obs.preset * self.obstacle_sheets[obs.state].get_width()/2) + (temp * 128),0, (obs.preset * self.obstacle_sheets[obs.state].get_width()/2) + ((1+temp) * 128),128))
		surf = pygame.transform.scale(surf, (obs.OBSTACLE_WIDTH, obs.OBSTACLE_HEIGHT))
		surf.set_colorkey((0,0,0))

		return surf

	def get_snork_sprite(self, snork):

		surf = pygame.Surface((128, 128)).convert_alpha()

		temp = snork.frame//8
		surf.blit(self.snorkle_sheets[snork.state], (0,0), (temp*128, 0, (1+temp) * 128,128))
		surf = pygame.transform.scale(surf, (snork.SNORKLE_WIDTH, snork.SNORKLE_HEIGHT))
		surf.set_colorkey((0,0,0))
		return surf

	def get_coin_sprite(self, coin):
		surf = pygame.Surface((128, 128)).convert_alpha()

		temp = coin.frame > 25
		if coin.val == 5:
			val = 1
		else:
			val = 0
		surf.blit(self.coin_idle, (0,0), (val * self.coin_idle.get_width()/2 + temp*128, 0, val* self.coin_idle.get_width()/2 + (1+temp) * 128,128))
		surf = pygame.transform.scale(surf, (coin.COIN_WIDTH, coin.COIN_HEIGHT))
		surf.set_colorkey((0,0,0))

		return surf

	def rot_center(self, image, angle, x, y):
	    
	    rotated_image = pygame.transform.rotate(image, angle)
	    new_rect = rotated_image.get_rect(center = image.get_rect(center = (x, y)).center)

	    return rotated_image, new_rect


