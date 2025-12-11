import pygame
import random
import os
from src.config import *

class Entidade(pygame.sprite.Sprite):
    """
    Classe MÃE (Superclasse) Melhorada.
    Agora ela sabe lidar com imagens e redimensionamento sozinha.
    """
    def __init__(self, x, y, largura, altura, cor, nome_imagem=None):
        super().__init__()
        
        # Define a lógica: Tenta imagem -> Falha -> Usa Quadrado Colorido
        self.image = None
        
        if nome_imagem:
            try:
                # Monta o caminho: assets/img/nome_imagem
                caminho = os.path.join("assets", "img", nome_imagem)
                img_carregada = pygame.image.load(caminho).convert_alpha()
                # Redimensiona para o tamanho pedido
                self.image = pygame.transform.scale(img_carregada, (largura, altura))
            except Exception as e:
                # Se der erro (arquivo não existe), o self.image continua None
                # print(f"Aviso: Imagem '{nome_imagem}' não encontrada. Usando cor.")
                pass

        # Se a imagem não foi carregada (ou não foi pedida), cria o quadrado
        if self.image is None:
            self.image = pygame.Surface([largura, altura])
            self.image.fill(cor)

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Aluno(Entidade):
    def __init__(self, x, y):
        # Chama a mãe passando o nome do arquivo "aluno.png"
        super().__init__(x, y, 40, 40, AZUL_UFPE, "aluno.png")
        self.velocidade_x = 0
        self.velocidade_y = 0
        self.pontos = 0
        self.vida = 100
    
    def update(self):
        self.rect.x += self.velocidade_x
        self.rect.y += self.velocidade_y

        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > LARGURA_TELA: self.rect.right = LARGURA_TELA
        if self.rect.top < 0: self.rect.top = 0
        if self.rect.bottom > ALTURA_TELA: self.rect.bottom = ALTURA_TELA

    def mover(self, dx, dy):
        self.velocidade_x = dx
        self.velocidade_y = dy

# --- COLETÁVEIS (Agora com imagens!) ---

class Coletavel(Entidade):
    def __init__(self, cor, tipo, nome_imagem):
        x = random.randint(50, LARGURA_TELA - 50)
        y = random.randint(50, ALTURA_TELA - 200) 
        # Passa a imagem para a classe Mãe
        super().__init__(x, y, 30, 30, cor, nome_imagem)
        self.tipo = tipo

class Cracha(Coletavel):
    def __init__(self):
        super().__init__((255, 215, 0), "cracha", "cracha.png")

class Comida(Coletavel):
    def __init__(self):
        super().__init__((0, 255, 0), "comida", "comida.png")

class Raio(Coletavel):
    def __init__(self):
        super().__init__((128, 0, 128), "raio", "raio.png")

# --- OBSTÁCULOS (Agora com imagem do Circular!) ---

class Obstaculo(Entidade):
    def __init__(self):
        lado = random.choice(["esquerda", "direita"])
        y = random.randint(50, ALTURA_TELA - 150)
        
        if lado == "esquerda":
            x = -100
            velocidade = random.randint(3, 7)
            img_nome = "onibus_dir.png" # Sugestão: ônibus virado pra direita
        else:
            x = LARGURA_TELA + 100
            velocidade = random.randint(-7, -3)
            img_nome = "onibus.png" # Ônibus padrão

        # Se não tiver a imagem "onibus_dir.png", ele vai usar "onibus.png" se você quiser tratar depois
        # Por enquanto vamos usar "onibus.png" para os dois e o PyGame vira a imagem se precisar (explicarei depois)
        
        super().__init__(x, y, 80, 40, VERMELHO, "onibus.png")
        self.velocidade_x = velocidade

        # Espelhar a imagem se vier da esquerda (opcional, visual)
        if velocidade > 0 and self.image: 
             self.image = pygame.transform.flip(self.image, True, False)

    def update(self):
        self.rect.x += self.velocidade_x
        if self.rect.right < -150 or self.rect.left > LARGURA_TELA + 150:
            self.kill()