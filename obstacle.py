import pygame
import os
import random

class Obstacle:

	OBSTACLE_WITDH = 80
	OBSTACLE_HEIGHT = 80 
	def __init__(self, x, y):
		self.img = pygame.transform.scale(pygame.image.load('Assets/temp_obstacle.png').convert_alpha(),(Obstacle.OBSTACLE_WITDH, Obstacle.OBSTACLE_HEIGHT))
		self.rect = pygame.Rect(x, y, Obstacle.OBSTACLE_WITDH, Obstacle.OBSTACLE_HEIGHT)
		self.type = 'Obstacle'
		self.vel_x = 0
		self.vel_y = -4 + random.randint(-1,1)
		self.state = 'SWIMMING'
		self.preset = random.randint(0,1)
		self.frame = 0
		self.hit_timer = 0
		self.bounced_timer = 0

	"""def render(self, screen):
		screen.blit(self.img, self.rect)"""

	def update(self):

		match self.state:
			case 'SWIMMING':
				self.rect.x += self.vel_x
				self.rect.y += self.vel_y
				self.frame = 0

			case 'HIT':
				self.frame = self.frame % (8 * 4)

				if pygame.time.get_ticks()-self.hit_timer > 1000:
					self.state = 'DEAD'

			case 'BOUNCED':
				self.frame = self.frame % (4 * 4)
				self.rect.x += int(self.vel_x * 0.75)
				self.rect.y += int(self.vel_y * 0.75)

				if pygame.time.get_ticks()-self.bounced_timer > 5000:
					self.state = 'SWIMMING'


			case _:
				pass

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
			#print("OH FUCK OWY")
			self.state = 'HIT'
			self.hit_timer = pygame.time.get_ticks()
			#print(self.state)
		else:
			self.state = 'BOUNCED'
			self.bounced_timer = pygame.time.get_ticks()


class Noodle(Obstacle):
	NOODLE_WIDTH = 100
	NOODLE_HEIGHT = 25

	def __init__(self, x, y):
		self.img = pygame.transform.scale(pygame.image.load('Assets/temp_noodle.png').convert_alpha(),(Noodle.NOODLE_WIDTH, Noodle.NOODLE_HEIGHT))
		self.rect = pygame.Rect(x, y, Noodle.NOODLE_WIDTH, Noodle.NOODLE_HEIGHT)
		self.left_rect = pygame.Rect(x,y+1, 1, Noodle.NOODLE_HEIGHT-2)
		self.right_rect = pygame.Rect(x+Noodle.NOODLE_WIDTH-1,y+1, 1, Noodle.NOODLE_HEIGHT-2)
		self.top_rect = pygame.Rect(x+5, y, Noodle.NOODLE_WIDTH -6, 1) 
		self.bottom_rect = pygame.Rect(x+5, y+Noodle.NOODLE_HEIGHT-6, Noodle.NOODLE_WIDTH -2, 1) 
		self.rect_list = [self.rect, self.left_rect, self.top_rect, self.right_rect, self.bottom_rect]
		self.type = 'Noodle'
		

	def update(self):
		for rect in self.rect_list:
			rect.y += Obstacle.VEL_Y

	def get_end_screen(self):

		if self.rect.y <= -Noodle.NOODLE_WIDTH:
			return True
		else:
			return False

class Coin(Obstacle):

	COIN_WIDTH = 25
	COIN_HEIGHT = 25

	def __init__(self, x, y):
		self.img = pygame.transform.scale(pygame.image.load('Assets/temp_coin.png').convert_alpha(),(Coin.COIN_WIDTH, Coin.COIN_HEIGHT))
		self.rect = pygame.Rect(x, y, Coin.COIN_WIDTH, Coin.COIN_HEIGHT)
		self.type = 'Coin'
		self.vel_x = 0
		self.vel_y = -5

	def update(self):
		self.rect.x += self.vel_x
		self.rect.y += self.vel_y

	def get_end_screen(self):

		if self.rect.y <= -Coin.COIN_HEIGHT:
			return True
		else:
			return False

class Snorkle(Obstacle):
	
	SNORKLE_WIDTH = 50
	SNORKLE_HEIGHT = 50

	def __init__(self, x, y):
		self.img_swim = pygame.transform.scale(pygame.image.load('Assets/temp_snorkle.png').convert_alpha(),(Snorkle.SNORKLE_WIDTH, Snorkle.SNORKLE_HEIGHT))
		self.img_act = pygame.transform.scale(pygame.image.load('Assets/temp_snorkle_activated.png').convert_alpha(),(Snorkle.SNORKLE_WIDTH, Snorkle.SNORKLE_HEIGHT))
		self.img_stomped = pygame.transform.scale(pygame.image.load('Assets/temp_snorkle_stomped.png').convert_alpha(),(Snorkle.SNORKLE_WIDTH, Snorkle.SNORKLE_HEIGHT))
		self.images = {'SWIMMING':self.img_swim, 'ACTIVATED' : self.img_act, 'STOMPED' : self.img_stomped, 'GONE' : self.img_stomped}
		self.rect = pygame.Rect(x, y, Snorkle.SNORKLE_WIDTH, Snorkle.SNORKLE_HEIGHT)
		self.vel_y = -4 + random.randint(-1,1)
		self.vel_x = 0
		self.state = 'SWIMMING'
		self.activate_timer = 0
		self.used = False
		self.type = 'Snorkle'

	def update(self):

		if self.state == 'SWIMMING':
			self.rect.x += self.vel_x
			self.rect.y += self.vel_y
			return False

		if self.state == 'ACTIVATED':
			if (pygame.time.get_ticks()-self.activate_timer)/1000 >= 2:
				self.state = 'SWIMMING'

		if self.state == 'STOMPED':
			if (pygame.time.get_ticks()-self.activate_timer)/1000 >= 1:
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

