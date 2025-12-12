# src/config.py
import pygame

# Configurações da Tela
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TITLE = "CIn Road: Rumo ao Diploma"

# Configurações da Grade (Grid)
# O tamanho do "pulo". 40x40 ou 50x50 costuma ser bom.
BLOCK_SIZE = 50 
GRID_WIDTH = SCREEN_WIDTH // BLOCK_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // BLOCK_SIZE

# Cores (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 139, 34) # Cor da grama (provisório)
BLUE = (0, 0, 255)    # Cor do Player (provisório)

# FPS
FPS = 60
# Adicione no final do arquivo src/config.py

# Meta: Quantos "passos" de grid até o CIn?
# 50 passos * 50 pixels = mapa de 2500 pixels de altura
GOAL_DISTANCE = 50