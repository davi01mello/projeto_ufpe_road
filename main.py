import pygame
import sys
import random

from src.config import *
from src.entities.player import Player
from src.entities.obstacles import Obstacle
from src.entities.collectibles import BadgeFragment, EnergyDrink, Shield

# --- CONFIGURAÇÃO ---
REQUIRED_BADGES = 7
GOAL_DISTANCE = 100  
TOTAL_ROWS = GOAL_DISTANCE + 20 

# Tipos de Linha
ROW_GRASS = 0
ROW_ROAD = 1
ROW_FINISH = 2

# Estados
START = 0
PLAYING = 1
GAME_OVER = 2
VICTORY = 3

class Game:
    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init()
            self.sound_enabled = True
        except:
            self.sound_enabled = False

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("CIn Road: Rumo ao Diploma")
        self.clock = pygame.time.Clock()
        
        self.font = pygame.font.SysFont("Arial", 24)
        self.title_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.alert_font = pygame.font.SysFont("Arial", 36, bold=True)
        
        self.state = START
        self.running = True

        # SONS
        self.sounds = {}
        if self.sound_enabled:
            try:
                pygame.mixer.music.load("assets/sounds/musica.mp3")
                pygame.mixer.music.set_volume(0.4) 
                self.sounds["jump"] = pygame.mixer.Sound("assets/sounds/pulo.wav")
                self.sounds["hit"] = pygame.mixer.Sound("assets/sounds/dano.wav")
                self.sounds["collect"] = pygame.mixer.Sound("assets/sounds/item.wav")
                self.sounds["game_over"] = pygame.mixer.Sound("assets/sounds/game_over.wav")
                self.sounds["win"] = pygame.mixer.Sound("assets/sounds/vitoria.wav")
                self.sounds["turbo"] = pygame.mixer.Sound("assets/sounds/item.wav")
                if "jump" in self.sounds: self.sounds["jump"].set_volume(0.3)
            except: pass

        self.map_layout = self.generate_map_layout()

    def play_sound(self, name):
        if self.sound_enabled and name in self.sounds:
            try: self.sounds[name].play()
            except: pass

    def generate_map_layout(self):
        layout = []
        for _ in range(10): layout.append(ROW_FINISH)
            
        while len(layout) < TOTAL_ROWS:
            if random.random() < 0.5:
                num = random.randint(2, 5)
                for _ in range(num): layout.append(ROW_ROAD)
            else:
                num = random.randint(1, 3)
                for _ in range(num): layout.append(ROW_GRASS)
        
        for i in range(1, 8):
            layout[-i] = ROW_GRASS
        return layout

    def new_game(self):
        self.all_sprites = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.items = pygame.sprite.Group()

        start_x = GRID_WIDTH // 2
        start_y = GRID_HEIGHT - 2
        skin = getattr(self, 'selected_skin', "aluno1frente.png")
        self.player = Player(start_x, start_y, skin) 
        self.all_sprites.add(self.player)

        self.spawn_timer = 0
        self.score = 0
        self.distance_traveled = 0 
        self.turbo_active = False
        self.turbo_timer = 0
        self.idle_frames = 0 
        
        # MUDANÇA: Dicionário para controlar o tempo de spawn de cada rua
        # Chave: Índice da Linha (int) -> Valor: Timer (int)
        self.lane_timers = {} 
        
        if self.sound_enabled:
            try: pygame.mixer.music.play(-1)
            except: pass

    def start_turbo(self):
        self.turbo_active = True
        self.turbo_timer = 60 
        self.play_sound("turbo")
        self.idle_frames = 0 

    def scroll_world(self):
        self.distance_traveled += 1
        self.idle_frames = 0 
        
        for sprite in self.all_sprites:
            if sprite != self.player:
                sprite.rect.y += BLOCK_SIZE
                if hasattr(sprite, 'grid_y'):
                    sprite.grid_y += 1
                if sprite.rect.top > SCREEN_HEIGHT:
                    sprite.kill()

        self.spawn_static_objects()

    def spawn_static_objects(self):
        """Gera apenas itens e obras (coisas que não andam)"""
        rows_remaining = len(self.map_layout) - 1 - self.distance_traveled
        rows_on_screen = SCREEN_HEIGHT // BLOCK_SIZE
        target_row_index = int(rows_remaining - rows_on_screen)
        
        if target_row_index < 0: return 
        
        row_type = self.map_layout[target_row_index]

        if row_type == ROW_GRASS:
            if random.random() < 0.5:
                if random.random() < 0.3:
                    obs = Obstacle("obra", fixed_y=-BLOCK_SIZE)
                    self.all_sprites.add(obs)
                    self.obstacles.add(obs)
                else:
                    item_class = random.choices([BadgeFragment, EnergyDrink, Shield], weights=[80, 10, 10], k=1)[0]
                    item = item_class()
                    item.rect.y = -BLOCK_SIZE 
                    self.all_sprites.add(item)
                    self.items.add(item)

    def manage_traffic(self):
        """
        Gera tráfego contínuo com espaçamento entre carros.
        """
        rows_on_screen = SCREEN_HEIGHT // BLOCK_SIZE
        bottom_row_logical_index = len(self.map_layout) - 1 - self.distance_traveled
        
        # Percorre as linhas visíveis
        for i in range(rows_on_screen + 2):
            screen_y = SCREEN_HEIGHT - ((i + 1) * BLOCK_SIZE)
            logical_index = int(bottom_row_logical_index - i)
            
            if logical_index < 0: continue
            
            # Se for RUA
            if self.map_layout[logical_index] == ROW_ROAD:
                
                # 1. Verifica/Atualiza o Timer dessa rua específica
                if logical_index not in self.lane_timers:
                    self.lane_timers[logical_index] = 0
                
                # Se o timer ainda está contando, diminui e PULA essa rua (não cria carro)
                if self.lane_timers[logical_index] > 0:
                    self.lane_timers[logical_index] -= 1
                    continue 

                # 2. Se o timer zerou, tenta criar um carro
                # Chance alta (5%) porque o timer já controla o fluxo
                if random.random() < 0.05:
                    
                    direction = "left" if logical_index % 2 == 0 else "right"
                    
                    progress = self.distance_traveled / GOAL_DISTANCE
                    dificuldade = 1.0 + (progress * 1.5)

                    obs = Obstacle(
                        random.choice(["carro", "carro", "circular"]), 
                        speed_multiplier=dificuldade,
                        fixed_y=screen_y,
                        fixed_direction=direction
                    )
                    
                    self.all_sprites.add(obs)
                    self.obstacles.add(obs)
                    
                    # 3. DEFINE O ESPAÇAMENTO PARA O PRÓXIMO CARRO
                    # Gera um número entre 90 e 200 frames (1.5s a 3.5s de intervalo)
                    # Isso garante que nunca venha um carro colado no outro
                    self.lane_timers[logical_index] = random.randint(90, 200)

    def spawn_entities(self):
        pass

    def check_collisions(self):
        # VITÓRIA
        if self.distance_traveled >= GOAL_DISTANCE:
            if self.sound_enabled: pygame.mixer.music.stop()
            if self.score >= REQUIRED_BADGES:
                self.play_sound("win")
                self.state = VICTORY
            else:
                self.play_sound("game_over")
                self.state = GAME_OVER
            return

        # OBSTÁCULOS
        hit_obstacle = pygame.sprite.spritecollideany(self.player, self.obstacles)
        if hit_obstacle:
            if self.turbo_active:
                self.play_sound("hit")
                hit_obstacle.kill()
            else:
                self.play_sound("hit")
                tomou_dano = self.player.check_damage()
                hit_obstacle.kill()
                if tomou_dano:
                    if self.player.lives > 0:
                        self.player.reset_position()
                    else:
                        if self.sound_enabled: pygame.mixer.music.stop()
                        self.play_sound("game_over")
                        self.state = GAME_OVER

        # ITENS
        collected_item = pygame.sprite.spritecollideany(self.player, self.items)
        if collected_item:
            self.play_sound("collect")
            if isinstance(collected_item, BadgeFragment):
                self.score += 1 
            elif isinstance(collected_item, Shield):
                self.player.has_shield = True
            elif isinstance(collected_item, EnergyDrink):
                self.start_turbo()
            collected_item.kill()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, 
                                 pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d]:
                    self.play_sound("jump")

                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.player.move(-1, 0)
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.player.move(1, 0)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.player.move(0, 1) 
                
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.idle_frames = 0 
                    if self.player.grid_y < 4:
                        self.scroll_world() 
                        self.player.update_sprite("back")
                    else:
                        self.player.move(0, -1)

    def draw_background(self):
        rows_on_screen = SCREEN_HEIGHT // BLOCK_SIZE
        bottom_row_logical_index = len(self.map_layout) - 1 - self.distance_traveled
        
        for i in range(rows_on_screen + 1):
            screen_y = SCREEN_HEIGHT - ((i + 1) * BLOCK_SIZE)
            logical_index = int(bottom_row_logical_index - i)
            
            if logical_index < 0: 
                pygame.draw.rect(self.screen, (200, 200, 255), (0, screen_y, SCREEN_WIDTH, BLOCK_SIZE))
                continue
            
            row_type = self.map_layout[logical_index]
            
            if row_type == ROW_ROAD:
                pygame.draw.rect(self.screen, (50, 50, 50), (0, screen_y, SCREEN_WIDTH, BLOCK_SIZE))
                pygame.draw.rect(self.screen, (255, 255, 255), (SCREEN_WIDTH//2 - 5, screen_y + 10, 10, 30))
            
            elif row_type == ROW_GRASS:
                pygame.draw.rect(self.screen, (34, 139, 34), (0, screen_y, SCREEN_WIDTH, BLOCK_SIZE))
                pygame.draw.rect(self.screen, (28, 100, 28), (0, screen_y + 45, SCREEN_WIDTH, 5))
            
            elif row_type == ROW_FINISH:
                pygame.draw.rect(self.screen, (200, 200, 200), (0, screen_y, SCREEN_WIDTH, BLOCK_SIZE))
                if logical_index == 9: 
                     for col in range(0, SCREEN_WIDTH, 40):
                        c = (0,0,0) if (col//40)%2==0 else (255,255,255)
                        pygame.draw.rect(self.screen, c, (col, screen_y, 40, BLOCK_SIZE))

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
        except:
            img_p1 = pygame.Surface((100,100)); img_p1.fill((0,0,255))
            img_p2 = pygame.Surface((100,100)); img_p2.fill((0,255,0))

        selection_index = 0 
        waiting = True
        pygame.event.clear()
        
        if self.sound_enabled and not pygame.mixer.music.get_busy():
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
                        self.play_sound("jump")
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        selection_index = 1
                        self.play_sound("jump")
                    elif event.key == pygame.K_RETURN:
                        self.play_sound("collect")
                        waiting = False

            self.screen.fill(WHITE)
            self.draw_text("CIn Road", self.title_font, BLACK, SCREEN_WIDTH/2, 80)
            self.draw_text(f"Meta: Chegar ao CIn com {REQUIRED_BADGES} crachás!", self.font, BLACK, SCREEN_WIDTH/2, 140)
            self.draw_text("Escolha seu Personagem:", self.font, BLACK, SCREEN_WIDTH/2, 220)

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
        if self.idle_frames >= 5 * 60:
            motivo = "Você ficou parado muito tempo!"
        elif self.score < REQUIRED_BADGES and self.distance_traveled >= GOAL_DISTANCE:
            motivo = f"Faltaram crachás! {self.score}/{REQUIRED_BADGES}"
        else:
            motivo = "Game Over!"

        self.draw_text("GAME OVER", self.title_font, (255, 0, 0), SCREEN_WIDTH/2, SCREEN_HEIGHT/4)
        self.draw_text(motivo, self.font, WHITE, SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
        self.draw_text("Tecle para reiniciar", self.font, WHITE, SCREEN_WIDTH/2, SCREEN_HEIGHT * 3/4)
        pygame.display.flip()
        self.wait_for_key()

    def show_victory_screen(self):
        self.screen.fill(WHITE)
        self.draw_text("APROVADO!", self.title_font, (0, 0, 255), SCREEN_WIDTH/2, SCREEN_HEIGHT/4)
        self.draw_text(f"Crachás: {self.score}", self.font, BLACK, SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
        self.draw_text("Tecle para reiniciar", self.font, BLACK, SCREEN_WIDTH/2, SCREEN_HEIGHT * 3/4)
        pygame.display.flip()
        self.wait_for_key()

    def wait_for_key(self):
        pygame.event.clear()
        waiting = True
        while waiting:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    waiting = False

    def update(self):
        if not self.turbo_active:
            self.idle_frames += 1
            if self.idle_frames >= 5 * 60:
                if self.sound_enabled: pygame.mixer.music.stop()
                self.play_sound("game_over")
                self.state = GAME_OVER
        
        if self.turbo_active:
            self.turbo_timer -= 1
            if self.turbo_timer % 2 == 0:
                self.scroll_world()
            if self.turbo_timer <= 0:
                self.turbo_active = False
        
        self.manage_traffic()
        self.all_sprites.update()
        self.check_collisions()

    def draw(self):
        self.draw_background()
        self.all_sprites.draw(self.screen)
        
        escudo_txt = "SIM" if self.player.has_shield else "NÃO"
        cor_escudo = (0, 200, 0) if self.player.has_shield else BLACK

        if self.turbo_active:
            self.draw_text("!!! TURBO !!!", self.title_font, (255, 165, 0), SCREEN_WIDTH/2, 100)
        elif self.idle_frames > 3 * 60:
            self.draw_text("MOVA-SE!", self.alert_font, (255, 0, 0), SCREEN_WIDTH/2, 100)

        self.draw_text(f"Vidas: {self.player.lives}", self.font, BLACK, 60, 10)
        self.draw_text(f"Escudo: {escudo_txt}", self.font, cor_escudo, 200, 10)
        
        distancia = GOAL_DISTANCE - self.distance_traveled
        if distancia < 0: distancia = 0
        self.draw_text(f"Faltam: {distancia}m", self.font, (0, 0, 255), SCREEN_WIDTH/2, 10)
        
        cor_score = BLACK
        if self.score >= REQUIRED_BADGES: cor_score = (0, 180, 0) 
        elif self.distance_traveled > GOAL_DISTANCE * 0.8: cor_score = (255, 0, 0)

        self.draw_text(f"Crachás: {self.score}/{REQUIRED_BADGES}", self.font, cor_score, SCREEN_WIDTH - 100, 10)
        
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