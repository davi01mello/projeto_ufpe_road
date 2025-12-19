import pygame
import random
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT
from src.entities.entity_base import Entity

class Obstacle(Entity):
    def __init__(self, type_name="carro", speed_multiplier=1.0, fixed_y=None, fixed_direction=None):
        """
        fixed_y: Se informado, força o obstáculo a nascer nessa altura.
        fixed_direction: "left" ou "right". Se informado, força a direção.
        """
        if fixed_y is not None:
            lane_y = fixed_y
        else:
            lane_y = random.randint(1, 10) * 50 

        if type_name == "circular":
            base_speed = random.randint(7, 10)
            img = "onibus.png"
            w, h = 100, 50
        elif type_name == "obra":
            base_speed = 0
            img = "cone.png"
            w, h = 40, 40
            side = "middle" 
        else: 
            base_speed = random.randint(3, 6)
            img = "carro.png"
            w, h = 80, 50

        if type_name == "obra":
            speed = 0
            start_x = random.randint(50, SCREEN_WIDTH - 50)
        else:
            if fixed_direction:
                side = fixed_direction
            else:
                side = random.choice(["left", "right"])

            final_speed = base_speed * speed_multiplier
            
            if side == "left":
                start_x = SCREEN_WIDTH + 50
                speed = -final_speed 
            else:
                start_x = -50 
                speed = final_speed

        super().__init__(start_x, lane_y, w, h, (255, 0, 0), img)
        
        self.original_speed = speed

        if speed > 0 and self.image and type_name != "obra":
             self.image = pygame.transform.flip(self.image, True, False)

    def update(self, slow_motion_active=False):
        current_speed = self.original_speed * 0.5 if slow_motion_active else self.original_speed
        self.rect.x += current_speed

        if self.rect.right < -150 or self.rect.left > SCREEN_WIDTH + 150:
            self.kill()

class Deadline(Entity):
    def __init__(self):
        super().__init__(0, SCREEN_HEIGHT + 50, SCREEN_WIDTH, 50, (0, 0, 0), "deadline.png")
        self.image = pygame.Surface((SCREEN_WIDTH, 50))
        self.image.set_alpha(150)
        self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = SCREEN_HEIGHT + 50
        self.speed = 0.5

    def update(self, scroll_y=0):
        self.rect.y -= self.speed
        self.rect.y += scroll_y
