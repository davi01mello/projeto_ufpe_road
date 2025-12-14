# src/config.py
import pygame

# Configurações da Tela
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TITLE = "CIn Road: Rumo ao Diploma"

# Configurações da Grade (Grid)
BLOCK_SIZE = 50 
GRID_WIDTH = SCREEN_WIDTH // BLOCK_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // BLOCK_SIZE

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)
BLUE = (0, 0, 255)

# Sombra dos textos
SHADOWCOLOR = (0, 0, 0)
OFFSET = 4
OFFSET_SMALL = 2

# FPS
FPS = 60

# --- MUDANÇA AQUI ---
# Meta aumentada para 100 passos (Jornada Longa)
GOAL_DISTANCE = 100