import pygame
from src.config import BLOCK_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
from src.entities.entity_base import Entity

class Player(Entity):
    def __init__(self, start_grid_x, start_grid_y):
        # Converte grade para pixels
        x_pixel = start_grid_x * BLOCK_SIZE
        y_pixel = start_grid_y * BLOCK_SIZE
        
        super().__init__(x_pixel, y_pixel, BLOCK_SIZE, BLOCK_SIZE, (0, 0, 255), "aluno.png")
        
        # Posição Lógica
        self.grid_x = start_grid_x
        self.grid_y = start_grid_y
        
        # Atributos
        self.lives = 3             
        self.has_shield = False    

    def move(self, dx, dy):
        """Movimenta na Grade"""
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
        """Volta o jogador para o início (usado quando perde vida)"""
        self.grid_x = (SCREEN_WIDTH // BLOCK_SIZE) // 2
        self.grid_y = (SCREEN_HEIGHT // BLOCK_SIZE) - 1
        self.rect.x = self.grid_x * BLOCK_SIZE
        self.rect.y = self.grid_y * BLOCK_SIZE

    def check_damage(self):
        """
        Verifica a lógica de dano.
        Retorna True se tomou dano real (perde vida e reseta).
        Retorna False se o escudo protegeu.
        """
        if self.has_shield:
            print("🛡️ ESCUDO PROTEGEU!")
            self.has_shield = False # Quebra o escudo
            return False # Não sofreu dano real
        else:
            self.lives -= 1
            print(f"💔 DANO! Vidas restantes: {self.lives}")
            return True # Sofreu dano real