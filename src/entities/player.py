import pygame
import os
from src.config import BLOCK_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
from src.entities.entity_base import Entity

class Player(Entity):
    def __init__(self, start_grid_x, start_grid_y, skin_filename):
        super().__init__(start_grid_x * BLOCK_SIZE, start_grid_y * BLOCK_SIZE, 
                         BLOCK_SIZE, BLOCK_SIZE, (0, 0, 255), None)
        
        self.grid_x = start_grid_x
        self.grid_y = start_grid_y
        
        self.lives = 3             
        self.has_shield = False    

        self.invulnerable_timer = 0 

        self.images = {} 
        self.current_direction = None 
        
        base_name = skin_filename.replace("frente.png", "")
        self._load_all_images(base_name)
        
        self.update_sprite("front")
        
        self.rect = self.image.get_rect()
        self.rect.x = self.grid_x * BLOCK_SIZE
        self.rect.y = self.grid_y * BLOCK_SIZE

    def _load_all_images(self, base_name):
        suffixes = {
            "front": "frente.png",
            "back":  "costas.png",
            "side":  "lado.png"
        }

        for direction, suffix in suffixes.items():
            full_name = base_name + suffix
            try:
                path = os.path.join("assets", "img", full_name)
                loaded_img = pygame.image.load(path).convert_alpha()
                scaled_img = pygame.transform.scale(loaded_img, (BLOCK_SIZE, BLOCK_SIZE))
                self.images[direction] = scaled_img
            except Exception as e:
                surf = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
                surf.fill((255, 0, 0))
                self.images[direction] = surf

    def update_sprite(self, direction, flip_x=False):
        state_id = f"{direction}_{flip_x}"
        if self.current_direction != state_id:
            img = self.images.get(direction)
            if img:
                if flip_x:
                    self.image = pygame.transform.flip(img, True, False)
                else:
                    self.image = img
            self.current_direction = state_id

    def move(self, dx, dy):
        if dx > 0:   self.update_sprite("side", flip_x=False)
        elif dx < 0: self.update_sprite("side", flip_x=True)
        elif dy < 0: self.update_sprite("back")
        elif dy > 0: self.update_sprite("front")

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
        self.update_sprite("front")

        self.invulnerable_timer = 120 

    def check_damage(self):
        """Retorna True se tomou dano real, False se foi protegido"""

        if self.invulnerable_timer > 0:
            return False

        if self.has_shield:
            print("🛡️ ESCUDO PROTEGEU!")
            self.has_shield = False 
            self.invulnerable_timer = 60 
            return False 

        else:
            self.lives -= 1
            print(f"💔 DANO! Vidas restantes: {self.lives}")
            self.invulnerable_timer = 120 
            return True 

    def update(self):
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= 1

            if (self.invulnerable_timer // 5) % 2 == 0:
                self.image.set_alpha(50) 
            else:
                self.image.set_alpha(255) 
        else:
            self.image.set_alpha(255)
