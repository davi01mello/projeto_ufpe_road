import pygame

# Configurações da Tela
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TITLE = "CIn Road: Rumo ao Diploma"

# Configurações da Grade (Grid)
BLOCK_SIZE = 50 
GRID_WIDTH = SCREEN_WIDTH // BLOCK_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // BLOCK_SIZE

# FPS
FPS = 60

# Meta de Distância
GOAL_DISTANCE = 100

MIN_CRACHAS = 6

# Cores (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)        # Verde Grama
CINZA_ESTRADA = (50, 50, 50) # Cinza Asfalto
BLUE = (0, 0, 255)           # Azul Player
RED = (255, 0, 0)            # Vermelho Vidas/Game Over