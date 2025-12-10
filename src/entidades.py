import pygame
import random
from src.config import *

class Entidade(pygame.sprite.Sprite):
    def __init__(self, x, y, largura, altura, cor):
        super().__init__()
        self.image = pygame.Surface([largura, altura])
        self.image.fill(cor)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Aluno(Entidade):
    def __init__(self, x, y):
        # Cria o quadrado AZUL (o Jogador)
        super().__init__(x, y, 40, 40, AZUL_UFPE)
        self.velocidade_x = 0
        self.velocidade_y = 0
        self.pontos = 0
        self.vida = 100
    
    def update(self):
        # AQUI ESTÁ A MÁGICA: Atualiza a posição baseado na velocidade
        self.rect.x += self.velocidade_x
        self.rect.y += self.velocidade_y
        
        # Impede de sair da tela
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > LARGURA_TELA: self.rect.right = LARGURA_TELA
        if self.rect.top < 0: self.rect.top = 0
        if self.rect.bottom > ALTURA_TELA: self.rect.bottom = ALTURA_TELA

    def mover(self, dx, dy):
        # Altera a velocidade
        self.velocidade_x = dx
        self.velocidade_y = dy

# --- CLASSES DOS COLETÁVEIS ---

class Coletavel(Entidade):
    def __init__(self, cor, tipo):
        x = random.randint(50, LARGURA_TELA - 50)
        y = random.randint(50, ALTURA_TELA - 200) 
        super().__init__(x, y, 20, 20, cor)
        self.tipo = tipo

class Cracha(Coletavel):
    def __init__(self):
        super().__init__((255, 215, 0), "cracha") # Amarelo

class Comida(Coletavel):
    def __init__(self):
        super().__init__((0, 255, 0), "comida") # Verde

class Raio(Coletavel):
    def __init__(self):
        super().__init__((128, 0, 128), "raio") # Roxo