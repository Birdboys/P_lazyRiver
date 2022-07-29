import pygame
import os
import random

class Obstacle:

	OBSTACLE_WIDTH = 80
	OBSTACLE_HEIGHT = 80 
	def __init__(self, x, y):
		self.rect = pygame.Rect(x, y, Obstacle.OBSTACLE_WIDTH, Obstacle.OBSTACLE_HEIGHT)
		self.type = 'Obstacle'
		self.vel_x = 0
		self.vel_y = -4 + random.randint(-1,1)
		self.state = 'SWIMMING'
		self.preset = random.randint(0,2)
		self.frame = 0
		self.hit_timer = 0
		self.bounced_timer = 0

	"""def render(self, screen):
		screen.blit(self.img, self.rect)"""

	def update(self, delta):

		match self.state:
			case 'SWIMMING':
				self.rect.x += self.vel_x * delta * 60
				self.rect.y += self.vel_y * delta * 60
				self.frame = 0

			case 'HIT':
				if self.preset == 2:
					self.frame = self.frame % (4 * 4)
				else:
					self.frame = self.frame % (8 * 4)
				self.rect.x += self.vel_x * delta * 60 
				self.rect.y += self.vel_y * delta * 60
				if pygame.time.get_ticks()-self.hit_timer > 1000:
					self.state = 'DEAD'

			case 'BOUNCED':
				self.frame = self.frame % (4 * 4)
				self.rect.x += int(self.vel_x * 0.75) * delta * 60
				self.rect.y += int(self.vel_y * 0.75) * delta * 60

				if pygame.time.get_ticks()-self.bounced_timer > 5000:
					self.state = 'SWIMMING'


			case _:
				pass
		self.edge_check()

	def get_end_screen(self):

		if self.rect.y <= -Obstacle.OBSTACLE_HEIGHT:
			return True
		else:
			return False

	def get_player_collision(self, p_rect):
		if pygame.Rect.colliderect(self.rect, p_rect):
			return True
		else:
			return False

	def hit(self):
		self.state = 'HIT'
		self.hit_timer = pygame.time.get_ticks()

	def bouncy(self):
		if self.state == 'BOUNCED':
			self.state = 'HIT'
			self.hit_timer = pygame.time.get_ticks()
		else:
			self.state = 'BOUNCED'
			self.bounced_timer = pygame.time.get_ticks()

	def edge_check(self):
		if self.rect.x < 0 + 10:
			self.vel_x = -self.vel_x
			self.rect.x = 10
		elif self.rect.x + self.rect.width > 400 - 10:
			self.vel_x = -self.vel_x
			self.rect.x = 400 - 10 - self.rect.width


class Coin(Obstacle):

	COIN_WIDTH = 50
	COIN_HEIGHT = 50

	def __init__(self, x, y):
		self.rect = pygame.Rect(x, y, Coin.COIN_WIDTH, Coin.COIN_HEIGHT)
		self.type = 'Coin'
		self.vel_x = 0
		self.vel_y = -5 + random.randint(-1,1)
		self.frame = random.randint(0,40)
		self.val = self.get_val()

	def update(self, delta):
		self.frame = self.frame % (10*4)
		self.rect.x += self.vel_x * delta * 60
		self.rect.y += self.vel_y * delta * 60

	def get_end_screen(self):

		if self.rect.y <= -Coin.COIN_HEIGHT:
			return True
		else:
			return False

	def get_val(self):
		if random.uniform(0,1) <= 0.1:
			return 5
		else:
			return 1

class Snorkle(Obstacle):
	
	SNORKLE_WIDTH = 80
	SNORKLE_HEIGHT = 80

	def __init__(self, x, y):
	
		self.rect = pygame.Rect(x, y, Snorkle.SNORKLE_WIDTH, Snorkle.SNORKLE_HEIGHT)
		self.vel_y = -4 + random.randint(-1,1)
		self.vel_x = 0
		self.state = 'SWIMMING'
		self.activate_timer = 0
		self.used = False
		self.type = 'Snorkle'
		self.frame = 0

	def update(self, delta):

		if self.state == 'SWIMMING':
			self.rect.x += self.vel_x * delta * 60
			self.rect.y += self.vel_y * delta * 60
			self.frame = self.frame % (7 * 4)

		if self.state == 'ACTIVATED':
			self.frame = self.frame % (16 * 4)
			if (pygame.time.get_ticks()-self.activate_timer)/1000 >= 2:
				self.state = 'SWIMMING'
			self.rect.x += self.vel_x / 4 * delta * 60
			self.rect.y += self.vel_y / 4 * delta * 60


		if self.state == 'STOMPED':
			if self.frame > 95:
				self.state = 'GONE'
				self.used = True

		if self.state == 'GONE':
			#print('IM GOING OH NO')
			self.rect.x += int(self.vel_x*0.75)
			self.rect.y += int(self.vel_y*0.75) 
			


	def get_end_screen(self):

		if self.rect.y <= -Snorkle.SNORKLE_HEIGHT:
			return True
		else:
			return False

	def activated(self):
		self.state = 'ACTIVATED'
		self.activate_timer = pygame.time.get_ticks()
		self.used = 'True'

	def stomp(self):
		self.state = 'STOMPED'
		self.frame = 0
		self.activate_timer = pygame.time.get_ticks()

