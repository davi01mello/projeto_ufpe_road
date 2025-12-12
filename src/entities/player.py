import pygame
from src.config import BLOCK_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
from src.entities.entity_base import Entity

class Player(Entity):
    def __init__(self, start_grid_x, start_grid_y):
        x_pixel = start_grid_x * BLOCK_SIZE
        y_pixel = start_grid_y * BLOCK_SIZE
        
        super().__init__(x_pixel, y_pixel, BLOCK_SIZE, BLOCK_SIZE, (0, 0, 255), "aluno.png")
        
        # Guarda a imagem original para poder desvirar
        self.original_image = self.image 
        self.facing_right = True # Começa olhando pra direita/frente

        self.grid_x = start_grid_x
        self.grid_y = start_grid_y
        
        self.lives = 3             
        self.has_shield = False    

    def move(self, dx, dy):
        """Movimenta e vira o sprite"""
        
        # --- Lógica de Virar (Animação) ---
        if dx < 0 and self.facing_right:
            # Se for pra esquerda e tá olhando pra direita: vira
            self.image = pygame.transform.flip(self.original_image, True, False)
            self.facing_right = False
        elif dx > 0 and not self.facing_right:
            # Se for pra direita e tá olhando pra esquerda: desvira
            self.image = self.original_image
            self.facing_right = True
        # ----------------------------------

        new_x = self.grid_x + dx
        new_y = self.grid_y + dy

        max_cols = SCREEN_WIDTH // BLOCK_SIZE
        max_rows = SCREEN_HEIGHT // BLOCK_SIZE

        if 0 <= new_x < max_cols and 0 <= new_y < max_rows:
            self.grid_x = new_x
            self.grid_y = new_y
            self.rect.x = self.grid_x * BLOCK_SIZE
            self.rect.y = self.grid_y * BLOCK_SIZE

    def reset_position(self):
        self.grid_x = (SCREEN_WIDTH // BLOCK_SIZE) // 2
        self.grid_y = (SCREEN_HEIGHT // BLOCK_SIZE) - 1
        self.rect.x = self.grid_x * BLOCK_SIZE
        self.rect.y = self.grid_y * BLOCK_SIZE
        
        # Reseta a imagem
        self.image = self.original_image
        self.facing_right = True

    def check_damage(self):
        if self.has_shield:
            print("🛡️ ESCUDO PROTEGEU!")
            self.has_shield = False
            return False
        else:
            self.lives -= 1
            print(f"💔 DANO! Vidas restantes: {self.lives}")
            return True