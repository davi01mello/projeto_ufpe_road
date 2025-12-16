import pygame
import sys
import random

from src.config import *
from src.entities.player import Player
from src.entities.obstacles import Obstacle
from src.entities.collectibles import BadgeFragment, EnergyDrink, Shield

# --- CONFIGURAÇÃO ---
REQUIRED_BADGES = 8
GOAL_DISTANCE = 100 
TOTAL_ROWS = GOAL_DISTANCE + 50 # Buffer de segurança

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
    def load_ui_images(self):
        """Carrega ícones usando caminho absoluto para evitar erros"""
        import os 
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        img_dir = os.path.join(base_dir, "assets", "img")
        
        size = (32, 32) 

        def load_and_scale(name):
            full_path = os.path.join(img_dir, name)
            try:
                img = pygame.image.load(full_path).convert_alpha()
                return pygame.transform.scale(img, size)
            except:
                return pygame.Surface(size)

        def create_black_version_for_badge(image):
            if image.get_width() == 32 and image.get_at((0,0)) == (0,0,0,255):
                return image 
            mask = pygame.mask.from_surface(image)
            return mask.to_surface(setcolor=(0, 0, 0, 150), unsetcolor=None)
        
        try:
            path_grass = os.path.join(img_dir, "grass.png")
            self.bg_grass = pygame.image.load(path_grass).convert() 
            self.bg_grass = pygame.transform.scale(self.bg_grass, (SCREEN_WIDTH, BLOCK_SIZE))

            path_road = os.path.join(img_dir, "road.png")
            self.bg_road = pygame.image.load(path_road).convert()
            self.bg_road = pygame.transform.scale(self.bg_road, (SCREEN_WIDTH, BLOCK_SIZE))

            path_cin = os.path.join(img_dir, "cin_predio.png")
            cin_surface = pygame.image.load(path_cin).convert_alpha()
            # Ajuste o tamanho do prédio aqui se achar necessário
            self.cin_img = pygame.transform.scale(cin_surface, (400, 300))
            
        except Exception as e:
            print(f"Erro textura: {e}")
            self.bg_grass = None
            self.bg_road = None
            self.cin_img = None

        self.icon_badge_color = load_and_scale("cracha.png")
        self.icon_badge_black = create_black_version_for_badge(self.icon_badge_color)
        self.icon_shield_color = load_and_scale("capacete.png")
        self.icon_shield_black = load_and_scale("capacete_LOCK.png") 
        self.icon_refri = load_and_scale("raio.png")

    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init()
            self.sound_enabled = True
        except:
            self.sound_enabled = False

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
        self.load_ui_images()
        self.background_image = pygame.image.load("assets/img/telainicial.png").convert()
        self.gameover_image = pygame.image.load("assets/img/gameover.png").convert()
        self.aprovado_image = pygame.image.load("assets/img/aprovado.png").convert()
        pygame.display.set_caption("CIn Road: Rumo ao Diploma")
        self.clock = pygame.time.Clock()
        
        self.font = pygame.font.SysFont("assets/fonts/PressStart2P.ttf", 24)
        self.title_font = pygame.font.SysFont("assets/fonts/PressStart2P.ttf", 48, bold=True)
        self.alert_font = pygame.font.SysFont("assets/fonts/PressStart2P.ttf", 36, bold=True)
        self.home_font = pygame.font.SysFont("assets/fonts/PressStart2P.ttf", 40, bold=False)
        self.gameover_font = pygame.font.SysFont("assets/fonts/PressStart2P.ttf", 58, bold = True)
        
        self.state = START
        self.running = True

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
        # Gera o mapa normal (aleatório)
        for _ in range(10): layout.append(ROW_GRASS)
        while len(layout) < TOTAL_ROWS:
            if random.random() < 0.5:
                num = random.randint(2, 5)
                for _ in range(num): layout.append(ROW_ROAD)
            else:
                num = random.randint(1, 3)
                for _ in range(num): layout.append(ROW_GRASS)
        
        # Garante grama no início
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
        self.slow_motion_timer = 0 
        self.idle_frames = 0 
        self.lane_timers = {} 
        
        if self.sound_enabled:
            try: pygame.mixer.music.play(-1)
            except: pass

    def start_slow_motion(self):
        self.slow_motion_timer = 300 
        self.play_sound("turbo") 

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
        # Lógica de spawn baseada no mapa
        rows_remaining = len(self.map_layout) - 1 - self.distance_traveled
        rows_on_screen = SCREEN_HEIGHT // BLOCK_SIZE
        target_row_index = int(rows_remaining - rows_on_screen)
        
        if target_row_index < 0: return 
        
        # Lógica de metros percorridos
        current_meter = self.distance_traveled + rows_on_screen # Topo da tela
        if current_meter >= GOAL_DISTANCE:
            return

        row_type = self.map_layout[target_row_index]

        if row_type == ROW_GRASS:
            if random.random() < 0.8:
                if random.random() < 0.1:
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
        rows_on_screen = SCREEN_HEIGHT // BLOCK_SIZE
        bottom_row_logical_index = len(self.map_layout) - 1 - self.distance_traveled
        
        for i in range(rows_on_screen + 2):
            screen_y = SCREEN_HEIGHT - ((i + 1) * BLOCK_SIZE)
            
            offset_from_player = i - 1
            current_line_meter = self.distance_traveled + offset_from_player

            if current_line_meter >= GOAL_DISTANCE:
                continue

            logical_index = int(bottom_row_logical_index - i)
            if logical_index < 0: continue

            if self.map_layout[logical_index] == ROW_ROAD:
                if logical_index not in self.lane_timers:
                    self.lane_timers[logical_index] = 0
                
                if self.lane_timers[logical_index] > 0:
                    self.lane_timers[logical_index] -= 1
                    continue 

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
                    self.lane_timers[logical_index] = random.randint(90, 200)

    def check_collisions(self):
        if self.distance_traveled >= GOAL_DISTANCE:
            if self.sound_enabled: pygame.mixer.music.stop()
            if self.score >= REQUIRED_BADGES:
                self.play_sound("win")
                self.state = VICTORY
            else:
                self.play_sound("game_over")
                self.state = GAME_OVER
            return

        hit_obstacle = pygame.sprite.spritecollideany(self.player, self.obstacles)
        if hit_obstacle:
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

        collected_item = pygame.sprite.spritecollideany(self.player, self.items)
        if collected_item:
            self.play_sound("collect")
            if isinstance(collected_item, BadgeFragment):
                self.score += 1 
            elif isinstance(collected_item, Shield):
                self.player.has_shield = True
            elif isinstance(collected_item, EnergyDrink):
                self.start_slow_motion() 
            collected_item.kill()

    def handle_events(self):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_F11:
                        pygame.display.toggle_fullscreen()

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
                            if hasattr(self.player, "update_sprite"):
                                self.player.update_sprite("back")
                        else:
                            self.player.move(0, -1)

    def draw_background(self):
        rows_on_screen = SCREEN_HEIGHT // BLOCK_SIZE
        bottom_row_logical_index = len(self.map_layout) - 1 - self.distance_traveled
        
        # --- 1. DESENHA O CHÃO ---
        for i in range(rows_on_screen + 1):
            screen_y = SCREEN_HEIGHT - ((i + 1) * BLOCK_SIZE)
            
            offset_from_player = i - 1
            current_line_meter = self.distance_traveled + offset_from_player
            
            if current_line_meter >= GOAL_DISTANCE:
                effective_type = ROW_GRASS 
            else:
                logical_index = int(bottom_row_logical_index - i)
                if logical_index >= 0:
                    effective_type = self.map_layout[logical_index]
                else:
                    effective_type = -1

            if effective_type == -1 or effective_type == ROW_GRASS or effective_type == ROW_FINISH:
                if self.bg_grass:
                    self.screen.blit(self.bg_grass, (0, screen_y))
                else:
                    pygame.draw.rect(self.screen, (34, 139, 34), (0, screen_y, SCREEN_WIDTH, BLOCK_SIZE))
            elif effective_type == ROW_ROAD:
                if self.bg_road:
                    self.screen.blit(self.bg_road, (0, screen_y))
                else:
                    pygame.draw.rect(self.screen, (50, 50, 50), (0, screen_y, SCREEN_WIDTH, BLOCK_SIZE))

        # --- 2. DESENHA O CIn (AJUSTE: 5 BLOCOS ACIMA) ---
        if self.cin_img:
            player_y_visual = SCREEN_HEIGHT - (2 * BLOCK_SIZE)
            blocks_to_go = GOAL_DISTANCE - self.distance_traveled
            finish_line_top_y = player_y_visual - (blocks_to_go * BLOCK_SIZE)
            
            cin_base_y = finish_line_top_y 
            
            # --- MUDANÇA AQUI ---
            # Antes era 8, descemos 3 -> Agora são 5 blocos de altura
            offset_altura = 5 * BLOCK_SIZE
            
            cin_draw_y = cin_base_y - self.cin_img.get_height() - offset_altura
            
            cin_x = (SCREEN_WIDTH // 2) - (self.cin_img.get_width() // 2)
            
            self.screen.blit(self.cin_img, (cin_x, cin_draw_y))

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

            self.screen.blit(self.background_image, (0, 0))
            self.draw_text(f"Meta: Chegar ao CIn com {REQUIRED_BADGES} crachás!", self.font, WHITE, SCREEN_WIDTH/2, 140)
            self.draw_text("Escolha seu Personagem:", self.home_font, SHADOWCOLOR, SCREEN_WIDTH/2 + OFFSET, 480 + OFFSET)
            self.draw_text("Escolha seu Personagem:", self.home_font, WHITE, SCREEN_WIDTH/2, 480)

            x1, y1 = SCREEN_WIDTH/2 - 150, 330
            x2, y2 = SCREEN_WIDTH/2 + 50, 330

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
        self.screen.blit(self.gameover_image, (0, 0))
        if self.idle_frames >= 5 * 60:
            motivo = "Você ficou parado muito tempo!"
        elif self.score < REQUIRED_BADGES and self.distance_traveled >= GOAL_DISTANCE:
            motivo = f"Faltaram crachás! {self.score}/{REQUIRED_BADGES}"
        else:
            motivo = "Game Over!"

        self.draw_text("GAME OVER", self.gameover_font, SHADOWCOLOR, SCREEN_WIDTH/2 + OFFSET, SCREEN_HEIGHT/4 + OFFSET)
        self.draw_text("GAME OVER", self.gameover_font, (255, 0, 0), SCREEN_WIDTH/2, SCREEN_HEIGHT/4)
        self.draw_text(motivo, self.alert_font, SHADOWCOLOR, SCREEN_WIDTH/2 + OFFSET_SMALL, SCREEN_HEIGHT/2 + OFFSET_SMALL)
        self.draw_text(motivo, self.alert_font, WHITE, SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
        self.draw_text("Tecle para reiniciar", self.alert_font, SHADOWCOLOR, SCREEN_WIDTH/2 + OFFSET_SMALL, SCREEN_HEIGHT * 3/4 + OFFSET_SMALL)
        self.draw_text("Tecle para reiniciar", self.alert_font, WHITE, SCREEN_WIDTH/2, SCREEN_HEIGHT * 3/4)
        pygame.display.flip()
        self.wait_for_key()

    def show_victory_screen(self):
        self.screen.blit(self.aprovado_image, (0, 0))
        self.draw_text("APROVADO!", self.gameover_font, SHADOWCOLOR, SCREEN_WIDTH/2 + OFFSET, SCREEN_HEIGHT/4 + OFFSET)
        self.draw_text("APROVADO!", self.gameover_font, (142, 248, 67), SCREEN_WIDTH/2, SCREEN_HEIGHT/4)
        self.draw_text(f"Crachás: {self.score}", self.alert_font, SHADOWCOLOR, SCREEN_WIDTH/2 + OFFSET_SMALL, SCREEN_HEIGHT/2 + OFFSET_SMALL)
        self.draw_text(f"Crachás: {self.score}", self.alert_font, WHITE, SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
        self.draw_text("Tecle para reiniciar", self.alert_font, SHADOWCOLOR, SCREEN_WIDTH/2 + OFFSET_SMALL, SCREEN_HEIGHT * 3/4 + OFFSET_SMALL)
        self.draw_text("Tecle para reiniciar", self.alert_font, WHITE, SCREEN_WIDTH/2, SCREEN_HEIGHT * 3/4)
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
        self.idle_frames += 1
        if self.idle_frames >= 5 * 60:
            if self.sound_enabled: pygame.mixer.music.stop()
            self.play_sound("game_over")
            self.state = GAME_OVER
        
        slow_motion_active = False
        if self.slow_motion_timer > 0:
            self.slow_motion_timer -= 1
            slow_motion_active = True
        
        self.manage_traffic()
        
        self.obstacles.update(slow_motion_active=slow_motion_active)
        self.items.update()
        self.player.update() 

        self.check_collisions()

    def draw(self):
        self.draw_background()
        self.all_sprites.draw(self.screen)
        
        # HUD
        self.draw_text(f"Vidas: {self.player.lives}", self.font, BLACK, 60, 10)

        distancia = max(0, GOAL_DISTANCE - self.distance_traveled)
        self.draw_text(f"Faltam: {distancia}m", self.font, (0, 0, 255), SCREEN_WIDTH/2, 10)

        shield_x, shield_y = 150, 10 
        if self.player.has_shield:
            self.screen.blit(self.icon_shield_color, (shield_x, shield_y))
            txt_color = (0, 180, 0)
            status = "ATIVO"
        else:
            self.screen.blit(self.icon_shield_black, (shield_x, shield_y))
            txt_color = BLACK
            status = "OFF"
        self.draw_text(status, self.font, txt_color, shield_x + 60, shield_y + 5)

        badge_x = SCREEN_WIDTH - 140
        badge_y = 10
        self.screen.blit(self.icon_badge_black, (badge_x, badge_y))
        
        ratio = min(self.score / REQUIRED_BADGES, 1.0) 
        if ratio > 0:
            pixel_height = int(32 * ratio) 
            rect_area = (0, 32 - pixel_height, 32, pixel_height)
            self.screen.blit(self.icon_badge_color, (badge_x, badge_y + (32 - pixel_height)), area=rect_area)

        cor_score = (0, 180, 0) if self.score >= REQUIRED_BADGES else BLACK
        self.draw_text(f"{self.score}/{REQUIRED_BADGES}", self.font, cor_score, badge_x + 60, badge_y + 5)

        if self.slow_motion_timer > 0:
            segundos = (self.slow_motion_timer // 60) + 1
            refri_x = SCREEN_WIDTH/2 - 185
            self.screen.blit(self.icon_refri, (refri_x, 80))
            self.draw_text(f"ENERGIZADO: {segundos}s", self.title_font, (0, 255, 255), SCREEN_WIDTH/2 + 20, 80)
            
        elif self.idle_frames > 3 * 60:
            self.draw_text("MOVA-SE!", self.alert_font, (255, 0, 0), SCREEN_WIDTH/2, 80)

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