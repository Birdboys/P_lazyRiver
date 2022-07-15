import pygame
import os
import random
import numpy as np

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
					new_state = SwimState(self.game)
					new_state.enter_state()

	def render(self, surface):
		surface.blit(self.title_img, (0,0))

class SwimState(State):

	FPS = 60
	MONEY_FONT = pygame.font.Font("Assets/m5x7.ttf",48)
	BACKGROUND_COLOR = (0,153,153)
	def __init__(self, game):
		State.__init__(self, game)
		self.game.player.hp = self.game.player_stats['hp']
		pygame.time.set_timer(self.game.events['SPAWN'], self.game.spawn_timer, 1)

		self.hp_render_img = pygame.image.load('Assets\\UI\\player_hp_sprites.png').convert_alpha()
		self.hp_render_rect = self.hp_render_img.get_rect()
		self.money_render_img = pygame.transform.scale(pygame.image.load('Assets\\UI\\player_money_sprites.png').convert_alpha(), (48,48))
		self.money_render_rect = self.money_render_img.get_rect()
		self.money_render_text = SwimState.MONEY_FONT.render(str(self.game.player_stats['money']), True, (0,0,0))
		self.money_render_text_rect = self.money_render_text.get_rect()
		self.run_time = pygame.time.get_ticks()
		self.initUI()

		self.goin = False
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
			new_state = PauseState(self.game)
			new_state.enter_state()

		self.game.backgroundManager.update(delta)
		self.game.obsManager.update(self.game.game_canvas, delta)
		self.game.player.update(self.game.game_canvas,self.game.obsManager.get_obstacles(), self.game.obsManager.get_coins(), self.game.obsManager.get_snorkle(), delta, self.game.player_stats['money_mult']+1)
		
		if self.game.player.hp <= 0:
			self.transition_state('DEAD')

		self.money_render_text = SwimState.MONEY_FONT.render(str(self.game.player.get_money()), True, (0,0,0))
		self.money_render_text_rect = self.money_render_text.get_rect()
		

		"""if elapsed >= 60:
			print("TIME END")
			self.game.playing = False
			self.game.state_stack.pop()
			new_state = ShopState(self.game)
			new_state.enter_state()"""


	def render(self, surface):
		if not self.goin:
			new_state = CountdownState(self.game)
			new_state.enter_state()
			self.goin = True
		surface.fill((0,153,153))
		self.game.backgroundManager.render(surface)
		self.game.obsManager.render(surface)
		self.game.player.render(surface)
		self.renderHPBar(surface)
		self.renderMoneyCounter(surface)

	def reset_play_space(self):
		self.game.player.reset_counters()

	def transition_state(self, state):
		match state:
			case 'DEAD':
				self.game.player_stats['money'] += self.game.player.get_money()
				self.game.player.reset(self.game.player_stats['hp'], 0)
				self.game.obsManager.reset()
				self.game.state_stack.pop()
				new_state = ShopEnterTransition(self.game)
				new_state.enter_state()

	def initUI(self):
		self.hp_render_rect.x = 20
		self.hp_render_rect.y = 4

		self.money_render_rect.x = self.game.WIDTH - self.money_render_rect.width - 20 - self.money_render_text_rect.width
		self.money_render_rect.y = 0
		self.money_render_text_rect.x = self.game.WIDTH - 20 - self.money_render_text_rect.width
		self.money_render_text_rect.y = 6

	def renderHPBar(self, surface):
		temp = pygame.Surface((5*128,128 )).convert_alpha()
		temp.blit(self.hp_render_img, (0,0), (0,0, 128 * self.game.player.get_hp(), 128))
		temp = pygame.transform.scale(temp, (48 * 5, 48))
		temp.set_colorkey((0,0,0))
		surface.blit(temp, self.hp_render_rect)

	def renderMoneyCounter(self, surface):
		self.money_render_rect.x = self.game.WIDTH - self.money_render_rect.width - 20 - self.money_render_text_rect.width
		self.money_render_text_rect.x = self.game.WIDTH - 20 - self.money_render_text_rect.width
		surface.blit(self.money_render_img, self.money_render_rect)
		surface.blit(self.money_render_text, self.money_render_text_rect)



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

	def update(self, events , delta):

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
		self.img = pygame.image.load('Assets\\Background\\shop_background_sprites.png').convert_alpha()
		self.img_rect = pygame.Rect(0,0,self.game.WIDTH, self.game.HEIGHT)
		self.index_y = 0
		self.store = []
		self.initItems()
		self.can_move = True
		self.player_money_render = ShopState.SHOP_FONT.render(str(self.game.player_stats['money']), True, (0,0,0))
		self.player_money_rect = self.player_money_render.get_rect()
		self.frame = 0

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
						#print("SPEED")
						self.game.increasePlayerSpeed()
					elif i == 1: #IF HP BOUGHT
						#print("HP")
						self.game.increasePlayerHP()
					elif i == 2: #IF NOODLE BOUGHT
						#print("NOODLE")
						self.game.increasePlayerMoneyMult()
				
				if i == 3: #IF SPEEDO BOUGHT
					self.game.state_stack.pop()
					new_state = ShopExitTransition(self.game)
					new_state.enter_state()

				self.can_move = False
				pygame.time.set_timer(ShopState.MENU_TIMER, 250, 1)	

		self.player_money_render = ShopState.SHOP_FONT.render(str(self.game.player_stats['money']), True, (0,0,0))
		self.updateItems()
		self.frame = (self.frame + 1) % (4 * 4)
	def render(self, surface):

		surface.blit(self.get_background(), self.img_rect)
		for ROW in range(ShopState.SHOP_ROW):
			for COLUMN in range(ShopState.SHOP_COL):
				if self.index_y == ROW and self.index_x == COLUMN:
					self.store[ROW*2+COLUMN].frame += 1 
				self.store[ROW*2+COLUMN].render(surface)

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

	def updateItems(self):
		for item in self.store:
			item.update()

	def get_background(self):
		surf = pygame.Surface((self.img.get_width()/8, self.img.get_height()))
		temp = not self.can_move
		frame_temp = self.frame//4
		surf.blit(self.img, (0,0), (temp * self.img.get_width()/2 + frame_temp*self.img.get_width()/8, 0, temp*self.img.get_width()/2 + (frame_temp+1)*self.img.get_width()/8, self.img.get_height()))
		surf = pygame.transform.scale(surf, (self.game.WIDTH, self.game.HEIGHT))
		return surf

