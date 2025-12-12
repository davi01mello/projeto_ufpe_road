import pygame
import random
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT
from src.entities.entity_base import Entity

class Obstacle(Entity):
    def __init__(self, type_name="carro", speed_multiplier=1.0):
        side = random.choice(["left", "right"])
        lane_y = random.randint(1, 10) * 50 
        
        if type_name == "circular":
            base_speed = random.randint(7, 10)
            img = "onibus.png"
            w, h = 100, 50
        elif type_name == "obra":
            base_speed = 0
            img = "cone.png"
            w, h = 40, 40
            start_x = random.randint(50, SCREEN_WIDTH - 50)
            side = "middle" 
        else: # Carro normal
            base_speed = random.randint(3, 6)
            img = "carro.png"
            w, h = 80, 50

        # Aplica o multiplicador de dificuldade na velocidade base
        final_speed = base_speed * speed_multiplier

        if side == "left":
            start_x = -100
            speed = final_speed
        elif side == "right":
            start_x = SCREEN_WIDTH + 100
            speed = -final_speed
        elif side == "middle":
            speed = 0
            start_x = random.randint(0, SCREEN_WIDTH)

        super().__init__(start_x, lane_y, w, h, (255, 0, 0), img)
        
        self.original_speed = speed
        
        if speed > 0 and self.image and type_name != "obra":
             self.image = pygame.transform.flip(self.image, True, False)

    def update(self, slow_motion_active=False):
        current_speed = self.original_speed * 0.5 if slow_motion_active else self.original_speed
        self.rect.x += current_speed

        if self.rect.right < -150 or self.rect.left > SCREEN_WIDTH + 150:
            self.kill()