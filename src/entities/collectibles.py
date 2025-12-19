import random
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT
from src.entities.entity_base import Entity

RED = (255, 0, 0)
SILVER = (192, 192, 192)
YELLOW = (255, 255, 0)

class Collectible(Entity):
    def __init__(self, color, type_name, image_name):
        block_size = 50 
        cols = SCREEN_WIDTH // block_size
        rows = SCREEN_HEIGHT // block_size
        
        grid_x = random.randint(0, cols-1) * block_size
        grid_y = random.randint(1, rows-4) * block_size 
        
        super().__init__(grid_x, grid_y, 40, 40, color, image_name)
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
