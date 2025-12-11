import pygame
import sys
import random
from src.config import *
from src.entidades import Aluno, Cracha, Comida, Raio, Obstaculo

class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        
        self.tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
        pygame.display.set_caption(TITULO_JOGO)
        self.relogio = pygame.time.Clock()
        self.rodando = True
        
        # Estados do Jogo
        self.estado = "MENU" # Pode ser: MENU, JOGANDO, GAME_OVER

        # Fontes
        self.fonte_titulo = pygame.font.SysFont("Arial", 50, bold=True)
        self.fonte_texto = pygame.font.SysFont("Arial", 24)

        # Inicia variáveis
        self.resetar_jogo()

    def resetar_jogo(self):
        """Reinicia tudo para um novo jogo"""
        self.todos_sprites = pygame.sprite.Group()
        self.coletaveis = pygame.sprite.Group()
        self.obstaculos = pygame.sprite.Group()
        
        self.jogador = Aluno(LARGURA_TELA // 2, ALTURA_TELA - 100)
        self.todos_sprites.add(self.jogador)

        self.ultimo_spawn = pygame.time.get_ticks()
        self.intervalo_spawn = 1500 

        for _ in range(5):
            self.criar_coletavel()

    def criar_coletavel(self):
        classe_item = random.choice([Cracha, Comida, Raio])
        item = classe_item()
        self.todos_sprites.add(item)
        self.coletaveis.add(item)

    def criar_obstaculo(self):
        inimigo = Obstaculo()
        self.todos_sprites.add(inimigo)
        self.obstaculos.add(inimigo)

    def eventos(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.rodando = False
            
            # --- EVENTOS NO MENU ---
            if self.estado == "MENU":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN: # Enter começa o jogo
                        self.estado = "JOGANDO"
            
            # --- EVENTOS JOGANDO ---
            elif self.estado == "JOGANDO":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT: self.jogador.mover(-5, 0)
                    if event.key == pygame.K_RIGHT: self.jogador.mover(5, 0)
                    if event.key == pygame.K_UP: self.jogador.mover(0, -5)
                    if event.key == pygame.K_DOWN: self.jogador.mover(0, 5)

                if event.type == pygame.KEYUP:
                    if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                        self.jogador.velocidade_x = 0
                    if event.key in [pygame.K_UP, pygame.K_DOWN]:
                        self.jogador.velocidade_y = 0
            
            # --- EVENTOS GAME OVER ---
            elif self.estado == "GAME_OVER":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r: # R reinicia
                        self.resetar_jogo()
                        self.estado = "JOGANDO"

    def atualizar(self):
        if self.estado != "JOGANDO":
            return # Se não estiver jogando, não mexe nada

        self.todos_sprites.update()

        # Spawns
        agora = pygame.time.get_ticks()
        if agora - self.ultimo_spawn > self.intervalo_spawn:
            self.criar_obstaculo()
            self.ultimo_spawn = agora

        # Colisões
        hits = pygame.sprite.spritecollide(self.jogador, self.coletaveis, True)
        for hit in hits:
            if hit.tipo == "cracha": self.jogador.pontos += 10
            elif hit.tipo == "comida": self.jogador.vida = min(100, self.jogador.vida + 10)
            self.criar_coletavel()

        dano = pygame.sprite.spritecollide(self.jogador, self.obstaculos, False)
        if dano:
            self.jogador.vida -= 1
            if self.jogador.vida <= 0:
                self.estado = "GAME_OVER"

    def desenhar_menu(self):
        self.tela.fill(AZUL_UFPE) # Fundo azul
        
        titulo = self.fonte_titulo.render("UFPE ROAD", True, BRANCO)
        instrucao = self.fonte_texto.render("Pressione ENTER para começar", True, BRANCO)
        
        rect_titulo = titulo.get_rect(center=(LARGURA_TELA/2, ALTURA_TELA/2 - 50))
        rect_instr = instrucao.get_rect(center=(LARGURA_TELA/2, ALTURA_TELA/2 + 20))
        
        self.tela.blit(titulo, rect_titulo)
        self.tela.blit(instrucao, rect_instr)

    def desenhar_hud(self):
        pontos = self.fonte_texto.render(f"PONTOS: {self.jogador.pontos}", True, PRETO)
        vida = self.fonte_texto.render(f"VIDA: {self.jogador.vida}%", True, VERMELHO)
        self.tela.blit(pontos, (10, 10))
        self.tela.blit(vida, (LARGURA_TELA - 150, 10))

    def desenhar_game_over(self):
        self.tela.fill(PRETO)
        texto = self.fonte_titulo.render("GAME OVER", True, VERMELHO)
        restart = self.fonte_texto.render("Pressione 'R' para Reiniciar", True, BRANCO)
        
        self.tela.blit(texto, (LARGURA_TELA/2 - 100, ALTURA_TELA/2 - 50))
        self.tela.blit(restart, (LARGURA_TELA/2 - 120, ALTURA_TELA/2 + 20))

    def desenhar(self):
        if self.estado == "MENU":
            self.desenhar_menu()
        elif self.estado == "JOGANDO":
            self.tela.fill(BRANCO)
            self.todos_sprites.draw(self.tela)
            self.desenhar_hud()
        elif self.estado == "GAME_OVER":
            self.desenhar_game_over()
        
        pygame.display.flip()

    def rodar(self):
        while self.rodando:
            self.eventos()
            self.atualizar()
            self.desenhar()
            self.relogio.tick(FPS)
        pygame.quit()
        sys.exit()