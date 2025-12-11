import pygame
import random
import os
from src.config import *

class Entidade(pygame.sprite.Sprite):
    def __init__(self, x, y, largura, altura, cor, nome_imagem=None):
        super().__init__()
        self.image = None
        if nome_imagem:
            try:
                caminho = os.path.join("assets", "img", nome_imagem)
                img_carregada = pygame.image.load(caminho).convert_alpha()
                self.image = pygame.transform.scale(img_carregada, (largura, altura))
            except Exception:
                pass 
        if self.image is None:
            self.image = pygame.Surface([largura, altura])
            self.image.fill(cor)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Aluno(Entidade):
    def __init__(self, x, y):
        super().__init__(x, y, 40, 40, AZUL_UFPE, "aluno.png")
        self.velocidade = 5 
        self.velocidade_x = 0
        self.velocidade_y = 0
        
        # --- NOVOS ATRIBUTOS (Inventário) ---
        self.vida = 3             # Vidas discretas (3 corações)
        self.fragmentos = 0       # Meta: chegar a 4
        self.tem_escudo = False   # Se True, ignora o próximo dano
    
    def update(self):
        self.rect.x += self.velocidade_x
        self.rect.y += self.velocidade_y

        # Limites da tela
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > LARGURA_TELA: self.rect.right = LARGURA_TELA
        if self.rect.top < 0: self.rect.top = 0
        if self.rect.bottom > ALTURA_TELA: self.rect.bottom = ALTURA_TELA

    def mover(self, dx, dy):
        if dx != 0: self.velocidade_x = self.velocidade * (1 if dx > 0 else -1)
        else: self.velocidade_x = 0 
        if dy != 0: self.velocidade_y = self.velocidade * (1 if dy > 0 else -1)
        else: self.velocidade_y = 0

    def receber_dano(self):
        """Lógica do Escudo: Se tiver escudo, perde o escudo. Se não, perde vida."""
        if self.tem_escudo:
            print("🛡️ ESCUDO QUEBROU! (Mas você sobreviveu)")
            self.tem_escudo = False
            return False # Retorna False (não morreu/não perdeu vida real)
        else:
            self.vida -= 1
            print(f"💔 DANO! Vidas restantes: {self.vida}")
            return True # Retorna True (tomou dano real)

# --- NOVOS ITENS (Requisitos do CIn) ---

class Coletavel(Entidade):
    def __init__(self, cor, tipo, nome_imagem):
        x = random.randint(50, LARGURA_TELA - 50)
        y = random.randint(50, ALTURA_TELA - 200) 
        super().__init__(x, y, 30, 30, cor, nome_imagem)
        self.tipo = tipo

class FragmentoCracha(Coletavel):
    def __init__(self):
        # Vermelho (Cartão do CIn)
        super().__init__((255, 0, 0), "fragmento", "cracha.png")

class Energetico(Coletavel):
    def __init__(self):
        # Prata (Lata) - Efeito Matrix
        super().__init__((192, 192, 192), "energetico", "energetico.png")

class Escudo(Coletavel):
    def __init__(self):
        # Amarelo (Capacete de Obra)
        super().__init__((255, 255, 0), "escudo", "capacete.png")

# --- OBSTÁCULOS INTELIGENTES ---

class Obstaculo(Entidade):
    def __init__(self, tipo="carro"):
        lado = random.choice(["esquerda", "direita"])
        y = random.randint(50, ALTURA_TELA - 150)
        
        # Configuração baseada no tipo
        if tipo == "circular":
            velocidade_base = random.randint(7, 10) # Rápido
            img = "onibus.png"
            largura, altura = 80, 40
        elif tipo == "obra":
            velocidade_base = 0 # Parado
            img = "cone.png"
            largura, altura = 40, 40
            x = random.randint(50, LARGURA_TELA - 50) # Obra spawna no meio da rua
            lado = "meio" 
        else: # Carro normal
            velocidade_base = random.randint(3, 6)
            img = "carro.png"
            largura, altura = 50, 30

        if lado == "esquerda":
            x = -100
            velocidade = velocidade_base
        elif lado == "direita":
            x = LARGURA_TELA + 100
            velocidade = -velocidade_base
        
        super().__init__(x, y, largura, altura, VERMELHO, img)
        
        self.velocidade_original = velocidade
        self.velocidade_atual = velocidade

        if velocidade > 0 and self.image and tipo != "obra":
             self.image = pygame.transform.flip(self.image, True, False)

    def update(self, slow_motion_ativo=False):
        # Lógica Matrix: Se slow motion ativo, velocidade cai pela metade
        if slow_motion_ativo:
            self.rect.x += self.velocidade_original * 0.5
        else:
            self.rect.x += self.velocidade_original

        # Remove se sair da tela
        if self.rect.right < -150 or self.rect.left > LARGURA_TELA + 150:
            self.kill()