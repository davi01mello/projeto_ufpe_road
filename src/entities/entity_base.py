import pygame
import os
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, BLOCK_SIZE

class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color, image_name=None):
        super().__init__()
        self.image = None

        if image_name:
            try:
                path = os.path.join("assets", "img", image_name)
                loaded_img = pygame.image.load(path).convert_alpha()
                self.image = pygame.transform.scale(loaded_img, (width, height))
            except Exception as e:
                print(f"Erro ao carregar {image_name}: {e}")
                pass 

        if self.image is None:
            self.image = pygame.Surface([width, height])
            self.image.fill(color)
            
        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y
