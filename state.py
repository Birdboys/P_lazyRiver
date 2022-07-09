import pygame
import os
import random
import numpy as np

pygame.init()
class State():

	def __init__(self, game):
		self.game = game
	def update(self, events):
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

	def update(self, events):

		for event in events:
			if event.type == pygame.QUIT:
				game.playing = False
				game.running = False

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_s:
					new_state = SwimState(self.game)
					new_state.enter_state()

	def render(self, surface):
		surface.blit(self.title_img, (0,0))

class SwimState(State):

	FPS = 60
	HP_FONT = pygame.font.Font("Assets/m5x7.ttf",32)
	BACKGROUND_COLOR = (0,153,153)
	def __init__(self, game):
		State.__init__(self, game)
		self.game.player.hp = self.game.player_stats['hp']
		pygame.time.set_timer(self.game.events['SPAWN'], self.game.spawn_timer, 1)

		self.hp_render = SwimState.HP_FONT.render(str(self.game.player_stats['hp']), True, (0,0,0))
		self.hp_rect = self.hp_render.get_rect()

		self.money_render = SwimState.HP_FONT.render(str(self.game.player_stats['money']), True, (0,0,0))
		self.money_rect = self.money_render.get_rect()

		self.initUI()

		self.run_time = pygame.time.get_ticks()
		#self.game_image = pyg

	def update(self, events):

		elapsed = (pygame.time.get_ticks()-self.run_time)/1000

		for event in events:
			if event.type == pygame.QUIT:
				self.game.playing = False
				self.game.running = False
			if event.type == self.game.events['SPAWN']:
				
				if elapsed >= 50:
					self.game.obsManager.spawn_obstacle(5, self.game.events['SPAWN'], self.game.spawn_timer)
				elif elapsed >= 30:
					self.game.obsManager.spawn_obstacle(4, self.game.events['SPAWN'], self.game.spawn_timer)
				else:
					self.game.obsManager.spawn_obstacle(3, self.game.events['SPAWN'], self.game.spawn_timer)

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
			new_state = PauseState(self.game)
			new_state.enter_state()

		self.game.obsManager.update(self.game.game_canvas)
		self.game.player.update(self.game.game_canvas,self.game.obsManager.get_obstacles(), self.game.obsManager.get_coins(), self.game.obsManager.get_snorkle())
		
		if self.game.player.hp <= 0:
			self.transition_state('DEAD')

		self.money_render = SwimState.HP_FONT.render(str(self.game.player.get_money()), True, (0,0,0))
		self.hp_render = SwimState.HP_FONT.render(str(self.game.player.get_hp()), True, (0,0,0))

		"""if elapsed >= 60:
			print("TIME END")
			self.game.playing = False
			self.game.state_stack.pop()
			new_state = ShopState(self.game)
			new_state.enter_state()"""


	def render(self, surface):
		surface.fill((0,153,153))
		self.game.obsManager.render(surface)
		self.game.player.render(surface)
		surface.blit(self.hp_render, self.hp_rect)
		surface.blit(self.money_render,self.money_rect)

	def reset_play_space(self):
		self.game.player.reset_counters()

	def transition_state(self, state):
		match state:
			case 'DEAD':
				self.game.player_stats['money'] += self.game.player.get_money()
				self.game.player.reset(self.game.player_stats['hp'], 0)
				self.game.obsManager.reset()
				self.game.state_stack.pop()
				new_state = ShopState(self.game)
				new_state.enter_state()

	def initUI(self):
		self.money_rect.y = 32

