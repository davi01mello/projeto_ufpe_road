import pygame
import sys
import random
import os
from src.config import *
from src.entidades import Aluno, FragmentoCracha, Energetico, Escudo, Obstaculo

class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
        pygame.display.set_caption("UFPE Road: Rumo ao CIn")
        self.relogio = pygame.time.Clock()
        self.rodando = True
        self.estado = "MENU"
        
        self.fonte_hud = pygame.font.SysFont("Arial", 20, bold=True)
        self.fonte_grande = pygame.font.SysFont("Arial", 40, bold=True)
        
        # Variáveis do Efeito Matrix (Câmera Lenta)
        self.slow_motion = False
        self.fim_slow_motion = 0

        # Carrega Fundo
        try:
            caminho_fundo = os.path.join("assets", "img", "fundo.png")
            self.fundo = pygame.transform.scale(pygame.image.load(caminho_fundo), (LARGURA_TELA, ALTURA_TELA))
        except: self.fundo = None
        
        self.resetar_jogo()

    def resetar_jogo(self):
        self.todos_sprites = pygame.sprite.Group()
        self.coletaveis = pygame.sprite.Group()
        self.obstaculos = pygame.sprite.Group()
        
        self.jogador = Aluno(LARGURA_TELA // 2, ALTURA_TELA - 60)
        self.todos_sprites.add(self.jogador)
        
        self.ultimo_spawn = pygame.time.get_ticks()
        self.intervalo_spawn = 1500
        
        # Limpar efeitos
        self.slow_motion = False
        
        # Spawnar itens iniciais
        for _ in range(3): self.criar_coletavel()

    def criar_coletavel(self):
        # 60% chance de Fragmento, 20% Energético, 20% Escudo
        sorteio = random.random()
        if sorteio < 0.6: item = FragmentoCracha()
        elif sorteio < 0.8: item = Energetico()
        else: item = Escudo()
        
        self.todos_sprites.add(item)
        self.coletaveis.add(item)

    def criar_obstaculo(self):
        # 20% chance de Circular (Rápido), 80% Carro normal
        tipo = "circular" if random.random() < 0.2 else "carro"
        inimigo = Obstaculo(tipo)
        self.todos_sprites.add(inimigo)
        self.obstaculos.add(inimigo)

    def eventos(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.rodando = False
            
            if self.estado == "MENU":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.estado = "JOGANDO"
            
            elif self.estado == "JOGANDO":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT: self.jogador.mover(-1, 0)
                    if event.key == pygame.K_RIGHT: self.jogador.mover(1, 0)
                    if event.key == pygame.K_UP: self.jogador.mover(0, -1)
                    if event.key == pygame.K_DOWN: self.jogador.mover(0, 1)
                if event.type == pygame.KEYUP:
                    if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:
                        self.jogador.mover(0, 0)
            
            elif self.estado in ["GAME_OVER", "VITORIA"]:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    self.resetar_jogo()
                    self.estado = "JOGANDO"

    def atualizar(self):
        if self.estado != "JOGANDO": return

        # --- Lógica do Slow Motion ---
        agora = pygame.time.get_ticks()
        if self.slow_motion and agora > self.fim_slow_motion:
            self.slow_motion = False
            print("🕒 Efeito Matrix acabou.")

        # Passamos o slow_motion para os obstáculos saberem como se comportar
        self.obstaculos.update(self.slow_motion)
        self.jogador.update()
        self.coletaveis.update() # Itens parados não mudam, mas precisa chamar

        # Gerar Obstáculos
        if agora - self.ultimo_spawn > self.intervalo_spawn:
            self.criar_obstaculo()
            self.ultimo_spawn = agora

        # --- Colisões: Itens ---
        hits = pygame.sprite.spritecollide(self.jogador, self.coletaveis, True)
        for hit in hits:
            if hit.tipo == "fragmento":
                self.jogador.fragmentos += 1
                print(f"🧩 Fragmento pego! Total: {self.jogador.fragmentos}/4")
                if self.jogador.fragmentos >= 4:
                    self.estado = "VITORIA"
            
            elif hit.tipo == "energetico":
                self.slow_motion = True
                self.fim_slow_motion = agora + 5000 # 5 segundos
                print("⚡ MATRIX MODE: Inimigos lentos!")
            
            elif hit.tipo == "escudo":
                self.jogador.tem_escudo = True
                print("🛡️ ESCUDO ATIVO!")
            
            self.criar_coletavel()

        # --- Colisões: Obstáculos ---
        colisao_inimigo = pygame.sprite.spritecollide(self.jogador, self.obstaculos, False)
        if colisao_inimigo:
            # Empurra o jogador para trás para não colidir 60 vezes por segundo
            if self.jogador.velocidade_y < 0: self.jogador.rect.y += 30
            else: self.jogador.rect.y -= 30
            
            # Chama a função receber_dano do Aluno (retorna True se machucou de verdade)
            levou_dano = self.jogador.receber_dano()
            
            if levou_dano and self.jogador.vida <= 0:
                self.estado = "GAME_OVER"

    def desenhar_hud(self):
        # Fundo do HUD
        pygame.draw.rect(self.tela, (200, 200, 200), (0, 0, LARGURA_TELA, 40))
        
        texto_frag = self.fonte_hud.render(f"🧩 Crachá: {self.jogador.fragmentos}/4", True, PRETO)
        texto_vida = self.fonte_hud.render(f"❤️ Vidas: {self.jogador.vida}", True, VERMELHO)
        
        self.tela.blit(texto_frag, (10, 10))
        self.tela.blit(texto_vida, (LARGURA_TELA - 120, 10))

        # Avisos de PowerUp
        if self.jogador.tem_escudo:
            self.tela.blit(self.fonte_hud.render("🛡️ BLINDADO", True, (0, 0, 255)), (LARGURA_TELA/2 - 50, 10))
        elif self.slow_motion:
            self.tela.blit(self.fonte_hud.render("🕒 MATRIX", True, (100, 100, 100)), (LARGURA_TELA/2 - 40, 10))

    def desenhar(self):
        if self.estado == "MENU":
            self.tela.fill(AZUL_UFPE)
            msg = self.fonte_grande.render("ENTER para Jogar", True, BRANCO)
            self.tela.blit(msg, (LARGURA_TELA//2 - 150, ALTURA_TELA//2))
        
        elif self.estado == "JOGANDO":
            if self.fundo: self.tela.blit(self.fundo, (0, 0))
            else: self.tela.fill(BRANCO)
            
            self.todos_sprites.draw(self.tela)
            self.desenhar_hud()
            
        elif self.estado == "GAME_OVER":
            self.tela.fill(PRETO)
            msg = self.fonte_grande.render("GAME OVER (R para reiniciar)", True, VERMELHO)
            self.tela.blit(msg, (LARGURA_TELA//2 - 250, ALTURA_TELA//2))

        elif self.estado == "VITORIA":
            self.tela.fill((0, 200, 0)) # Verde
            msg = self.fonte_grande.render("PARABÉNS! CHEGOU NO CIn!", True, BRANCO)
            self.tela.blit(msg, (LARGURA_TELA//2 - 250, ALTURA_TELA//2))
            
        pygame.display.flip()

    def rodar(self):
        while self.rodando:
            self.eventos()
            self.atualizar()
            self.desenhar()
            self.relogio.tick(FPS)
        pygame.quit()
        sys.exit()