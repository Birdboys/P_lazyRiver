import pygame
import os
from game import Game

g = Game()
while g.running:
	g.game_loop()
