import pygame
import os

WIDTH, HEIGHT = 400, 800
PLAYER_WIDTH, PLAYER_HEIGHT = 50, 50
WIN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Lazy River")

FPS = 60
clock = pygame.time.Clock()

BACKGROUND_COLOR = (0,153,153)
class Player:

	MAX_VEL_X = 7
	ACCELERATION_X = 1
	ACCELERATION_Y = 1.5
	DESCELERATION_Y = -1
	DESCELERATION_X = 0.3
	CURRENT_LINES = {(0,200):-1,(200,400):-1.2,(400,600):-1.4,(600,800):-1.6}
	MAX_VEL_Y = 5
	MAX_BACK_VEL_Y = -2

	def __init__(self):
		self.img = pygame.transform.scale(pygame.image.load('Assets/temp_player.png').convert_alpha(),(PLAYER_WIDTH,PLAYER_HEIGHT))
		self.rect = pygame.Rect(WIDTH//2 - PLAYER_WIDTH//2, 10, PLAYER_WIDTH, PLAYER_HEIGHT)
		self.vel_x = 0
		self.vel_y = 0
		self.current = 0

	def update(self,screen):

		self.descelerate()
		self.rect.x += self.vel_x
		self.rect.y += self.vel_y

		self.border_check()

		self.render(screen)

	def render(self, screen):
		screen.blit(self.img, self.rect)

	def key_down(self, key):
		match key:
			case 'a':
				self.vel_x -= Player.ACCELERATION_X 
				if self.vel_x < -Player.MAX_VEL_X:
					self.vel_x = -Player.MAX_VEL_X 
				
			case 'd':
				self.vel_x += Player.ACCELERATION_X
				if self.vel_x > Player.MAX_VEL_X:
					self.vel_x = Player.MAX_VEL_X

			case 's':
				self.vel_y += Player.ACCELERATION_Y
				if self.vel_y > Player.MAX_VEL_Y:
					self.vel_y = Player.MAX_VEL_Y

			case 'w':
				self.vel_y -= Player.ACCELERATION_Y
				if self.vel_y < Player.MAX_BACK_VEL_Y:
					self.vel_y = Player.MAX_BACK_VEL_Y

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
			if self.vel_y < Player.MAX_BACK_VEL_Y:
				self.vel_y = Player.MAX_BACK_VEL_Y

	def border_check(self):
		if self.rect.y < 0:
			self.rect.y = 0
			self.vel_y = 0
		if self.rect.x < 0:
			self.rect.x = 0
		if self.rect.x + PLAYER_WIDTH > WIDTH:
			self.rect.x = WIDTH - PLAYER_WIDTH

#GAME LOOP
player = Player()
running = True
while running:

	clock.tick(FPS)
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

		

		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_a or event.key == pygame.K_d:
				player.key_down(event.key)

	keys_pressed = pygame.key.get_pressed()
	if keys_pressed[pygame.K_a]:
		player.key_down('a')
	if keys_pressed[pygame.K_d]:
		player.key_down('d')
	if keys_pressed[pygame.K_s]:
		player.key_down('s')
	if keys_pressed[pygame.K_w]:
		player.key_down('w')

	WIN.fill(BACKGROUND_COLOR)
	player.update(WIN)
	pygame.display.update()