class PauseState(State):

	MENU_TIMER = pygame.USEREVENT+3
	FPS = 10
	def __init__(self, game):
		State.__init__(self, game)
		self.game.playing = False
		self.resume = Button('temp_resume_button','temp_resume_button') 
		self.exit = Button('temp_exit_button','temp_exit_button') 
		self.buttons = [self.resume, self.exit]
		self.index = 0
		self.initMenu()
		self.can_move = True

	def initMenu(self):
		self.game.game_canvas.fill((0,0,0))
		self.buttons[0].rect.x = 50
		self.buttons[0].rect.y = 200
		self.buttons[1].rect.x = 50
		self.buttons[1].rect.y = self.game.HEIGHT-300

	def update(self, events):

		for event in events:
			if event.type == pygame.QUIT:
				self.game.playing = False
				self.game.running = False
			if event.type == self.game.events['SPAWN']:
				self.game.spawn_buffer = pygame.time.get_ticks() - self.game.spawn_buffer
			if event.type == ShopState.MENU_TIMER:
				self.can_move = True

		keys_pressed = pygame.key.get_pressed()
		if self.can_move:
			if keys_pressed[pygame.K_w]:
				self.index = (self.index - 1) % len(self.buttons)
				self.can_move = False
				pygame.time.set_timer(ShopState.MENU_TIMER, 250, 1)
			if keys_pressed[pygame.K_s]:
				self.index = (self.index + 1) % len(self.buttons)
				self.can_move = False
				pygame.time.set_timer(ShopState.MENU_TIMER, 250, 1)

		if keys_pressed[pygame.K_RETURN]:
			if self.index == 0:
				self.game.playing = True
				pygame.time.set_timer(self.game.events['SPAWN'], self.game.spawn_buffer, 1)
				self.game.spawn_buffer = 0
				self.exit_state()

			elif self.index == 1:
				self.game.playing = False
				self.game.running = False

	def render(self, surface):
		surface.fill((0,0,0))
		for x in range(len(self.buttons)):
			if not self.index == x:
				self.buttons[x].render(surface)
			else:
				self.buttons[x].render_hover(surface)

class ShopState(State):

	SHOP_FONT = pygame.font.Font("Assets/m5x7.ttf",32)
	MENU_TIMER = pygame.USEREVENT+3
	SHOP_ROW = 2
	SHOP_COL = 2
	def __init__(self, game):
		State.__init__(self, game)
		self.index_x = 0
		self.index_y = 0
		self.store = []
		self.initItems()
		self.can_move = True
		self.player_money_render = ShopState.SHOP_FONT.render(str(self.game.player_stats['money']), True, (0,0,0))
		self.player_money_rect = self.player_money_render.get_rect()

	def update(self, events):
		for event in events:
			if event.type == pygame.QUIT:
				self.game.playing = False
				self.word.running = False
			if event.type == ShopState.MENU_TIMER:
				self.can_move = True

		keys_pressed = pygame.key.get_pressed()
		if keys_pressed[pygame.K_ESCAPE]:
			self.game.state_stack.pop()
			new_state = SwimState(self.game)
			new_state.enter_state()

		if self.can_move:
			if keys_pressed[pygame.K_a]:
				self.index_x = (self.index_x - 1)%ShopState.SHOP_COL
				self.can_move = False
				pygame.time.set_timer(ShopState.MENU_TIMER, 250, 1)
			if keys_pressed[pygame.K_d]:
				self.index_x = (self.index_x + 1)%ShopState.SHOP_COL
				self.can_move = False
				pygame.time.set_timer(ShopState.MENU_TIMER, 250, 1)
			if keys_pressed[pygame.K_s]:
				self.index_y = (self.index_y - 1)%ShopState.SHOP_ROW
				self.can_move = False
				pygame.time.set_timer(ShopState.MENU_TIMER, 250, 1)
			if keys_pressed[pygame.K_w]:
				self.index_y = (self.index_y + 1)%ShopState.SHOP_ROW
				self.can_move = False
				pygame.time.set_timer(ShopState.MENU_TIMER, 250, 1)

			if keys_pressed[pygame.K_RETURN]:
				i = self.index_y*2 + self.index_x
				#print(self.store[i].val_cur, self.store[i].val_max, self.game.player_stats['money'])
				if self.store[i].val_cur < self.store[i].val_max and self.game.player_stats['money'] >= self.store[i].costs[self.store[i].val_cur]:
					self.game.player_stats['money'] = self.game.player_stats['money'] - self.store[i].costs[self.store[i].val_cur]
					self.store[i].val_cur += 1

					if i == 0: #IF SPEED BOUGHT
						print("SPEED")
						self.game.increasePlayerSpeed()
					elif i == 1: #IF HP BOUGHT
						print("HP")
						self.game.increasePlayerHP()
					elif i == 2: #IF NOODLE BOUGHT
						print("NOODLE")
						self.game.noodleObtained()
					elif i == 3: #IF SPEEDO BOUGHT
						print("SPEEDO")
						self.game.speedoObtained()
					self.can_move = False
					pygame.time.set_timer(ShopState.MENU_TIMER, 250, 1)

		self.player_money_render = ShopState.SHOP_FONT.render(str(self.game.player_stats['money']), True, (0,0,0))
		self.updateItems()

	def render(self, surface):

		surface.fill((255,255,255))
		for ROW in range(ShopState.SHOP_ROW):
			for COLUMN in range(ShopState.SHOP_COL):
				if self.index_y == ROW and self.index_x == COLUMN:
					self.store[ROW*2+COLUMN].render_hover(surface)
				else:
					self.store[ROW*2+COLUMN].render(surface)

		surface.blit(self.player_money_render,self.player_money_rect)
				
	def initItems(self):
		self.store.append(self.speedUpgrade())
		self.store.append(self.hpUpgrade())
		self.store.append(self.noodleUpgrade())
		self.store.append(self.speedoUpgrade())

	def speedUpgrade(self):
		speed_img = pygame.image.load('Assets/temp_speed_icon.png').convert_alpha()
		boy = ShopItem(speed_img, 5-(9-self.game.player_stats['max_vel_x']), 5, [5,10,15,20,25])
		boy.img_rect.x, boy.img_rect.y = 50,50
		return boy

	def hpUpgrade(self):
		hp_img = pygame.image.load('Assets/temp_heart_icon.png').convert_alpha()
		boy = ShopItem(hp_img, self.game.player_stats['hp']-1, 4, [5,10,15,20])
		boy.img_rect.x, boy.img_rect.y = self.game.WIDTH-50-boy.ITEM_WIDTH,50
		return boy

	def noodleUpgrade(self):
		noodle_img = pygame.image.load('Assets/temp_noodle_icon.png').convert_alpha()
		boy =  ShopItem(noodle_img, self.game.player_stats['noodle_upgrade'], 1, [20])
		boy.img_rect.x, boy.img_rect.y = 50,self.game.HEIGHT-50-boy.ITEM_HEIGHT
		return boy

	def speedoUpgrade(self):
		speedo_img = pygame.image.load('Assets/temp_speedo_icon.png').convert_alpha()
		boy = ShopItem(speedo_img, self.game.player_stats['speedo_upgrade'], 1, [30])
		boy.img_rect.x, boy.img_rect.y = self.game.WIDTH-50-boy.ITEM_WIDTH,self.game.HEIGHT-50-boy.ITEM_HEIGHT
		return boy

	def updateItems(self):
		for item in self.store:
			item.update()



