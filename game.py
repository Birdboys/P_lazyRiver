import pygame
import os
import random
from player import Player
from obstacle import Obstacle
from obstacleManager import ObstacleManager
from state import *

class Game:

	SPAWN_OBSTACLE = pygame.USEREVENT+1
	pygame.display.set_caption("Lazy River")
	BACKGROUND_COLOR = (0,153,153)
	FPS = 60
	clock = pygame.time.Clock()

	PLAYER_WIDTH = 60
	PLAYER_HEIGHT = 60


	def __init__(self):
		pygame.init()
		self.WIDTH, self.HEIGHT = 400, 800
		self.WIN = pygame.display.set_mode((self.WIDTH,self.HEIGHT))
		self.game_canvas = pygame.Surface((self.WIDTH, self.HEIGHT))

		self.player = Player(self.WIDTH,self.HEIGHT)
		self.obsManager = ObstacleManager(self.game_canvas, self.WIDTH, self.HEIGHT)

		self.player_stats = {'hp':5,'money':20,'max_vel_x':4, 'max_vel_y':3,'noodle_upgrade':0, 'speedo_upgrade':0}
		self.playing = True
		self.running = True
		self.state_stack = [TitleState(self)]
		self.prev_state = None
		self.spawn_timer = 2000
		self.events = {'SPAWN':Game.SPAWN_OBSTACLE}
		self.spawn_buffer = 0

	def update(self, events):
		self.state_stack[-1].update(events)

	def render(self, events):
		self.state_stack[-1].render(self.game_canvas)
		self.WIN.blit(self.game_canvas,(0,0))
		pygame.display.update()

	def game_loop(self):
		Game.clock.tick(Game.FPS)
		events = pygame.event.get()
		self.update(events)
		self.render(self.WIN)

	def increasePlayerSpeed(self):
		self.player_stats['max_vel_x'] = self.player_stats['max_vel_x'] + 1
		self.player_stats['max_vel_y'] = self.player_stats['max_vel_y'] + 1
		self.player.updateSpeed(self.player_stats['max_vel_x'])

	def increasePlayerHP(self):
		self.player_stats['hp'] = self.player_stats['hp'] + 1

	def noodleObtained(self):
		self.player_stats['noodle_upgrade'] = 1 

	def speedoObtained(self):
		self.player_stats['speedo_upgrade'] = 1
