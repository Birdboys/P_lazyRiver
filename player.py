import pygame
import numpy as np
import os
class Player:

	ACCELERATION_X = 1
	ACCELERATION_Y = 1.5
	DESCELERATION_Y = -1
	DESCELERATION_X = 0.3
	PLAYER_WIDTH, PLAYER_HEIGHT = 100, 100

	def __init__(self, WIDTH, HEIGHT):
		self.GAME_WIDTH = WIDTH
		self.GAME_HEIGHT = HEIGHT
		self.img_swim = pygame.image.load('Assets\\Player\\player_swimming_sprites.png').convert_alpha()
		self.img_hit = pygame.image.load('Assets\\Player\\player_hit_sprites.png').convert_alpha()
		self.img_bounce = pygame.image.load('Assets\\Player\\player_bouncing_sprites-sheet.png').convert_alpha()
		self.images = {'SWIMMING':self.img_swim, 'HIT':self.img_hit, 'BOUNCE':self.img_bounce}
		self.rect = pygame.Rect(self.GAME_WIDTH//2 - Player.PLAYER_WIDTH//2, 10, Player.PLAYER_WIDTH, Player.PLAYER_HEIGHT)
		self.vel_x = 0
		self.vel_y = 0
		self.hp = 2
		self.state = 'SWIMMING'
		self.stats = {'max_vel_x':4, 'max_vel_y':3, 'max_back_vel_y':-3}
		self.stats_bounce = {'max_vel_x':4, 'max_vel_y':4, 'max_back_vel_y':-4}
		self.hit_timer = 0
		self.bounce_timer = 0
		self.bounce_time = 2000
		self.money = 0
		self.frame = 0
		self.part_list = []
		

	def update(self,screen, obstacles, coins, snorklers):

		if self.state == 'SWIMMING':
			self.descelerate()
			self.rect.x += self.vel_x
			self.rect.y += self.vel_y
			self.coin_hit_check(coins)
			self.state = self.obstacle_hit_check(obstacles)
			self.snorkle_hit_check(snorklers)
			self.border_check()	
			 

		if self.state == 'HIT':
			
			self.descelerate()
			self.rect.x += self.vel_x//2
			self.rect.y += self.vel_y//2
			self.border_check()
			if (pygame.time.get_ticks()-self.hit_timer)/1000 >= 1:
				self.state = 'SWIMMING'
				self.hit_timer = 0


		if self.state == 'BOUNCE':
			if self.vel_x > 0 and self.vel_y > 0:
				temp = self.vel_y
				self.vel_y = temp * np.sin(45)
				self.vel_x = temp * np.sin(45)
			self.rect.x += self.vel_x
			self.rect.y += self.vel_y
			self.border_check()

			#GET SCALE
			delta = (pygame.time.get_ticks()-self.bounce_timer)
			scale = self.get_bounce_scale(delta)
			#self.images['BOUNCE'] = pygame.transform.scale(self.images['BOUNCE'], (Player.PLAYER_WIDTH + int(25 * scale), Player.PLAYER_HEIGHT + int(25 * scale)))
			
			if delta >= self.bounce_time:
				self.bounce_timer = 0
				#self.images['BOUNCE'] = pygame.transform.scale(self.images['BOUNCE'], (Player.PLAYER_WIDTH, Player.PLAYER_HEIGHT))

				if self.check_rebound_snorkle(snorklers):
					self.state = 'HIT'
					self.hit_timer = pygame.time.get_ticks()
				else:
					self.state = 'SWIMMING'
			elif delta >= self.bounce_time-self.bounce_time/10:
				self.coin_hit_check(coins)
				if self.check_rebound(obstacles):
					self.bounce_timer = pygame.time.get_ticks()
					#self.images['BOUNCE'] = pygame.transform.scale(self.images['BOUNCE'], (Player.PLAYER_WIDTH, Player.PLAYER_HEIGHT))

			self.vel_x = 0
			self.vel_y = 0
		self.border_check()	

	def render(self, screen):

		val = 1
		scale = 1
		match self.state:
			case 'SWIMMING':
				if self.vel_x < 0:
					val = 0
				elif self.vel_x > 0:
					val = 2

			case 'BOUNCE':
				delta = (pygame.time.get_ticks()-self.bounce_timer)
				scale = int(45 * self.get_bounce_scale(delta))
				if delta < self.bounce_time/10:
					val = 1
				elif delta >= self.bounce_time/2:
					val = val = 3
				else: val = 2


			case 'HIT':
				self.frame = (self.frame + 1) % 20
				if self.frame > 10:
					val = 0
				else:
					val = 1

			case _:
				val = 0
		image = self.get_sprite(self.images[self.state], 128, 128, (128 * val, 0),(128 * (val + 1), 128), scale)

		screen.blit(image, self.rect)

	def reset(self, hp,money):
		self.bounce_timer = 0
		self.hit_timer = 0
		self.hp = hp
		self.money = money
		self.rect.y = 10
		self.rect.x = self.GAME_WIDTH//2 - Player.PLAYER_WIDTH//2


	def key_down(self, key):

		match key:
			case 'a':
				if self.state == 'SWIMMING':
					self.vel_x -= Player.ACCELERATION_X 
					if self.vel_x < -self.stats['max_vel_x']:
						self.vel_x = -self.stats['max_vel_x'] 
				if self.state == 'BOUNCE':
					self.vel_x = -self.stats_bounce['max_vel_x'] 
				
			case 'd':
				if self.state == 'SWIMMING':
					self.vel_x += Player.ACCELERATION_X
					if self.vel_x > self.stats['max_vel_x']:
						self.vel_x = self.stats['max_vel_x']
				elif self.state == 'BOUNCE':
					self.vel_x = self.stats_bounce['max_vel_x']

			case 's':
				if self.state == 'SWIMMING':
					self.vel_y += Player.ACCELERATION_Y
					if self.vel_y > self.stats['max_vel_y']:
						self.vel_y = self.stats['max_vel_y']
				elif self.state == 'BOUNCE':
					self.vel_y = self.stats_bounce['max_vel_y']

			case 'w':
				if self.state == 'SWIMMING':
					self.vel_y -= Player.ACCELERATION_Y 
					if self.vel_y < self.stats['max_back_vel_y']:
						self.vel_y = self.stats['max_back_vel_y']
				elif self.state == 'BOUNCE':
					self.vel_y = -self.stats_bounce['max_vel_y']
	def descelerate(self):

		if self.vel_x != 0:
			direction = self.vel_x

			if self.vel_x < 0:
				self.vel_x += Player.DESCELERATION_X
			elif self.vel_x > 0:
				self.vel_x -= Player.DESCELERATION_X
			if self.vel_x/direction < 0:
				self.vel_x = 0

		if self.rect.y != 0:

			self.vel_y += Player.DESCELERATION_Y
			if self.vel_y < self.stats['max_back_vel_y']:
				self.vel_y = self.stats['max_back_vel_y']

	def border_check(self):
		if self.rect.y < 0:
			self.rect.y = 0
			self.vel_y = 0
		if self.rect.y + Player.PLAYER_HEIGHT > self.GAME_HEIGHT:
			self.y = self.GAME_HEIGHT - Player.PLAYER_HEIGHT
		if self.rect.x < 0:
			self.rect.x = 0
		if self.rect.x + Player.PLAYER_WIDTH > self.GAME_WIDTH:
			self.rect.x = self.GAME_WIDTH - Player.PLAYER_WIDTH


	def get_rect(self):
		return self.rect

	def get_hp(self):
		return self.hp

	def hit(self):
		self.hp -= 1

	def obstacle_hit_check(self, obstacles):
		hit = False
		for obstacle in obstacles:
			if pygame.Rect.colliderect(self.rect, obstacle.rect) and not obstacle.state == 'HIT' and self.get_distance(obstacle) < 75:
				self.hit()
				obstacle.hit()
				hit = True
		if hit:
			self.hit_timer = pygame.time.get_ticks()
			self.vel_x = self.vel_x * -1
			self.vel_y = self.vel_y * -1
			return 'HIT'
		else:
			return 'SWIMMING'


	def coin_hit_check(self, coins):
		for coin in coins:
			if pygame.Rect.colliderect(self.rect, coin.rect):
				self.money += 1
				coins.remove(coin)

	def snorkle_hit_check(self, snorkles):
		for snorkle in snorkles:
			if pygame.Rect.colliderect(self.rect, snorkle.rect) and not snorkle.used and self.get_distance(snorkle) < 40:
				self.state = 'BOUNCE'
				self.bounce_timer = pygame.time.get_ticks()
				snorkle.activated()
				

	def get_money(self):
		return self.money

	def get_bounce_scale(self, delta):
		#return (-0.64*((delta/1000-1.25)**2) + 1)
		return np.sin(2*np.pi*(delta/1000)/(self.bounce_time*2/1000))

	def check_rebound(self, obstacles):
		rebound = False
		for obstacle in obstacles:
			if pygame.Rect.colliderect(self.rect, obstacle.rect):
					if obstacle.state == 'BOUNCED':
						self.hit()
					rebound = True
					obstacle.bouncy()
			
				
				

		return rebound

	def check_rebound_snorkle(self, snorkles):
		hit = False
		for snorkler in snorkles:
			if pygame.Rect.colliderect(self.rect, snorkler.rect):
				snorkler.stomp()
				self.hit()
				hit = True
		return hit

	def get_distance(self, obj):
		x_dif = (self.rect.x + Player.PLAYER_WIDTH/2) - (obj.rect.x + obj.rect.width/2)
		y_dif = (self.rect.y + Player.PLAYER_HEIGHT/2) - (obj.rect.y + obj.rect.height/2)
		return ((x_dif)**2 + (y_dif)**2)**(1/2)

	def updateSpeed(self, vel):
		self.stats['max_vel_x'] = vel
		self.stats['max_vel_y'] = vel-1
		self.stats_bounce['max_vel_x'] = vel
		self.stats_bounce['max_vel_y'] = vel

	def get_sprite(self, image, width, height, p1, p2, scale=1):
		surf = pygame.Surface((width, height)).convert_alpha()
		surf.blit(image, (0,0), (p1[0],p1[1],p2[0],p2[1]))
		surf = pygame.transform.scale(surf, (Player.PLAYER_WIDTH+scale,Player.PLAYER_HEIGHT+scale))
		surf.set_colorkey((0,0,0))
		return surf

class

				




				

