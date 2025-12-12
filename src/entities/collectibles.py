import pygame
import random
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, BLOCK_SIZE
from src.entities.entity_base import Entity

# Cores para fallback
RED = (255, 0, 0)
SILVER = (192, 192, 192)
YELLOW = (255, 255, 0)

class Collectible(Entity):
    def __init__(self, color, type_name, image_name):
        # Gera uma posição X aleatória alinhada à grade
        cols = SCREEN_WIDTH // BLOCK_SIZE
        grid_x = random.randint(0, cols-1) * BLOCK_SIZE
        
        # O Y será definido pelo jogo ao criar o item, então começamos com 0
        start_y = 0 
        
        super().__init__(grid_x, start_y, 40, 40, color, image_name)
        self.type = type_name

class BadgeFragment(Collectible):
    def __init__(self):
        super().__init__(RED, "fragmento", "cracha.png")

class EnergyDrink(Collectible):
    def __init__(self):
        super().__init__(SILVER, "energetico", "raio.png")

class Shield(Collectible):
    def __init__(self):
        super().__init__(YELLOW, "escudo", "capacete.png")