class ShopEnterTransition(State):
	def __init__(self, game):
		self.img = pygame.image.load('Assets\\Background\\shop_background_enter.png').convert_alpha()
		self.game = game
		self.store = []
		self.initItems()
		self.frame = 0
		self.img_rect = pygame.Rect((0,0),(self.game.WIDTH,self.game.HEIGHT))

	def update(self, events, delta):
		self.frame = self.frame + 1
		if self.frame >= 48:
			self.game.state_stack.pop()
			new_state = ShopState(self.game)
			new_state.enter_state()


	def render(self, surface):
		surface.blit(self.get_background(), self.img_rect)
		for thing in self.store:
			thing.render(surface)

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

	def update(self, events, delta):
		self.frame = self.frame + 1
		if self.frame >= 60:
			self.game.state_stack.pop()
			new_state = SwimState(self.game)
			new_state.enter_state()


	def render(self, surface):
		surface.blit(self.get_background(), self.img_rect)
		for thing in self.store:
			thing.render(surface)

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
		self.frame = self.frame % (8 * 2) 

	def render(self, surface):
		self.progress_rect_border = pygame.Rect((self.img_rect.x, self.img_rect.y + self.img_rect.height), (ShopItem.ITEM_WIDTH, 20))
		#print(self.img_rect.width)
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
		temp = self.frame//8
		surf.blit(self.img, (0,0), (ShopItem.ITEM_WIDTH * temp, 0, ShopItem.ITEM_WIDTH * (temp + 1), ShopItem.ITEM_HEIGHT))
		surf.set_colorkey((0,0,0))
		return surf
