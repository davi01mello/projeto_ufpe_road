import pygame
import sys
import random
import os

from src.config import *
from src.entities.player import Player
from src.entities.obstacles import Obstacle
from src.entities.collectibles import BadgeFragment, EnergyDrink, Shield

# Estados do Jogo
START = 0
PLAYING = 1
GAME_OVER = 2
VICTORY = 3

class Game:
    def __init__(self):
        pygame.init()
        
        # --- 1. CONFIGURAÇÃO DE SOM ---
        try:
            pygame.mixer.init()
            self.sound_enabled = True
        except:
            print("⚠️ Aviso: Não foi possível iniciar o mixer de som.")
            self.sound_enabled = False

        # --- 2. TELA E FONTES ---
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("CIn Road: Rumo ao Diploma")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)
        self.title_font = pygame.font.SysFont("Arial", 48, bold=True)
        
        # --- 3. VARIÁVEIS DE ESTADO ---
        self.state = START
        self.running = True
        self.score = 0
        self.distance_traveled = 0
        self.spawn_timer = 0
        self.selected_skin = "aluno1frente.png"
        self.faixas_rua_seguidas = 0
        
        # Variável para saber por que perdeu (Atropelado ou Barrado)
        self.motivo_game_over = "" 

        # --- 4. GRUPOS DE SPRITES ---
        self.all_sprites = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        
        # --- 5. CARREGAMENTO DOS SONS ---
        self.sounds = {}
        if self.sound_enabled:
            lista_sons = {
                "jump": "pulo.wav",
                "hit": "dano.wav",
                "collect": "item.wav",
                "game_over": "game_over.wav",
                "win": "vitoria.wav",
                "shield_break": "dano.wav" 
            }
            for nome_logico, nome_arquivo in lista_sons.items():
                try:
                    caminho = os.path.join("assets", "sounds", nome_arquivo)
                    self.sounds[nome_logico] = pygame.mixer.Sound(caminho)
                    self.sounds[nome_logico].set_volume(0.4)
                except: pass

            try:
                caminho_musica = os.path.join("assets", "sounds", "musica.mp3")
                pygame.mixer.music.load(caminho_musica)
                pygame.mixer.music.set_volume(0.3)
            except: pass

        # --- 6. GERAÇÃO DO MAPA INICIAL ---
        self.mapa_faixas = []
        num_faixas = SCREEN_HEIGHT // BLOCK_SIZE
        for i in range(num_faixas):
            if i > num_faixas - 4:
                self.mapa_faixas.append(0)
                self.faixas_rua_seguidas = 0
            else:
                self.mapa_faixas.append(self.gerar_tipo_faixa())

    def gerar_tipo_faixa(self):
        if self.faixas_rua_seguidas >= 2:
            self.faixas_rua_seguidas = 0
            return 0 
        
        if random.random() < 0.6:
            self.faixas_rua_seguidas += 1
            return 1 
        else:
            self.faixas_rua_seguidas = 0
            return 0 

    def play_sound(self, name):
        if self.sound_enabled and name in self.sounds:
            self.sounds[name].play()

    def new_game(self):
        self.all_sprites = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.items = pygame.sprite.Group()

        start_x = GRID_WIDTH // 2
        start_y = GRID_HEIGHT - 2
        self.player = Player(start_x, start_y, self.selected_skin) 
        self.all_sprites.add(self.player)

        self.spawn_timer = 0
        self.score = 0
        self.distance_traveled = 0 
        self.motivo_game_over = "" # Reseta o motivo
        
        if self.sound_enabled:
            try: 
                if not pygame.mixer.music.get_busy():
                    pygame.mixer.music.play(-1)
            except: pass

    def reset_round(self):
        self.player.reset_position()
        self.obstacles.empty()
        
        num_faixas = SCREEN_HEIGHT // BLOCK_SIZE
        self.mapa_faixas = []
        for i in range(num_faixas):
            if i > num_faixas - 4:
                self.mapa_faixas.append(0)
            else:
                self.mapa_faixas.append(self.gerar_tipo_faixa())

    def draw(self):
        self.screen.fill(GREEN) 

        for i, tipo in enumerate(self.mapa_faixas):
            if tipo == 1: 
                y_pos = i * BLOCK_SIZE
                pygame.draw.rect(self.screen, CINZA_ESTRADA, (0, y_pos, SCREEN_WIDTH, BLOCK_SIZE))
                meio = y_pos + (BLOCK_SIZE // 2)
                pygame.draw.line(self.screen, WHITE, (0, meio), (SCREEN_WIDTH, meio), 2)

        self.all_sprites.draw(self.screen)
        self.draw_hud()
        pygame.display.flip()

    def draw_hud(self):
        def draw_text_w_shadow(text, font, col, x, y):
            sh = font.render(text, True, (0,0,0))
            self.screen.blit(sh, (x+2, y+2))
            txt = font.render(text, True, col)
            self.screen.blit(txt, (x, y))

        # AGORA MOSTRA A META NO PLACAR (Ex: 2/6)
        cor_score = WHITE
        if self.score >= MIN_CRACHAS: cor_score = (0, 255, 0) # Fica verde se já tiver o suficiente
        
        draw_text_w_shadow(f"Crachás: {self.score}/{MIN_CRACHAS}", self.font, cor_score, SCREEN_WIDTH - 180, 10)
        
        # Mostra a distância
        dist_restante = max(0, GOAL_DISTANCE - self.distance_traveled)
        draw_text_w_shadow(f"CIn em: {dist_restante}m", self.font, WHITE, SCREEN_WIDTH/2 - 50, 10)

        draw_text_w_shadow(f"Vidas: {self.player.lives}", self.font, RED, 10, 10)
        
        if self.player.has_shield:
            draw_text_w_shadow("🛡️ BLINDADO", self.font, BLUE, 10, 40)

    def scroll_world(self):
        self.distance_traveled += 1
        
        for sprite in self.all_sprites:
            if sprite != self.player:
                sprite.rect.y += int(BLOCK_SIZE)
                if sprite.rect.top > SCREEN_HEIGHT:
                    sprite.kill()

        self.mapa_faixas.pop() 
        self.mapa_faixas.insert(0, self.gerar_tipo_faixa())

    def spawn_entities(self):
        self.spawn_timer += 1
        
        if self.spawn_timer >= 25: 
            self.spawn_timer = 0
            
            ruas = [i for i, tipo in enumerate(self.mapa_faixas) if tipo == 1]
            if ruas and random.random() < 0.8:
                linha = random.choice(ruas)
                y_pixel = linha * BLOCK_SIZE
                tipo = random.choice(["carro", "carro", "circular", "obra"])
                
                obs = Obstacle(y_pos=y_pixel, type_name=tipo)
                self.all_sprites.add(obs)
                self.obstacles.add(obs)

            if random.random() < 0.35: # Chance de item um pouco maior
                linha_item = random.randint(0, len(self.mapa_faixas)-1)
                y_pixel_item = linha_item * BLOCK_SIZE
                
                escolha = random.choices(
                    [BadgeFragment, EnergyDrink, Shield], 
                    weights=[65, 15, 20], 
                    k=1
                )[0]
                
                item = escolha()
                item.rect.y = int(y_pixel_item)
                self.all_sprites.add(item)
                self.items.add(item)

    def check_collisions(self):
        # --- AQUI MUDOU A LÓGICA DE VITÓRIA ---
        if self.distance_traveled >= GOAL_DISTANCE:
            # Chegou no CIn! Verifica se tem crachá
            if self.score >= MIN_CRACHAS:
                self.play_sound("win")
                if self.sound_enabled: pygame.mixer.music.stop()
                self.state = VICTORY
            else:
                # Chegou mas não entra!
                self.play_sound("game_over")
                self.motivo_game_over = "BARRADO" # Motivo específico
                if self.sound_enabled: pygame.mixer.music.stop()
                self.state = GAME_OVER
            return

        # Obstáculos
        hit_obstacle = pygame.sprite.spritecollideany(self.player, self.obstacles)
        
        if hit_obstacle:
            if self.player.has_shield:
                self.play_sound("shield_break") 
                print("🛡️ Escudo protegeu!")
                self.player.has_shield = False
                hit_obstacle.kill() 
            else:
                self.play_sound("hit")
                hit_obstacle.kill() 
                self.player.lives -= 1
                
                if self.player.lives > 0:
                    print("💔 Vida perdida. Resetando fase...")
                    self.reset_round() 
                else:
                    self.motivo_game_over = "MORREU" # Motivo Padrão
                    self.state = GAME_OVER

        # Itens
        item = pygame.sprite.spritecollideany(self.player, self.items)
        if item:
            self.play_sound("collect")
            if isinstance(item, BadgeFragment):
                self.score += 1 
            elif isinstance(item, Shield):
                self.player.has_shield = True
            
            item.kill()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_LEFT, pygame.K_a]: self.player.move(-1, 0)
                elif event.key in [pygame.K_RIGHT, pygame.K_d]: self.player.move(1, 0)
                elif event.key in [pygame.K_DOWN, pygame.K_s]: self.player.move(0, 1)
                elif event.key in [pygame.K_UP, pygame.K_w]:
                    if self.player.grid_y < 4:
                        self.scroll_world()
                        self.player.update_sprite("back")
                    else:
                        self.player.move(0, -1)

    # --- Telas ---
    def show_start_screen(self):
        try:
            img_p1 = pygame.image.load("assets/img/aluno1frente.png").convert_alpha()
            img_p1 = pygame.transform.scale(img_p1, (100, 100))
            img_p2 = pygame.image.load("assets/img/aluno2frente.png").convert_alpha()
            img_p2 = pygame.transform.scale(img_p2, (100, 100))
        except:
            img_p1 = pygame.Surface((100,100)); img_p1.fill(BLUE)
            img_p2 = pygame.Surface((100,100)); img_p2.fill(RED)

        selection = 0 
        waiting = True
        
        if self.sound_enabled:
             if not pygame.mixer.music.get_busy():
                 try: pygame.mixer.music.play(-1)
                 except: pass

        while waiting:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    waiting = False
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_LEFT, pygame.K_a]:
                        selection = 0
                        self.play_sound("jump")
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                        selection = 1
                        self.play_sound("jump")
                    elif event.key == pygame.K_RETURN:
                        self.play_sound("collect")
                        waiting = False

            self.screen.fill(WHITE)
            
            t1 = self.title_font.render("CIn Road", True, BLACK)
            self.screen.blit(t1, (SCREEN_WIDTH//2 - t1.get_width()//2, 100))
            
            t2 = self.font.render("Escolha seu Personagem:", True, BLACK)
            self.screen.blit(t2, (SCREEN_WIDTH//2 - t2.get_width()//2, 200))

            x1, y1 = SCREEN_WIDTH//2 - 150, 300
            x2, y2 = SCREEN_WIDTH//2 + 50, 300

            self.screen.blit(img_p1, (x1, y1))
            self.screen.blit(img_p2, (x2, y2))

            if selection == 0:
                pygame.draw.rect(self.screen, RED, (x1-5, y1-5, 110, 110), 3)
                self.selected_skin = "aluno1frente.png"
            else:
                pygame.draw.rect(self.screen, RED, (x2-5, y2-5, 110, 110), 3)
                self.selected_skin = "aluno2frente.png"

            pygame.display.flip()

    def show_game_over_screen(self):
        self.screen.fill(BLACK)
        
        # Título Vermelho
        t1 = self.title_font.render("GAME OVER", True, RED)
        self.screen.blit(t1, (SCREEN_WIDTH//2 - t1.get_width()//2, 150))
        
        # MENSAGEM DO MOTIVO (Novo!)
        msg = "Suas vidas acabaram..."
        if self.motivo_game_over == "BARRADO":
            msg = f"Barrado no CIn! Faltaram crachás."
        
        t_motivo = self.font.render(msg, True, WHITE)
        self.screen.blit(t_motivo, (SCREEN_WIDTH//2 - t_motivo.get_width()//2, 250))

        t2 = self.font.render(f"Você coletou: {self.score} / {MIN_CRACHAS} crachás", True, WHITE)
        self.screen.blit(t2, (SCREEN_WIDTH//2 - t2.get_width()//2, 300))
        
        t3 = self.font.render("Pressione ENTER para Tentar de Novo", True, WHITE)
        self.screen.blit(t3, (SCREEN_WIDTH//2 - t3.get_width()//2, 450))
        
        pygame.display.flip()
        self.wait_for_input()

    def show_victory_screen(self):
        self.screen.fill(WHITE)
        t1 = self.title_font.render("VOCÊ ENTROU NO CIn!", True, BLUE)
        self.screen.blit(t1, (SCREEN_WIDTH//2 - t1.get_width()//2, 200))
        
        t2 = self.font.render(f"Missão Cumprida: {self.score} crachás", True, BLACK)
        self.screen.blit(t2, (SCREEN_WIDTH//2 - t2.get_width()//2, 300))
        
        t3 = self.font.render("Pressione ENTER para Jogar Novamente", True, BLACK)
        self.screen.blit(t3, (SCREEN_WIDTH//2 - t3.get_width()//2, 400))
        
        pygame.display.flip()
        self.wait_for_input()

    def wait_for_input(self):
        waiting = True
        while waiting:
            self.clock.tick(15)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    waiting = False
                    if self.state != START:
                         self.state = START

    def update(self):
        self.all_sprites.update()
        self.spawn_entities()
        self.check_collisions()

    def run(self):
        while self.running:
            if self.state == START:
                self.show_start_screen()
                self.new_game()
                self.state = PLAYING
            elif self.state == GAME_OVER:
                self.show_game_over_screen()
            elif self.state == VICTORY:
                self.show_victory_screen()
            elif self.state == PLAYING:
                self.handle_events()
                self.update()
                self.draw()
                self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()