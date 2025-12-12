import pygame
import os
# Ajuste o import conforme onde seu config estiver
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, BLOCK_SIZE

class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color, image_name=None):
        super().__init__()
        self.image = None
        
        # Lógica de carregar imagem (Preservada do seu código)
        if image_name:
            try:
                path = os.path.join("assets", "img", image_name)
                loaded_img = pygame.image.load(path).convert_alpha()
                self.image = pygame.transform.scale(loaded_img, (width, height))
            except Exception as e:
                print(f"Erro ao carregar {image_name}: {e}")
                pass 
        
        # Fallback: Se não tiver imagem, cria um quadrado colorido
        if self.image is None:
            self.image = pygame.Surface([width, height])
            self.image.fill(color)
            
        self.rect = self.image.get_rect()
        
        # Importante: No Crossy Road, guardamos a posição na GRADE também
        self.rect.x = x
        self.rect.y = y