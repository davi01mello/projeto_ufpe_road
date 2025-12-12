import pygame
import random
from src.config import SCREEN_WIDTH, CINZA_ESTRADA 
from src.entities.entity_base import Entity 

class Obstacle(Entity):
    def __init__(self, y_pos, type_name="carro", speed_multiplier=1.0):
        
        # --- Configurações por Tipo ---
        if type_name == "circular":
            base_speed = 7
            img = "onibus.png"
            w, h = 100, 40
            movimento = "normal"
        elif type_name == "obra":
            base_speed = 0  # Obra não anda
            img = "cone.png"
            w, h = 40, 40
            movimento = "estatico"
        else: # carro padrão
            base_speed = 5
            img = "carro.png"
            w, h = 80, 40
            movimento = "normal"

        # --- Lógica de Posição e Velocidade ---
        if movimento == "estatico":
            # Obra: Posição X aleatória na pista, Velocidade 0
            start_x = random.randint(50, SCREEN_WIDTH - 50)
            self.speed = 0
        else:
            # Veículos: Decide lado e aplica velocidade
            final_speed = base_speed * speed_multiplier
            side = random.choice(["left", "right"])
            
            if side == "left":
                start_x = -100
                self.speed = final_speed
            else:
                start_x = SCREEN_WIDTH + 100
                self.speed = -final_speed

        # --- Chama a Classe Pai ---
        super().__init__(start_x, y_pos, w, h, (255, 0, 0), img)
        
        # Vira a imagem se necessário
        if self.speed > 0 and self.image:
             self.image = pygame.transform.flip(self.image, True, False)

    def update(self):
        self.rect.x += self.speed
        
        # Remove se sair da tela (apenas se estiver andando)
        if self.speed != 0:
            if self.rect.right < -150 or self.rect.left > SCREEN_WIDTH + 150:
                self.kill()