class Button():

	def __init__(self, img, img_hover):
		self.img = pygame.image.load('Assets/%s.png'%(img)).convert_alpha()
		self.img_hover = pygame.transform.flip(self.img, True, False)
		self.rect = self.img.get_rect()

	def render(self, surface):
		surface.blit(self.img, self.rect)

	def render_hover(self, surface):
		surface.blit(self.img_hover, self.rect)


class ShopItem():
	
	ITEM_WIDTH = 125
	ITEM_HEIGHT = 125
	ITEM_FONT = pygame.font.Font("Assets/m5x7.ttf",32)
	def __init__(self, img, val_cur, val_max, costs):
		self.img = pygame.transform.scale(img, (ShopItem.ITEM_WIDTH, ShopItem.ITEM_HEIGHT))
		#self.img_hover = pygame.image.load('Assets/%s.png'%(img)).convert_alpha()
		#self.img_out = pygame.image.load('Assets/%s.png'%(img)).convert_alpha()
		self.img_rect = self.img.get_rect()
		self.val_cur = val_cur
		self.val_max = val_max
		self.costs = costs
		self.price_render = ShopItem.ITEM_FONT.render(str(self.costs[self.val_cur]), True, (0,0,0))
		self.val_render = ShopItem.ITEM_FONT.render("%s/%s"%(self.val_cur,self.val_max), True, (0,0,0))
		self.price_rect = self.price_render.get_rect()
		self.val_rect = self.val_render.get_rect()

	def update(self):
		self.price_render = ShopItem.ITEM_FONT.render(str(self.costs[self.val_cur]), True, (0,0,0))
		self.val_render = ShopItem.ITEM_FONT.render("%s/%s"%(self.val_cur,self.val_max), True, (0,0,0))

	def render(self, surface):
		surface.blit(self.img, self.img_rect)
		self.setup_text()
		surface.blit(self.price_render, self.price_rect)
		surface.blit(self.val_render, self.val_rect	)

	def render_hover(self, surface):
		surface.blit(pygame.transform.flip(self.img,True,False), self.img_rect)
		self.setup_text()
		surface.blit(self.price_render, self.price_rect)
		surface.blit(self.val_render, self.val_rect	)

	def render_out(self, surface):
		surface.blitz(self.img_out, self.img_rect)

	def purchased(self):
		self.val_cur += 1

	def setup_text(self):
		self.price_rect.x, self.price_rect.y = self.img_rect.x+5, self.img_rect.y
		self.val_rect.x,self.val_rect.y = self.img_rect.x+ShopItem.ITEM_WIDTH-37, self.img_rect.y





