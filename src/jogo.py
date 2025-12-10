import pygame
import sys
from src.config import *
from src.entidades import Aluno

class Game:
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
        pygame.display.set_caption(TITULO_JOGO)
        self.relogio = pygame.time.Clock()
        self.rodando = True

        # Grupos de Sprites (para desenhar tudo de uma vez)
        self.todos_sprites = pygame.sprite.Group()
        
        # Criando o Jogador (Instanciando a classe)
        self.jogador = Aluno(LARGURA_TELA // 2, ALTURA_TELA - 100)
        self.todos_sprites.add(self.jogador)

    def eventos(self):
        """Captura cliques e teclas"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.rodando = False
            
            # Movimentação (Teclado)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.jogador.mover(-5, 0)
                if event.key == pygame.K_RIGHT:
                    self.jogador.mover(5, 0)
                if event.key == pygame.K_UP:
                    self.jogador.mover(0, -5)
                if event.key == pygame.K_DOWN:
                    self.jogador.mover(0, 5)

            if event.type == pygame.KEYUP:
                if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                    self.jogador.mover(0, 0)
                if event.key in [pygame.K_UP, pygame.K_DOWN]:
                    self.jogador.mover(0, 0)

    def atualizar(self):
        """Atualiza a lógica do jogo"""
        self.todos_sprites.update()

    def desenhar(self):
        """Desenha na tela"""
        self.tela.fill(BRANCO) # Limpa a tela
        self.todos_sprites.draw(self.tela) # Desenha todos os objetos
        pygame.display.flip() # Atualiza o display

    def rodar(self):
        """Loop Principal do Jogo"""
        while self.rodando:
            self.eventos()
            self.atualizar()
            self.desenhar()
            self.relogio.tick(FPS)
        
        pygame.quit()
        sys.exit()