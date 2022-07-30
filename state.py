import pygame
import os
import random
import math
import numpy as np
from obstacle import *
from particle import *

pygame.init()
class State():

	def __init__(self, game):
		self.game = game
	def update(self, events, delta):
		pass

	def render(self, surface):
		pass

	def enter_state(self):
		self.game.state_stack.append(self)

	def exit_state(self):
		self.game.state_stack.pop()


class TitleState(State):

	FPS = 60
	def __init__(self, game):
		self.game = game
		self.title_img = pygame.image.load('Assets/temp_title_screen.png').convert_alpha()
		self.title_rect = self.title_img.get_rect()

	def update(self, events, delta):

		for event in events:
			if event.type == pygame.QUIT:
				game.playing = False
				game.running = False

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_s:
					new_state = StartSwimState(self.game)
					new_state.enter_state()

	def render(self, surface):
		surface.blit(self.title_img, (0,0))

class SwimState(State):

	FPS = 60
	MONEY_FONT = pygame.font.Font("Assets/m5x7.ttf",35)
	MONEY_FONT.bold = True
	BACKGROUND_COLOR = (0,153,153)
	def __init__(self, game):
		State.__init__(self, game)
		self.game.player.hp = self.game.player_stats['hp']
		self.game.player.rect.y = 10
		pygame.time.set_timer(self.game.events['SPAWN'], self.game.spawn_timer, 1)

		self.hp_render_img = pygame.transform.scale(pygame.image.load('Assets\\UI\\player_hp_sprites.png').convert_alpha(), (35,35))
		self.hp_render_rect = self.hp_render_img.get_rect()
		self.hp_render_text = SwimState.MONEY_FONT.render(str(self.game.player_stats['hp']), True, (0,0,0))
		self.hp_render_text_rect = self.hp_render_text.get_rect()
		
		self.money_render_img = pygame.transform.scale(pygame.image.load('Assets\\UI\\player_money_sprites.png').convert_alpha(), (35,35))
		self.money_render_rect = self.money_render_img.get_rect()
		self.money_render_text = SwimState.MONEY_FONT.render(str(self.game.player_stats['money']), True, (0,0,0))
		self.money_render_text_rect = self.money_render_text.get_rect()
		self.run_time = pygame.time.get_ticks()
		
		self.prog_background = pygame.Rect(100, 10, 200, 35)
		self.prog_player = pygame.Rect(self.prog_background.x + 10, self.prog_background.y + 5, 180, 25)
		self.prog_enemy_img = pygame.transform.scale(pygame.image.load('Assets\\UI\\enemy_progress_runner.png').convert_alpha(), (48*4,48))
		self.prog_enemy_frame = 0

		self.speed_conv = {4: 0.75, 5: 0.85, 6: 0.95, 7: 1.05, 8: 1.15, 9: 1.25}

		self.initUI()

		self.goin = False
		self.end_timer = 0
		#self.game_image = pyg

	def update(self, events, delta):

		elapsed = (pygame.time.get_ticks()-self.run_time)/1000

		for event in events:
			if event.type == pygame.QUIT:
				self.game.playing = False
				self.game.running = False
			if event.type == self.game.events['SPAWN']:
				
				if elapsed >= 30:
					self.game.obsManager.spawn_obstacle(3, self.game.events['SPAWN'], self.game.spawn_timer)
				else:
					self.game.obsManager.spawn_obstacle(2, self.game.events['SPAWN'], self.game.spawn_timer)

		keys_pressed = pygame.key.get_pressed()
		if keys_pressed[pygame.K_a]:
			self.game.player.key_down('a')
		if keys_pressed[pygame.K_d]:
			self.game.player.key_down('d')
		if keys_pressed[pygame.K_s]:
			self.game.player.key_down('s')
		if keys_pressed[pygame.K_w]:
			self.game.player.key_down('w')
		if keys_pressed[pygame.K_p]:
			self.game.playing = False
			self.game.spawn_buffer = pygame.time.get_ticks()
			self.game.prev_state = self
			temp_surf = self.render(pygame.Surface((self.game.WIDTH, self.game.HEIGHT)))
			new_state = PauseState(self.game, temp_surf)
			new_state.enter_state()

		self.game.backgroundManager.update(delta)
		self.game.obsManager.update(self.game.game_canvas, delta)
		self.game.player.update(self.game.game_canvas,self.game.obsManager.get_obstacles(), self.game.obsManager.get_coins(), self.game.obsManager.get_snorkle(), delta, self.game.player_stats['money_mult']+1)
		
		if self.game.player.hp <= 0:
			if self.end_timer == 0:
				self.end_timer = pygame.time.get_ticks()
			if pygame.time.get_ticks() - self.end_timer > 2000:
				self.transition_state('DEAD')

		self.hp_render_text = SwimState.MONEY_FONT.render(str(self.game.player.get_hp()), True, (0,0,0))
		self.hp_render_text_rect = self.hp_render_text.get_rect()

		self.money_render_text = SwimState.MONEY_FONT.render(str(self.game.player.get_money()), True, (0,0,0))
		self.money_render_text_rect = self.money_render_text.get_rect()
		

		if elapsed >= 60:
			self.game.playing = False
			self.game.state_stack.pop()
			new_state = ShopState(self.game)
			new_state.enter_state()


	def render(self, surface):
		#if not self.goin:
			#new_state = CountdownState(self.game)
			#new_state.enter_state()
			#self.goin = True
		surface.fill((0,153,153))
		self.game.backgroundManager.render(surface)
		self.game.shadowManager.render(surface)
		self.game.obsManager.render(surface)
		self.game.shadowManager.render_player(surface)
		self.game.player.render(surface)
		self.renderHPBar(surface)
		self.renderMoneyCounter(surface)
		self.renderProgress(surface)

		if self.game.prev_state == self:
			return surface


	def reset_play_space(self):
		self.game.player.reset_counters()

	def transition_state(self, state):
		match state:
			case 'DEAD':
				self.game.player.state = 'SWIMMING'
				self.game.player_stats['money'] += self.game.player.get_money()
				self.game.player.reset(self.game.player_stats['hp'], 0)
				self.game.obsManager.reset()
				self.game.state_stack.pop()
				new_state = ShopEnterTransition(self.game)
				new_state.enter_state()

	def initUI(self):
		self.hp_render_rect.x = 20
		self.hp_render_text_rect.x = 45
		self.hp_render_rect.y = 10
		self.hp_render_text_rect.y = 300

		self.money_render_rect.x = self.game.WIDTH - self.money_render_rect.width - 20 - self.money_render_text_rect.width
		self.money_render_rect.y = 10
		self.money_render_text_rect.x = self.game.WIDTH - 20 - self.money_render_text_rect.width
		self.money_render_text_rect.y = 20

	def renderHPBar(self, surface):
		self.hp_render_rect.x = 20
		self.hp_render_text_rect.x = 25 + self.hp_render_rect.width
		self.hp_render_text_rect.y = 10
		surface.blit(self.hp_render_img, self.hp_render_rect)
		surface.blit(self.hp_render_text, self.hp_render_text_rect)

	def renderMoneyCounter(self, surface):
		self.money_render_rect.x = self.game.WIDTH - self.money_render_rect.width - 25 - self.money_render_text_rect.width
		self.money_render_text_rect.y = 10
		self.money_render_text_rect.x = self.game.WIDTH - 20 - self.money_render_text_rect.width
		surface.blit(self.money_render_img, self.money_render_rect)
		surface.blit(self.money_render_text, self.money_render_text_rect)

	def renderProgress(self, surface):
		pygame.draw.rect(surface, (139,155,180), self.prog_background)
		
		self.prog_player.width = 180 * (pygame.time.get_ticks() - self.run_time)//60000 * self.speed_conv[self.game.player_stats['max_vel_x']]
		pygame.draw.rect(surface, (254,172,52), self.prog_player)

		self.prog_enemy_frame = (self.prog_enemy_frame + 1) % 31
		temp = (self.prog_background.width - 20) * (pygame.time.get_ticks() - self.run_time)//60000
		val = self.prog_enemy_img.get_width()//4
		surface.blit(self.prog_enemy_img, (self.prog_background.x+temp - 24 + 10, 20), (self.prog_enemy_frame//8 * val, 0, val, self.prog_enemy_img.get_height()))

class StartSwimState(State):
	START_FONT = pygame.font.Font("Assets/m5x7.ttf",56)
	START_FONT.bold = True
	def __init__(self, game):
		State.__init__(self, game)

		self.run_time = pygame.time.get_ticks()
		
		self.prog_background = pygame.Rect(100, 10, 200, 35)
		self.prog_player = pygame.Rect(self.prog_background.x + 10, self.prog_background.y + 5, 180, 25)
		self.prog_enemy_img = pygame.transform.scale(pygame.image.load('Assets\\UI\\enemy_progress_runner.png').convert_alpha(), (48*4,48))
		self.prog_enemy_frame = 0

		self.obstacle_images_1 = pygame.image.load("Assets\\Obstacle\\obstacle_1_swimming_sprites.png")
		self.obstacle_images_3 = pygame.image.load("Assets\\Obstacle\\obstacle_3_swimming_sprites.png")

		self.player_images = pygame.image.load("Assets\\TransitionStuff\\player_cash.png")
		self.pusher_images = pygame.image.load("Assets\\TransitionStuff\\pusher_animation.png")
		self.pusher_rect = pygame.Rect(self.game.WIDTH//2 - self.game.player.rect.width//2, 360, Obstacle.OBSTACLE_WIDTH, Obstacle.OBSTACLE_HEIGHT)
		self.pusher_vel_x = 0
		self.pusher_vel_y = 0

		self.boundary_rect = pygame.Rect(self.game.WIDTH//2 - 100/2, self.game.HEIGHT-300, 100, 300)
		self.shadow = pygame.image.load("Assets\\shadow.png").convert_alpha()

		self.num_img = pygame.image.load('Assets\\UI\\pause_num_sprites.png').convert_alpha()
		self.num_img_rect = pygame.Rect((self.game.WIDTH//2 - self.game.WIDTH//8 , self.game.HEIGHT//2 - self.game.HEIGHT//8, self.game.WIDTH//4, self.game.HEIGHT//4))

		self.start_text_1 = StartSwimState.START_FONT.render(str('Press any key'), True, (255,255,255))
		self.start_text_2 = StartSwimState.START_FONT.render(str('to start'), True, (255,255,255))
		self.start_text_x, self.start_text_y = self.game.WIDTH//2 - self.start_text_1.get_width()//2,  self.game.HEIGHT//2 - self.start_text_1.get_height()//2 - 10
		self.start_text_2_x, self.start_text_2_y  = self.game.WIDTH//2 - self.start_text_2.get_width()//2,  self.start_text_y + self.start_text_1.get_height()
		self.obstacle_list = []
		self.rotations = []
		self.begin = False
		self.frame = 0
		self.goin = False
		self.num_val = -1

		self.part_list = []

		self.push_timer = 0

		self.initPlayer()

		self.initObstacles()
		

	def update(self, events, delta):
		
		keys_pressed = pygame.key.get_pressed()
		for event in events:
			if event.type == pygame.QUIT:
				self.game.running = False
				self.game.playing = False
			elif event.type == pygame.KEYDOWN and not self.begin and not keys_pressed[pygame.K_p]:
				self.frame = 0
				self.begin = True
				self.num_val = 0
				self.push_timer = pygame.time.get_ticks()
				self.pusher_vel_y = -1
				self.pusher_vel_x = random.uniform(-2,2)
		
		if keys_pressed[pygame.K_p]:
			self.game.playing = False
			self.game.spawn_buffer = pygame.time.get_ticks()
			self.game.prev_state = self
			temp_surf = self.render(pygame.Surface((self.game.WIDTH, self.game.HEIGHT)))
			new_state = PauseState(self.game, temp_surf)
			new_state.enter_state() 

		if not self.begin:
			self.ob_bob()
			self.frame = (self.frame + 1) % 120
		else:
			delta = pygame.time.get_ticks() - self.push_timer
			if delta >= 4500:
				self.get_collisions()
				self.edge_check()
				self.game.player.rect.y += 4
				self.pusher_rect.x += self.pusher_vel_x
				self.pusher_rect.y += self.pusher_vel_y
				self.part_list.append(Particle(self.game.player.rect.x + self.game.player.rect.width//2, self.game.player.rect.y + 50, random.randint(-1,1), random.randint(-4, -2), (255,255,255), 6, 0))
				
				for obstacle in self.obstacle_list:
					obstacle.rect.x += obstacle.vel_x
					obstacle.rect.y += obstacle.vel_y

				for part in self.part_list:
					part.update()

				if self.game.player.rect.y > self.game.HEIGHT:
					self.game.state_stack.pop()
					new_state = SwimState(self.game)
					new_state.enter_state()
			elif delta >= 4000:
				self.num_val = -1
			elif delta >= 3000:
				self.ob_bob()
				self.num_val = 2
			elif delta >= 2000:
				self.ob_bob()
				self.num_val = 1
			elif delta >= 1000:
				self.ob_bob()
				self.num_val = 0
			else:
				self.ob_bob()
				self.num_val = -1
			self.frame += 1
		

	def render(self, surface):
		surface.fill((0,153,153))
		self.game.backgroundManager.render(surface)
		self.render_shadows(surface)
		self.game.shadowManager.render_player(surface)
		counter = 0
		for obstacle in self.obstacle_list:
			surface.blit(pygame.transform.rotate(self.get_obs_sprite(obstacle), self.rotations[counter]).convert_alpha(),  obstacle.rect)
			counter += 1

		self.renderProgress(surface)
		

		self.game.shadowManager.render_shadow(surface, self.pusher_rect)
		surface.blit(self.get_pusher_sprite(), self.pusher_rect)
		if not self.begin:
			if self.frame // 30 < 3 and self.game.prev_state != self:
				surface.blit(self.start_text_1, (self.start_text_x, self.start_text_y))	
				surface.blit(self.start_text_2, (self.start_text_2_x, self.start_text_2_y))	
		else:
			
			if self.num_val < 0:
				for part in self.part_list:
					part.render(surface)
		surface.blit(self.get_player_sprite(), self.game.player.rect)
		if self.num_val >= 0:
			surface.blit(self.get_num(), self.num_img_rect)

		if self.game.prev_state == self:
			return surface
	
	def renderProgress(self, surface):
		pygame.draw.rect(surface, (139,155,180), self.prog_background)

		self.prog_enemy_frame = (self.prog_enemy_frame + 1) % 31
		surface.blit(self.prog_enemy_img, (self.prog_background.x - 24 + 10, 20), (0, 0, self.prog_enemy_img.get_height(), self.prog_enemy_img.get_height()))

	def render_shadows(self, surface):
		for obstacle in self.obstacle_list:
			surface.blit(pygame.transform.scale(self.shadow, (obstacle.rect.width, obstacle.rect.height)), obstacle.rect)

	def initPlayer(self):
		self.game.player.rect.x = self.game.WIDTH//2 - self.game.player.rect.width//2
		self.game.player.rect.y = self.game.HEIGHT - self.game.HEIGHT//3 - 70

	def initObstacles(self):
		num_tries = 0
		while len(self.obstacle_list) < 20:
			while len(self.obstacle_list) < 5:
				works = True
				new_ob = self.add_obstacle()
				for item in self.obstacle_list:
					if pygame.Rect.colliderect(item.rect, new_ob.rect):
						works = False
				if pygame.Rect.colliderect(self.game.player.rect, new_ob.rect) or pygame.Rect.colliderect(self.pusher_rect, new_ob.rect):
					works = False
				if works:
					self.obstacle_list.append(new_ob)

			works = True
			new_ob = self.add_obstacle()
			for item in self.obstacle_list:
				if pygame.Rect.colliderect(item.rect, new_ob.rect):
					works = False
			if pygame.Rect.colliderect(self.game.player.rect, new_ob.rect) or pygame.Rect.colliderect(self.pusher_rect, new_ob.rect):
				works = False
				
			if works:
				self.obstacle_list.append(new_ob)
			num_tries = num_tries + 1
			if num_tries > 30:
				self.rotations = [random.randint(0,360-1) for x in range(len(self.obstacle_list))]
				for obstacle in self.obstacle_list:
					obstacle.vel_x = 0
					obstacle.vel_y = 0
				return
		self.rotations = [random.randint(0,360-1) for x in range(len(self.obstacle_list))]
		for obstacle in self.obstacle_list:
			obstacle.vel_x = 0
			obstacle.vel_y = 0
		return

	def add_obstacle(self):
		obx = random.randint(16,400 - Obstacle.OBSTACLE_WIDTH - 16)
		oby = random.randint(0, self.game.HEIGHT - Obstacle.OBSTACLE_HEIGHT - 50)
		return Obstacle(obx, oby, random.randint(0,360))

	def get_obs_sprite(self, obs):
		surf = pygame.Surface((128, 128)).convert_alpha()

		if obs.preset == 2:
			surf.blit(self.obstacle_images_3, (0,0))
		else:
			surf.blit(self.obstacle_images_1, (0,0), ((obs.preset * self.obstacle_images_1.get_width()/2),0, self.obstacle_images_1.get_width()/2,128))
		surf = pygame.transform.scale(surf, (obs.OBSTACLE_WIDTH, obs.OBSTACLE_HEIGHT))
		surf.set_colorkey((0,0,0))

		return surf
	
	def get_pusher_sprite(self):
		surf = pygame.Surface((128, 128)).convert_alpha()

		if not self.begin:
			surf.blit(self.pusher_images, (0,0), (0,0,self.pusher_images.get_height(),self.pusher_images.get_height()))
			surf = pygame.transform.scale(surf, (self.game.player.rect.width, self.game.player.rect.height))
			surf.set_colorkey((0,0,0))
			
		else:
			delta = pygame.time.get_ticks() - self.push_timer
			
			if delta > 4500:
				if self.pusher_vel_x < -0.5:
					surf.blit(self.pusher_images, (0,0), (self.pusher_images.get_width()//7 * 5, 0, self.pusher_images.get_height(), self.pusher_images.get_height()))
				elif self.pusher_vel_x > 0.5:
					surf.blit(self.pusher_images, (0,0), (self.pusher_images.get_width()//7 * 6, 0, self.pusher_images.get_height(), self.pusher_images.get_height()))
				else:
					surf.blit(self.pusher_images, (0,0), (self.pusher_images.get_width()//7 * 4, 0, self.pusher_images.get_height(), self.pusher_images.get_height()))

			elif self.frame > 24:
				surf.blit(self.pusher_images, (0,0), (self.pusher_images.get_width()//7 * 3, 0, self.pusher_images.get_height(), self.pusher_images.get_height()))
			else:
				val = self.frame // 8
				surf.blit(self.pusher_images, (0,0), (val * self.pusher_images.get_width()//7, 0, self.pusher_images.get_height(), self.pusher_images.get_height()))
			surf = pygame.transform.scale(surf, (self.game.player.rect.width, self.game.player.rect.height))
			surf.set_colorkey((0,0,0))

		return surf


	def get_player_sprite(self):
		surf = pygame.Surface((128, 128)).convert_alpha()

		if not self.begin:
			surf.blit(self.player_images, (0,0), (0,0,self.player_images.get_height(),self.player_images.get_height()))
			surf = pygame.transform.scale(surf, (self.game.player.rect.width, self.game.player.rect.height))
			surf.set_colorkey((0,0,0))
			return surf
		else:
			surf.blit(self.player_images, (0,0), (self.player_images.get_width()//2,0,self.player_images.get_height(),self.player_images.get_height()))
			surf = pygame.transform.scale(surf, (self.game.player.rect.width, self.game.player.rect.height))
			surf.set_colorkey((0,0,0))
			return surf

	def get_num(self):
		surf = pygame.Surface((self.num_img.get_width()/3, self.num_img.get_height()))
		surf.blit(self.num_img, (0,0), ((self.num_val) * self.num_img.get_width()/3, 0, (self.num_val + 1) * self.num_img.get_width()/3, self.num_img.get_height()))
		surf.set_colorkey((0,0,0))
		surf = pygame.transform.scale(surf, (self.game.WIDTH//4, self.game.HEIGHT//4))
		return surf

	def ob_bob(self):
		for obstacle in self.obstacle_list:
			#if random.uniform(0,1) <= 0.05:
				#obstacle.rect.x += random.randint(-1,1)
			if random.uniform(0,1) <= 0.03:
				obstacle.rect.y += random.randint(-2,2)

		if random.uniform(0,1) <= 0.03:
			self.game.player.rect.y += random.randint(-2,2)

		#if random.uniform(0,1) <= 0.03:
			#self.pusher_rect.y += random.randint(-2,2)

	def get_collisions(self):
		for obstacle in self.obstacle_list:
			if obstacle.vel_x > 0 or obstacle.vel_y > 0:
				for other_obstacle in self.obstacle_list:
					if pygame.Rect.colliderect(obstacle.rect, other_obstacle.rect) and obstacle.rect.x != other_obstacle.rect.x:
						unit_x, unit_y = self.normalize(obstacle.rect.x, obstacle.rect.y, other_obstacle.rect.x, other_obstacle.rect.y)
						speed = math.sqrt(obstacle.vel_x**2 + obstacle.vel_y**2)
						other_obstacle.vel_x = unit_x * speed
						other_obstacle.vel_y = unit_y * speed
			if pygame.Rect.colliderect(obstacle.rect, self.pusher_rect):
				unit_x, unit_y = self.normalize(self.pusher_rect.x, self.pusher_rect.y, obstacle.rect.x, obstacle.rect.y)
				speed = math.sqrt(self.pusher_vel_x**2 + self.pusher_vel_y**2)
				obstacle.vel_x = unit_x * speed
				obstacle.vel_y = unit_y * speed

			if pygame.Rect.colliderect(obstacle.rect, self.game.player.rect):
				unit_x, unit_y = self.normalize(self.game.player.rect.x, self.game.player.rect.y, obstacle.rect.x, obstacle.rect.y)
				speed = 4
				obstacle.vel_x = unit_x * speed
				obstacle.vel_y = unit_y * speed

	def normalize(self, x1, y1, x2, y2):
		mag = math.sqrt((x2-x1)**2 + (y2-y1)**2)
		return (x2-x1)/mag, (y2-y1)/mag 

	def edge_check(self):
		for obstacle in self.obstacle_list:
			if obstacle.rect.x < 0 + 10:
				obstacle.vel_x = -obstacle.vel_x
			elif obstacle.rect.x + obstacle.rect.width > self.game.WIDTH - 10:
				obstacle.vel_x = -obstacle.vel_x


class PauseState(State):

	PAUSE_FONT = pygame.font.Font("Assets/m5x7.ttf",96)
	PAUSE_FONT.bold = True

	MENU_TIMER = pygame.USEREVENT+3
	FPS = 10
	def __init__(self, game, surface):
		State.__init__(self, game)
		self.game.playing = False
		self.play_sheet = pygame.image.load('Assets\\UI\\button_play_sprites.png')
		self.quit_sheet = pygame.image.load('Assets\\UI\\button_quit_sprites.png')
		self.tut_sheet = pygame.image.load('Assets\\UI\\button_tut_sprites.png')
		self.credits_sheet = pygame.image.load('Assets\\UI\\button_credits_sprites.png')
		self.index = 0
		self.initMenu()
		self.background_img = self.greyscale(surface)
		self.can_move = True

	def initMenu(self):
		self.play = Button(self.play_sheet, self.game.WIDTH//2 - Button.BUTTON_WIDTH//2, 64, 0)
		self.quit = Button(self.quit_sheet, self.game.WIDTH//2 - Button.BUTTON_WIDTH//2, 256, 23)
		self.tut = Button(self.tut_sheet, self.game.WIDTH//2 - Button.BUTTON_WIDTH//2, 448, 57)
		self.cred = Button(self.credits_sheet, self.game.WIDTH//2 - Button.BUTTON_WIDTH//2, 638, 76)
		self.buttons = [self.play, self.quit, self.tut, self.cred]

	def update(self, events , delta):

		for event in events:
			if event.type == pygame.QUIT:
				self.game.playing = False
				self.game.running = False
			if event.type == self.game.events['SPAWN']:
				self.game.spawn_buffer = pygame.time.get_ticks() - self.game.spawn_buffer
			if event.type == PauseState.MENU_TIMER:
				self.can_move = True

		keys_pressed = pygame.key.get_pressed()
		if self.can_move:
			if keys_pressed[pygame.K_w]:
				self.index = (self.index - 1) % len(self.buttons)
				self.can_move = False
				pygame.time.set_timer(PauseState.MENU_TIMER, 150, 1)
			if keys_pressed[pygame.K_s]:
				self.index = (self.index + 1) % len(self.buttons)
				self.can_move = False
				pygame.time.set_timer(PauseState.MENU_TIMER, 150, 1)

		if keys_pressed[pygame.K_RETURN]:
			if self.index == 0:
				self.game.playing = True
				pygame.time.set_timer(self.game.events['SPAWN'], self.game.spawn_buffer, 1)
				self.game.spawn_buffer = 0
				self.game.prev_state = None
				self.exit_state()

			elif self.index == 1:
				self.game.playing = False
				self.game.running = False

		self.buttons[self.index].update()

	def greyscale(self, surface: pygame.Surface):
	    arr = pygame.surfarray.pixels3d(surface)
	    mean_arr = np.dot(arr[:,:,:], [0.216, 0.587, 0.144])
	    mean_arr3d = mean_arr[..., np.newaxis]
	    new_arr = np.repeat(mean_arr3d[:, :, :], 3, axis=2)
	    return pygame.surfarray.make_surface(new_arr)

	def render(self, surface):
		surface.blit(self.background_img, (0,0))
		for button in self.buttons:
			button.render(surface)

class ShopState(State):

	SHOP_FONT = pygame.font.Font("Assets/m5x7.ttf", 64)
	SHOP_FONT.bold = True
	MENU_TIMER = pygame.USEREVENT+3
	SHOP_ROW = 2
	SHOP_COL = 2

	def __init__(self, game):
		State.__init__(self, game)
		self.index_x = 0
		self.img = pygame.image.load('Assets\\Background\\shop_background_sprites.png').convert_alpha()
		self.img_rect = pygame.Rect(0,0,self.game.WIDTH, self.game.HEIGHT)

		self.cursor_images = pygame.image.load('Assets\\UI\\shop_cursor_sprites.png')
		self.cursor_rect = pygame.Rect(0, 0, ShopItem.ITEM_WIDTH, ShopItem.ITEM_HEIGHT)
		self.index_y = 0
		self.store = []
		self.initItems()
		self.can_move = True
		self.player_money_render = ShopState.SHOP_FONT.render("$" + (str(self.game.player_stats['money'])), True, (139,155,180))
		self.player_money_rect = self.player_money_render.get_rect()
		self.player_money_rect.y = 655
		self.frame = 0
		self.cursor_frame = 0

	def update(self, events , delta):
		for event in events:
			if event.type == pygame.QUIT:
				self.game.playing = False
				self.word.running = False
			if event.type == ShopState.MENU_TIMER:
				self.can_move = True

		keys_pressed = pygame.key.get_pressed()
		if keys_pressed[pygame.K_ESCAPE]:
			self.game.state_stack.pop()
			new_state = ShopExitTransition(self.game)
			new_state.enter_state()

		self.player_money_render = ShopState.SHOP_FONT.render("$" + (str(self.game.player_stats['money'])), True, (139,155,180))
		self.player_money_rect.x = 155 - self.player_money_render.get_width()
		
		if self.can_move:
			if keys_pressed[pygame.K_a]:
				self.index_x = (self.index_x - 1)%ShopState.SHOP_COL
				self.can_move = False
				pygame.time.set_timer(ShopState.MENU_TIMER, 150, 1)
			if keys_pressed[pygame.K_d]:
				self.index_x = (self.index_x + 1)%ShopState.SHOP_COL
				self.can_move = False
				pygame.time.set_timer(ShopState.MENU_TIMER, 150, 1)
			if keys_pressed[pygame.K_s]:
				self.index_y = (self.index_y - 1)%ShopState.SHOP_ROW
				self.can_move = False
				pygame.time.set_timer(ShopState.MENU_TIMER, 150, 1)
			if keys_pressed[pygame.K_w]:
				self.index_y = (self.index_y + 1)%ShopState.SHOP_ROW
				self.can_move = False
				pygame.time.set_timer(ShopState.MENU_TIMER, 150, 1)

			if keys_pressed[pygame.K_RETURN]:
				i = self.index_y*2 + self.index_x
				if self.store[i].val_cur < self.store[i].val_max and self.game.player_stats['money'] >= self.store[i].costs[self.store[i].val_cur]:
					self.game.player_stats['money'] = self.game.player_stats['money'] - self.store[i].costs[self.store[i].val_cur]
					self.store[i].val_cur += 1

					if i == 0: #IF SPEED BOUGHT
						self.game.increasePlayerSpeed()
					elif i == 1: #IF HP BOUGHT
						self.game.increasePlayerHP()
					elif i == 2: #IF NOODLE BOUGHT
						self.game.increasePlayerMoneyMult()
				
				if i == 3: #IF SPEEDO BOUGHT
					self.game.state_stack.pop()
					new_state = ShopExitTransition(self.game)
					new_state.enter_state()

				self.can_move = False
				pygame.time.set_timer(ShopState.MENU_TIMER, 150, 1)	

		self.updateItems()
		self.updateCursor()
		self.frame = (self.frame + 1) % (10 * 4)
		self.cursor_frame = (self.cursor_frame + 1) % 60
	def render(self, surface):

		surface.blit(self.get_background(), self.img_rect)
		for ROW in range(ShopState.SHOP_ROW):
			for COLUMN in range(ShopState.SHOP_COL):
				if self.index_y == ROW and self.index_x == COLUMN:
					self.store[ROW*2+COLUMN].frame += 1 
				self.store[ROW*2+COLUMN].render(surface)

		surface.blit(self.player_money_render,self.player_money_rect)
		if self.cursor_frame < 30:
			surface.blit(self.get_cursor(), self.cursor_rect)
				
	def initItems(self):
		self.store.append(self.speedUpgrade())
		self.store.append(self.hpUpgrade())
		self.store.append(self.moneyUpgrade())
		self.store.append(self.exitButton())

	def speedUpgrade(self):
		speed_img = pygame.image.load('Assets/UI/shop_speed_sprites.png').convert_alpha()
		boy = ShopItem(speed_img, 5-(9-self.game.player_stats['max_vel_x']), 5, [5,10,15,20,25])
		boy.img_rect.x, boy.img_rect.y = 40,10
		return boy

	def hpUpgrade(self):
		hp_img = pygame.image.load('Assets/UI/shop_hp_sprites.png').convert_alpha()
		boy = ShopItem(hp_img, self.game.player_stats['hp']-2, 3, [10,15,20])
		boy.img_rect.x, boy.img_rect.y = self.game.WIDTH-40-boy.ITEM_WIDTH,10
		return boy

	def moneyUpgrade(self):
		money_img = pygame.image.load('Assets/UI/shop_money_sprites.png').convert_alpha()
		boy =  ShopItem(money_img, self.game.player_stats['money_mult'], 3, [20,40,60])
		boy.img_rect.x, boy.img_rect.y = 40,self.store[0].img_rect.y + self.store[0].img_rect.height + 50
		return boy

	def exitButton(self):
		exit_img = pygame.image.load('Assets/UI/shop_exit_sprites.png').convert_alpha()
		boy = ShopItem(exit_img, 0, 0, [0])
		boy.img_rect.x, boy.img_rect.y = self.game.WIDTH-40-boy.ITEM_WIDTH,self.store[0].img_rect.y + self.store[0].img_rect.height + 50
		return boy

	def updateItems(self):
		for item in self.store:
			item.update()

	def updateCursor(self):
		ind = self.index_y*2 + self.index_x
		self.cursor_rect.x, self.cursor_rect.y = self.store[ind].img_rect.x, self.store[ind].img_rect.y
	
	def get_background(self):
		surf = pygame.Surface((self.img.get_width()/8, self.img.get_height()))
		temp = not self.can_move
		frame_temp = self.frame//10
		surf.blit(self.img, (0,0), (temp * self.img.get_width()/2 + frame_temp*self.img.get_width()/8, 0, temp*self.img.get_width()/2 + (frame_temp+1)*self.img.get_width()/8, self.img.get_height()))
		surf = pygame.transform.scale(surf, (self.game.WIDTH, self.game.HEIGHT))
		return surf

	def get_cursor(self):
		surf = pygame.Surface((self.cursor_images.get_width()/2, self.cursor_images.get_height()))
		ind = self.index_y*2 + self.index_x
		if not self.game.player_stats['money'] < self.store[ind].get_cost():
			surf.blit(self.cursor_images, (0,0), (0, 0, self.cursor_images.get_width()/2, self.cursor_images.get_height()))
		else:
			surf.blit(self.cursor_images, (0,0), (self.cursor_images.get_width()/2, 0, self.cursor_images.get_width(), self.cursor_images.get_height()))

		surf.convert_alpha()
		surf.set_colorkey((0,0,0))

		return surf
class ShopEnterTransition(State):
	def __init__(self, game):
		self.img = pygame.image.load('Assets\\Background\\shop_background_enter.png').convert_alpha()
		self.game = game
		self.store = []
		self.initItems()
		self.frame = 0
		self.img_rect = pygame.Rect((0,0),(self.game.WIDTH,self.game.HEIGHT))

		self.player_money_render = ShopState.SHOP_FONT.render("$" + (str(self.game.player_stats['money'])), True, (139,155,180))
		self.player_money_rect = self.player_money_render.get_rect()
		self.player_money_rect.y = 655

	def update(self, events, delta):
		self.player_money_render = ShopState.SHOP_FONT.render("$" + (str(self.game.player_stats['money'])), True, (139,155,180))
		self.player_money_rect.x = 155 - self.player_money_render.get_width()

		self.frame = self.frame + 1
		if self.frame >= 48:
			self.game.state_stack.pop()
			new_state = ShopState(self.game)
			new_state.enter_state()


	def render(self, surface):
		surface.blit(self.get_background(), self.img_rect)
		for thing in self.store:
			thing.render(surface)

		surface.blit(self.player_money_render,self.player_money_rect)

	def initItems(self):
		self.store.append(self.speedUpgrade())
		self.store.append(self.hpUpgrade())
		self.store.append(self.moneyUpgrade())
		self.store.append(self.exitButton())

	def speedUpgrade(self):
		speed_img = pygame.image.load('Assets/UI/shop_speed_sprites.png').convert_alpha()
		boy = ShopItem(speed_img, 5-(9-self.game.player_stats['max_vel_x']), 5, [5,10,15,20,25])
		boy.img_rect.x, boy.img_rect.y = 40,10
		return boy

	def hpUpgrade(self):
		hp_img = pygame.image.load('Assets/UI/shop_hp_sprites.png').convert_alpha()
		boy = ShopItem(hp_img, self.game.player_stats['hp']-2, 3, [10,15,20])
		boy.img_rect.x, boy.img_rect.y = self.game.WIDTH-40-boy.ITEM_WIDTH,10
		return boy

	def moneyUpgrade(self):
		money_img = pygame.image.load('Assets/UI/shop_money_sprites.png').convert_alpha()
		boy =  ShopItem(money_img, self.game.player_stats['money_mult'], 3, [20,40,60])
		boy.img_rect.x, boy.img_rect.y = 40,self.store[0].img_rect.y + self.store[0].img_rect.height + 50
		return boy

	def exitButton(self):
		exit_img = pygame.image.load('Assets/UI/shop_exit_sprites.png').convert_alpha()
		boy = ShopItem(exit_img, 0, 0, [0])
		boy.img_rect.x, boy.img_rect.y = self.game.WIDTH-40-boy.ITEM_WIDTH,self.store[0].img_rect.y + self.store[0].img_rect.height + 50
		return boy

	def get_background(self):
		surf = pygame.Surface((self.img.get_width()/6, self.img.get_height()))
		frame_temp = self.frame//8
		surf.blit(self.img, (0,0),(frame_temp*self.img.get_width()/6, 0, (frame_temp+1)*self.img.get_width()/6, self.img.get_height()))
		surf = pygame.transform.scale(surf, (self.game.WIDTH, self.game.HEIGHT))
		return surf

class ShopExitTransition(State):
	def __init__(self, game):
		self.img = pygame.image.load('Assets\\Background\\shop_background_leave.png').convert_alpha()
		self.game = game
		self.store = []
		self.initItems()
		self.frame = 0
		self.img_rect = pygame.Rect((0,0),(self.game.WIDTH,self.game.HEIGHT))

		self.player_money_render = ShopState.SHOP_FONT.render("$" + (str(self.game.player_stats['money'])), True, (139,155,180))
		self.player_money_rect = self.player_money_render.get_rect()
		self.player_money_rect.y = 655

	def update(self, events, delta):
		self.player_money_render = ShopState.SHOP_FONT.render("$" + (str(self.game.player_stats['money'])), True, (139,155,180))
		self.player_money_rect.x = 155 - self.player_money_render.get_width()

		self.frame = self.frame + 1
		if self.frame >= 60:
			self.game.state_stack.pop()
			new_state = StartSwimState(self.game)
			new_state.enter_state()


	def render(self, surface):
		surface.blit(self.get_background(), self.img_rect)
		for thing in self.store:
			thing.render(surface)

		surface.blit(self.player_money_render,self.player_money_rect)

	def initItems(self):
		self.store.append(self.speedUpgrade())
		self.store.append(self.hpUpgrade())
		self.store.append(self.moneyUpgrade())
		self.store.append(self.exitButton())

	def speedUpgrade(self):
		speed_img = pygame.image.load('Assets/UI/shop_speed_sprites.png').convert_alpha()
		boy = ShopItem(speed_img, 5-(9-self.game.player_stats['max_vel_x']), 5, [5,10,15,20,25])
		boy.img_rect.x, boy.img_rect.y = 40,10
		return boy

	def hpUpgrade(self):
		hp_img = pygame.image.load('Assets/UI/shop_hp_sprites.png').convert_alpha()
		boy = ShopItem(hp_img, self.game.player_stats['hp']-2, 3, [10,15,20])
		boy.img_rect.x, boy.img_rect.y = self.game.WIDTH-40-boy.ITEM_WIDTH,10
		return boy

	def moneyUpgrade(self):
		money_img = pygame.image.load('Assets/UI/shop_money_sprites.png').convert_alpha()
		boy =  ShopItem(money_img, self.game.player_stats['money_mult'], 3, [20,40,60])
		boy.img_rect.x, boy.img_rect.y = 40,self.store[0].img_rect.y + self.store[0].img_rect.height + 50
		return boy

	def exitButton(self):
		exit_img = pygame.image.load('Assets/UI/shop_exit_sprites.png').convert_alpha()
		boy = ShopItem(exit_img, 0, 0, [0])
		boy.img_rect.x, boy.img_rect.y = self.game.WIDTH-40-boy.ITEM_WIDTH,self.store[0].img_rect.y + self.store[0].img_rect.height + 50
		return boy

	def get_background(self):
		surf = pygame.Surface((self.img.get_width()/10, self.img.get_height()))
		frame_temp = self.frame//8
		surf.blit(self.img, (0,0),(frame_temp*self.img.get_width()/10, 0, (frame_temp+1)*self.img.get_width()/10, self.img.get_height()))
		surf = pygame.transform.scale(surf, (self.game.WIDTH, self.game.HEIGHT))
		return surf

class CountdownState(State):
	def __init__(self, game):
		self.game = game
		self.game.playing = False
		self.img = pygame.image.load('Assets\\UI\\pause_num_sprites.png').convert_alpha()
		self.img_rect = pygame.Rect((self.game.WIDTH//3 , self.game.HEIGHT//3, self.game.WIDTH//3, self.game.HEIGHT//3))
		self.go_time = pygame.time.get_ticks()
		self.val = 0

	def update(self, events, delta):
		if pygame.time.get_ticks() - self.go_time >= 3000:
			self.exit_state()
		elif pygame.time.get_ticks() - self.go_time >= 2000:
			self.val = 0
		elif pygame.time.get_ticks() - self.go_time >= 1000:
			self.val = 1
		else:
			self.val = 2

	def render(self, surface):
		surface.blit(self.get_num(), self.img_rect)

	def get_num(self):
		surf = pygame.Surface((self.img.get_width()/3, self.img.get_height()))
		surf.fill((0,153,153))
		surf.blit(self.img, (0,0), ((self.val) * self.img.get_width()/3, 0, (self.val + 1) * self.img.get_width()/3, self.img.get_height()))
		surf.set_colorkey((0,0,0))
		surf = pygame.transform.scale(surf, (self.game.WIDTH//3, self.game.HEIGHT//3))
		return surf

class Button():

	BUTTON_WIDTH = 256

	def __init__(self, sheet, x, y, frame):
		self.img_sheet = sheet
		self.x, self.y = x, y
		self.frame = frame
	
	def update(self):
		self.frame = (self.frame + 1) % (12 * 8)

	def render(self, surface):
		surface.blit(self.get_sprite(), (self.x, self.y))

	def get_sprite(self):
		temp = self.frame//8
		temp_surf = pygame.Surface((256, 150)) 
		w, h = self.img_sheet.get_width()//12, self.img_sheet.get_height()
		temp_surf.blit(self.img_sheet, (0,0), (temp * w, 0, (temp+1)*w, h))
		temp_surf.convert_alpha()
		temp_surf.set_colorkey((0,0,0))
		return temp_surf




class ShopItem():
	
	ITEM_WIDTH = 125
	ITEM_HEIGHT = 125
	ITEM_FONT = pygame.font.Font("Assets/m5x7.ttf",32)
	def __init__(self, img, val_cur, val_max, costs):
		self.img = pygame.transform.scale(img, (ShopItem.ITEM_WIDTH*3, ShopItem.ITEM_HEIGHT))
		#self.img_hover = pygame.image.load('Assets/%s.png'%(img)).convert_alpha()
		#self.img_out = pygame.image.load('Assets/%s.png'%(img)).convert_alpha()
		self.img_rect = self.img.get_rect()
		self.val_cur = val_cur
		self.val_max = val_max
		self.costs = costs

		if self.val_cur >= self.val_max:
			self.price_render = ShopItem.ITEM_FONT.render("MAX", True, (0,0,0))
		else:
			self.price_render = ShopItem.ITEM_FONT.render(str(self.costs[self.val_cur]), True, (0,0,0))
		self.val_render = ShopItem.ITEM_FONT.render("%s/%s"%(self.val_cur,self.val_max), True, (0,0,0))
		self.price_rect = self.price_render.get_rect()
		self.val_rect = self.val_render.get_rect()
		self.frame = 0

	def update(self):
		if self.val_cur >= self.val_max:
			self.price_render = ShopItem.ITEM_FONT.render("MAX", True, (0,0,0))
		else:
			self.price_render = ShopItem.ITEM_FONT.render(str(self.costs[self.val_cur]), True, (0,0,0))
		self.val_render = ShopItem.ITEM_FONT.render("%s/%s"%(self.val_cur,self.val_max), True, (0,0,0))
		self.frame = self.frame % 35 

	def render(self, surface):
		self.progress_rect_border = pygame.Rect((self.img_rect.x, self.img_rect.y + self.img_rect.height), (ShopItem.ITEM_WIDTH, 20))
		if self.val_max == 0:
			self.progress_rect = pygame.Rect((self.progress_rect_border.x + 5, self.progress_rect_border.y + 5), (self.progress_rect_border.width-10, self.progress_rect_border.height-10))
		else:
			self.progress_rect = pygame.Rect(self.progress_rect_border.x + 5, self.progress_rect_border.y + 5, self.val_cur * (((self.progress_rect_border.width-10)/self.val_max)), self.progress_rect_border.height-10)
		surface.blit(self.get_sprite(), self.img_rect)
		self.setup_text()
		surface.blit(self.price_render, self.price_rect)
		surface.blit(self.val_render, self.val_rect	)
		pygame.draw.rect(surface, (254,174,152), self.progress_rect_border)
		pygame.draw.rect(surface, (255,255,255), self.progress_rect)

	def render_out(self, surface):
		surface.blitz(self.img_out, self.img_rect)

	def purchased(self):
		self.val_cur += 1

	def setup_text(self):
		self.price_rect.x, self.price_rect.y = self.img_rect.x+5, self.img_rect.y
		self.val_rect.x,self.val_rect.y = self.img_rect.x+ShopItem.ITEM_WIDTH-37, self.img_rect.y

	def get_sprite(self):
		surf = pygame.Surface((ShopItem.ITEM_WIDTH, ShopItem.ITEM_HEIGHT)).convert_alpha()
		temp = self.frame//12
		surf.blit(self.img, (0,0), (ShopItem.ITEM_WIDTH * temp, 0, ShopItem.ITEM_WIDTH * (temp + 1), ShopItem.ITEM_HEIGHT))
		surf.set_colorkey((0,0,0))
		return surf

	def get_cost(self):
		return self.costs[self.val_cur]
