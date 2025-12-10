import pygame
from src.config import *

class Entidade(pygame.sprite.Sprite):
    """
    Classe MÃE (Superclasse).
    Todos os objetos do jogo (jogador, inimigos, itens) herdarão daqui.
    """
    def init(self, x, y, largura, altura, cor):
        super().init()
        # Cria um quadrado simples (placeholder para imagem futura)
        self.image = pygame.Surface([largura, altura])
        self.image.fill(cor)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Aluno(Entidade):
    """
    Classe do Jogador. Herda de Entidade.
    Possui lógica específica de movimento.
    """
    def init(self, x, y):
        # Chama o construtor da mãe (cria o quadrado AZUL)
        super().init(x, y, 40, 40, AZUL_UFPE)
        self.velocidade_x = 0
        self.velocidade_y = 0
        self.vida = 100

    def update(self):
        """Atualiza a posição do aluno a cada frame"""
        self.rect.x += self.velocidade_x
        self.rect.y += self.velocidade_y

        # Impede de sair da tela (Colisão com bordas)
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > LARGURA_TELA: self.rect.right = LARGURA_TELA
        if self.rect.top < 0: self.rect.top = 0
        if self.rect.bottom > ALTURA_TELA: self.rect.bottom = ALTURA_TELA

    def mover(self, dx, dy):
        """Método para controlar o movimento"""
        self.velocidade_x = dx
        self.velocidade_y = dy