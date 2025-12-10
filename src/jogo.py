import pygame
import sys
import random
from src.config import *
from src.entidades import Aluno, Cracha, Comida, Raio

class Game:
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
        pygame.display.set_caption(TITULO_JOGO)
        self.relogio = pygame.time.Clock()
        self.rodando = True

        # Grupos de Sprites
        self.todos_sprites = pygame.sprite.Group()
        self.coletaveis = pygame.sprite.Group()
        
        # Criar o JOGADOR e adicionar ao grupo
        self.jogador = Aluno(LARGURA_TELA // 2, ALTURA_TELA - 100)
        self.todos_sprites.add(self.jogador)

        # Criar itens iniciais
        for _ in range(5):
            self.criar_coletavel()

    def criar_coletavel(self):
        classe_item = random.choice([Cracha, Comida, Raio])
        item = classe_item()
        self.todos_sprites.add(item)
        self.coletaveis.add(item)

    def eventos(self):
        # Captura as teclas
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.rodando = False
            
            # Quando APERTA a tecla
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.jogador.mover(-5, 0)
                if event.key == pygame.K_RIGHT:
                    self.jogador.mover(5, 0)
                if event.key == pygame.K_UP:
                    self.jogador.mover(0, -5)
                if event.key == pygame.K_DOWN:
                    self.jogador.mover(0, 5)

            # Quando SOLTA a tecla (para o boneco parar)
            if event.type == pygame.KEYUP:
                if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                    self.jogador.velocidade_x = 0
                if event.key in [pygame.K_UP, pygame.K_DOWN]:
                    self.jogador.velocidade_y = 0

    def atualizar(self):
        # Atualiza a posição de todos os sprites
        self.todos_sprites.update()

        # Checa colisão
        hits = pygame.sprite.spritecollide(self.jogador, self.coletaveis, True)
        for hit in hits:
            print(f"Pegou item: {hit.tipo}")
            self.criar_coletavel()

    def desenhar(self):
        self.tela.fill(BRANCO)
        self.todos_sprites.draw(self.tela)
        pygame.display.flip()

    def rodar(self):
        while self.rodando:
            self.eventos()
            self.atualizar()
            self.desenhar()
            self.relogio.tick(FPS)
        pygame.quit()
        sys.exit()