import pygame
import sys
import random

from src.config import *
from src.entities.player import Player
from src.entities.obstacles import Obstacle
from src.entities.collectibles import BadgeFragment, EnergyDrink, Shield

# Estados
START = 0
PLAYING = 1
GAME_OVER = 2
VICTORY = 3

class Game:
    def __init__(self):
        pygame.init()
        
        # --- 1. INICIALIZA O SISTEMA DE SOM ---
        try:
            pygame.mixer.init()
            self.sound_enabled = True
        except Exception as e:
            print(f"Aviso: Não foi possível iniciar o som. {e}")
            self.sound_enabled = False

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("CIn Road: Rumo ao Diploma")
        self.clock = pygame.time.Clock()
        
        self.font = pygame.font.SysFont("Arial", 24)
        self.title_font = pygame.font.SysFont("Arial", 48, bold=True)
        
        self.state = START
        self.running = True

        # --- 2. CARREGA OS SONS ---
        self.sounds = {}
        if self.sound_enabled:
            try:
                # Música de Fundo (ajuste o volume: 0.0 a 1.0)
                pygame.mixer.music.load("assets/sounds/musica.mp3")
                pygame.mixer.music.set_volume(0.4) 
                
                # Efeitos Sonoros (SFX)
                self.sounds["jump"] = pygame.mixer.Sound("assets/sounds/pulo.wav")
                self.sounds["hit"] = pygame.mixer.Sound("assets/sounds/dano.wav")
                self.sounds["collect"] = pygame.mixer.Sound("assets/sounds/item.wav")
                self.sounds["game_over"] = pygame.mixer.Sound("assets/sounds/game_over.wav")
                self.sounds["win"] = pygame.mixer.Sound("assets/sounds/vitoria.wav")
                
                # Ajuste opcional de volumes individuais
                if "jump" in self.sounds: self.sounds["jump"].set_volume(0.3)
            except Exception as e:
                print(f"⚠️ Aviso: Arquivos de som faltando em 'assets/sounds/'. O jogo ficará mudo. Erro: {e}")

    def play_sound(self, name):
        """Função auxiliar para tocar sons sem quebrar o jogo se faltar arquivo"""
        if self.sound_enabled and name in self.sounds:
            self.sounds[name].play()

    def new_game(self):
        self.all_sprites = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.items = pygame.sprite.Group()

        # Jogador começa lá embaixo
        start_x = GRID_WIDTH // 2
        start_y = GRID_HEIGHT - 2
        
        # Cria o Player com a Skin Escolhida
        self.player = Player(start_x, start_y, self.selected_skin) 
        self.all_sprites.add(self.player)

        self.spawn_timer = 0
        self.score = 0
        self.distance_traveled = 0 

        # Toca a música em loop (-1) ao iniciar o jogo
        if self.sound_enabled:
            try: 
                pygame.mixer.music.play(-1)
            except: 
                pass

    def scroll_world(self):
        """Move o mundo para baixo para simular a câmera subindo."""
        self.distance_traveled += 1
        
        # 1. Move tudo que NÃO é o player para baixo
        for sprite in self.all_sprites:
            if sprite != self.player:
                sprite.rect.y += BLOCK_SIZE
                if hasattr(sprite, 'grid_y'):
                    sprite.grid_y += 1
                if sprite.rect.top > SCREEN_HEIGHT:
                    sprite.kill()

        # 2. Gera novos obstáculos no TOPO da tela
        self.spawn_on_horizon()

    def spawn_on_horizon(self):
        """Cria inimigos com dificuldade progressiva"""
        if random.random() < 0.6: 
            if random.random() < 0.7:
                # Dificuldade progressiva
                progress = self.distance_traveled / GOAL_DISTANCE
                dificuldade = 1.0 + (progress * 1.0) 
                
                obs = Obstacle(random.choice(["carro", "carro", "circular", "obra"]), speed_multiplier=dificuldade)
                obs.rect.y = -BLOCK_SIZE 
                self.all_sprites.add(obs)
                self.obstacles.add(obs)
            else:
                item_class = random.choice([BadgeFragment, EnergyDrink, Shield])
                item = item_class()
                item.rect.y = -BLOCK_SIZE 
                self.all_sprites.add(item)
                self.items.add(item)

    def spawn_entities(self):
        """Spawn aleatório secundário"""
        self.spawn_timer += 1
        if self.spawn_timer >= 60: 
            self.spawn_timer = 0
            pass

    def check_collisions(self):
        # 1. Vitória
        if self.distance_traveled >= GOAL_DISTANCE:
            if self.sound_enabled: pygame.mixer.music.stop()
            self.play_sound("win") # <--- SOM DE VITÓRIA
            self.state = VICTORY
            return

        # 2. Colisão Obstáculos
        hit_obstacle = pygame.sprite.spritecollideany(self.player, self.obstacles)
        if hit_obstacle:
            self.play_sound("hit") # <--- SOM DE DANO
            tomou_dano = self.player.check_damage()
            hit_obstacle.kill()

            if tomou_dano:
                if self.player.lives > 0:
                    self.player.reset_position()
                else:
                    if self.sound_enabled: pygame.mixer.music.stop()
                    self.play_sound("game_over") # <--- SOM DE GAME OVER
                    self.state = GAME_OVER

        # 3. Colisão Itens
        collected_item = pygame.sprite.spritecollideany(self.player, self.items)
        if collected_item:
            self.play_sound("collect") # <--- SOM DE COLETA
            
            if isinstance(collected_item, BadgeFragment):
                self.score += 1 
            elif isinstance(collected_item, Shield):
                self.player.has_shield = True
            elif isinstance(collected_item, EnergyDrink):
                pass
            collected_item.kill()

    # --- INPUTS ---
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                
                # Toca som se for tecla de movimento
                if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, 
                                 pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d]:
                    self.play_sound("jump") # <--- SOM DE PULO

                # --- ESQUERDA ---
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.player.move(-1, 0)

                # --- DIREITA ---
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.player.move(1, 0)

                # --- BAIXO ---
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.player.move(0, 1) 
                
                # --- CIMA ---
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    if self.player.grid_y < 4:
                        self.scroll_world() 
                        self.player.update_sprite("back")
                    else:
                        self.player.move(0, -1)

    def draw_text(self, text, font, color, x, y):
        img = font.render(text, True, color)
        rect = img.get_rect()
        rect.midtop = (x, y)
        self.screen.blit(img, rect)

    def show_start_screen(self):
        try:
            img_p1 = pygame.image.load("assets/img/aluno1frente.png").convert_alpha()
            img_p1 = pygame.transform.scale(img_p1, (100, 100))

            img_p2 = pygame.image.load("assets/img/aluno2frente.png").convert_alpha()
            img_p2 = pygame.transform.scale(img_p2, (100, 100))
        except Exception as e:
            print(f"Erro no menu: {e}")
            sys.exit()

        selection_index = 0 
        waiting = True
        
        # Música do Menu (opcional, pode ser a mesma do jogo ou outra)
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
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        selection_index = 0
                        self.play_sound("jump") # Som ao trocar seleção
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        selection_index = 1
                        self.play_sound("jump")
                    elif event.key == pygame.K_RETURN:
                        self.play_sound("collect") # Som de confirmar
                        waiting = False

            self.screen.fill(WHITE)
            self.draw_text("CIn Road", self.title_font, BLACK, SCREEN_WIDTH/2, 100)
            self.draw_text("Escolha o Personagem:", self.font, BLACK, SCREEN_WIDTH/2, 200)

            x1, y1 = SCREEN_WIDTH/2 - 150, 300
            x2, y2 = SCREEN_WIDTH/2 + 50, 300

            self.screen.blit(img_p1, (x1, y1))
            self.screen.blit(img_p2, (x2, y2))

            if selection_index == 0:
                pygame.draw.rect(self.screen, (255, 0, 0), (x1-5, y1-5, 110, 110), 3)
                self.selected_skin = "aluno1frente.png"
            else:
                pygame.draw.rect(self.screen, (255, 0, 0), (x2-5, y2-5, 110, 110), 3)
                self.selected_skin = "aluno2frente.png"

            pygame.display.flip()

    def show_game_over_screen(self):
        self.screen.fill(BLACK)
        self.draw_text("GAME OVER", self.title_font, (255, 0, 0), SCREEN_WIDTH/2, SCREEN_HEIGHT/4)
        self.draw_text(f"Pontuação: {self.score}", self.font, WHITE, SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
        self.draw_text("Tecla para reiniciar", self.font, WHITE, SCREEN_WIDTH/2, SCREEN_HEIGHT * 3/4)
        pygame.display.flip()
        self.wait_for_key()

    def show_victory_screen(self):
        self.screen.fill(WHITE)
        self.draw_text("CHEGOU AO CIn!", self.title_font, (0, 0, 255), SCREEN_WIDTH/2, SCREEN_HEIGHT/4)
        self.draw_text(f"Crachás: {self.score}", self.font, BLACK, SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
        self.draw_text("Tecla para reiniciar", self.font, BLACK, SCREEN_WIDTH/2, SCREEN_HEIGHT * 3/4)
        pygame.display.flip()
        self.wait_for_key()

    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pygame.KEYUP:
                    waiting = False

    def update(self):
        self.all_sprites.update()
        self.spawn_entities()
        self.check_collisions()

    def draw(self):
        self.screen.fill(WHITE)
        # Grade
        for x in range(0, SCREEN_WIDTH, BLOCK_SIZE):
            pygame.draw.line(self.screen, (230, 230, 230), (x, 0), (x, SCREEN_HEIGHT))
        
        self.all_sprites.draw(self.screen)
        
        # HUD
        escudo_txt = "SIM" if self.player.has_shield else "NÃO"
        cor_escudo = (0, 200, 0) if self.player.has_shield else BLACK

        self.draw_text(f"Vidas: {self.player.lives}", self.font, BLACK, 60, 10)
        self.draw_text(f"Escudo: {escudo_txt}", self.font, cor_escudo, 200, 10)
        
        distancia_restante = GOAL_DISTANCE - self.distance_traveled
        if distancia_restante < 0: distancia_restante = 0
        self.draw_text(f"Faltam: {distancia_restante}m", self.font, (0, 0, 255), SCREEN_WIDTH/2, 10)
        
        self.draw_text(f"Crachás: {self.score}", self.font, BLACK, SCREEN_WIDTH - 80, 10)
        
        pygame.display.flip()

    def run(self):
        while self.running:
            if self.state == START:
                self.show_start_screen()
                self.new_game()
                self.state = PLAYING
            elif self.state == GAME_OVER:
                self.show_game_over_screen()
                self.state = START
            elif self.state == VICTORY:
                self.show_victory_screen()
                self.state = START
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