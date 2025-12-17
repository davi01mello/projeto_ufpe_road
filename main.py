import pygame
import sys
import random

from src.config import *
from src.entities.player import Player
from src.entities.obstacles import Obstacle
from src.entities.collectibles import BadgeFragment, EnergyDrink, Shield

# --- CONFIGURAÇÃO GERAL ---
GOAL_DISTANCE = 100 
TOTAL_ROWS = GOAL_DISTANCE + 50 # Buffer de segurança

# Tipos de Linha
ROW_GRASS = 0
ROW_ROAD = 1
ROW_FINISH = 2

# Estados do Jogo
MENU = 0
CHARACTER_SELECT = 1 
PLAYING = 2
GAME_OVER = 3
VICTORY = 4
DIFFICULTY_SELECT = 5
SETTINGS = 6 
TUTORIAL = 7 
CREDITS = 8 

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
        
        # Fontes
        self.font = pygame.font.SysFont("assets/fonts/PressStart2P.ttf", 24)
        self.small_font = pygame.font.SysFont("assets/fonts/PressStart2P.ttf", 18) 
        self.title_font = pygame.font.SysFont("assets/fonts/PressStart2P.ttf", 48, bold=True)
        self.alert_font = pygame.font.SysFont("assets/fonts/PressStart2P.ttf", 36, bold=True)
        self.home_font = pygame.font.SysFont("assets/fonts/PressStart2P.ttf", 40, bold=False)
        self.gameover_font = pygame.font.SysFont("assets/fonts/PressStart2P.ttf", 58, bold = True)
        
        self.state = MENU
        self.running = True
        self.difficulty_multiplier = 1.0 
        self.volume_level = 0.5 
        self.required_badges = 8 
        self.is_fullscreen = True

        self.sounds = {}
        if self.sound_enabled:
            try:
                pygame.mixer.music.load("assets/sounds/musica.mp3")
                pygame.mixer.music.set_volume(self.volume_level) 
                self.sounds["jump"] = pygame.mixer.Sound("assets/sounds/pulo.wav")
                self.sounds["hit"] = pygame.mixer.Sound("assets/sounds/dano.wav")
                self.sounds["collect"] = pygame.mixer.Sound("assets/sounds/item.wav")
                self.sounds["game_over"] = pygame.mixer.Sound("assets/sounds/game_over.wav")
                self.sounds["win"] = pygame.mixer.Sound("assets/sounds/vitoria.wav")
                self.sounds["turbo"] = pygame.mixer.Sound("assets/sounds/item.wav")
                self.update_sound_volumes()
            except: pass

    def update_sound_volumes(self):
        if not self.sound_enabled: return
        try:
            pygame.mixer.music.set_volume(self.volume_level)
            for sound in self.sounds.values():
                sound.set_volume(self.volume_level)
        except: pass

    def play_sound(self, name):
        if self.sound_enabled and name in self.sounds:
            try: self.sounds[name].play()
            except: pass

    # --- NOVO MÉTODO VISUAL: OVERLAY ESCURO ---
    def draw_dim_overlay(self):
        """Desenha uma tela preta semi-transparente para melhorar a leitura"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200) # Transparência (0 a 255). 200 é bem escuro.
        overlay.fill((0, 0, 0)) # Preto
        self.screen.blit(overlay, (0, 0))

    def generate_map_layout(self):
        layout = []
        is_hard_mode = self.difficulty_multiplier >= 1.5
        chance_road = 0.8 if is_hard_mode else 0.5  
        min_road_block = 3 if is_hard_mode else 2   
        max_road_block = 8 if is_hard_mode else 5

        for _ in range(10): layout.append(ROW_GRASS)
        
        while len(layout) < TOTAL_ROWS:
            if random.random() < chance_road:
                num = random.randint(min_road_block, max_road_block)
                for _ in range(num): layout.append(ROW_ROAD)
            else:
                num = random.randint(1, 3) 
                for _ in range(num): layout.append(ROW_GRASS)
        
        for i in range(1, 8):
            layout[-i] = ROW_GRASS
        return layout

    def new_game(self):
        self.map_layout = self.generate_map_layout()
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
        rows_remaining = len(self.map_layout) - 1 - self.distance_traveled
        rows_on_screen = SCREEN_HEIGHT // BLOCK_SIZE
        target_row_index = int(rows_remaining - rows_on_screen)
        
        if target_row_index < 0: return 
        
        current_meter = self.distance_traveled + rows_on_screen 
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
                    
                    base_dificuldade = 1.0 + (progress * 1.5)
                    final_difficulty = base_dificuldade * self.difficulty_multiplier

                    obs = Obstacle(
                        random.choice(["carro", "carro", "circular"]), 
                        speed_multiplier=final_difficulty,
                        fixed_y=screen_y,
                        fixed_direction=direction
                    )
                    
                    self.all_sprites.add(obs)
                    self.obstacles.add(obs)
                    self.lane_timers[logical_index] = random.randint(90, 200)

    def check_collisions(self):
        if self.distance_traveled >= GOAL_DISTANCE:
            if self.sound_enabled: pygame.mixer.music.stop()
            if self.score >= self.required_badges:
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
                        self.state = MENU
                    elif event.key == pygame.K_F11:
                        pygame.display.toggle_fullscreen()
                        self.is_fullscreen = not self.is_fullscreen

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

        if self.cin_img:
            player_y_visual = SCREEN_HEIGHT - (2 * BLOCK_SIZE)
            blocks_to_go = GOAL_DISTANCE - self.distance_traveled
            finish_line_top_y = player_y_visual - (blocks_to_go * BLOCK_SIZE)
            cin_base_y = finish_line_top_y 
            offset_altura = 5 * BLOCK_SIZE
            cin_draw_y = cin_base_y - self.cin_img.get_height() - offset_altura
            cin_x = (SCREEN_WIDTH // 2) - (self.cin_img.get_width() // 2)
            self.screen.blit(self.cin_img, (cin_x, cin_draw_y))

    def draw_text(self, text, font, color, x, y):
        img = font.render(text, True, color)
        rect = img.get_rect()
        rect.midtop = (x, y)
        self.screen.blit(img, rect)

    # --- MENU PRINCIPAL ---
    def show_main_menu(self):
        options = ["INICIAR JOGO", "COMO JOGAR", "CONFIGURAÇÕES", "CRÉDITOS", "SAIR"]
        index = 0
        waiting = True
        pygame.event.clear()
        
        if self.sound_enabled and not pygame.mixer.music.get_busy():
            try: pygame.mixer.music.play(-1)
            except: pass

        while waiting:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.play_sound("jump")
                        index = (index - 1) % len(options)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.play_sound("jump")
                        index = (index + 1) % len(options)
                    elif event.key == pygame.K_RETURN:
                        self.play_sound("collect")
                        if index == 0: self.state = CHARACTER_SELECT
                        elif index == 1: self.state = TUTORIAL
                        elif index == 2: self.state = SETTINGS
                        elif index == 3: self.state = CREDITS
                        elif index == 4: self.running = False
                        waiting = False

            self.screen.blit(self.background_image, (0, 0))
            
            for i, text in enumerate(options):
                color = (255, 255, 0) if i == index else WHITE
                prefix = "> " if i == index else "  "
                
                pos_y = 280 + (i * 50) 
                self.draw_text(f"{prefix}{text}", self.home_font, SHADOWCOLOR, SCREEN_WIDTH/2+2, pos_y+2)
                self.draw_text(f"{prefix}{text}", self.home_font, color, SCREEN_WIDTH/2, pos_y)
            
            pygame.display.flip()

    # --- CONFIGURAÇÕES (COM OVERLAY ESCURO) ---
    def show_settings_screen(self):
        options = ["VOLTAR"]
        waiting = True
        pygame.event.clear()

        while waiting:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.state = MENU 
                        waiting = False
                    
                    if event.key == pygame.K_RETURN:
                        self.play_sound("collect")
                        pygame.display.toggle_fullscreen()
                        self.is_fullscreen = not self.is_fullscreen
                    
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.volume_level = max(0.0, self.volume_level - 0.1)
                        self.update_sound_volumes()
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.volume_level = min(1.0, self.volume_level + 0.1)
                        self.update_sound_volumes()

            self.screen.blit(self.background_image, (0, 0))
            self.draw_dim_overlay() # <--- APLICA O FILTRO ESCURO
            
            self.draw_text("CONFIGURAÇÕES", self.alert_font, WHITE, SCREEN_WIDTH/2, 80)

            # Barra de Volume
            vol_perc = int(self.volume_level * 100)
            self.draw_text(f"VOLUME: {vol_perc}%", self.home_font, WHITE, SCREEN_WIDTH/2, 220)
            self.draw_text("(Setas Esq/Dir)", self.small_font, (200,200,200), SCREEN_WIDTH/2, 260)

            # Tela Cheia Toggle
            status_tela = "LIGADO" if self.is_fullscreen else "DESLIGADO"
            self.draw_text(f"TELA CHEIA: {status_tela}", self.home_font, WHITE, SCREEN_WIDTH/2, 350)
            self.draw_text("(Pressione ENTER)", self.small_font, (200,200,200), SCREEN_WIDTH/2, 390)
            
            self.draw_text("ESC para voltar", self.font, (255, 255, 0), SCREEN_WIDTH/2, 520)

            pygame.display.flip()

    # --- TUTORIAL (COM OVERLAY ESCURO) ---
    def show_tutorial_screen(self):
        waiting = True
        pygame.event.clear()
        
        while waiting:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                        self.state = MENU
                        waiting = False

            self.screen.blit(self.background_image, (0, 0))
            self.draw_dim_overlay() # <--- APLICA O FILTRO ESCURO
            
            self.draw_text("COMO JOGAR", self.alert_font, WHITE, SCREEN_WIDTH/2, 50)
            
            # Controles
            self.draw_text("Use as SETAS ou WASD para mover.", self.font, WHITE, SCREEN_WIDTH/2, 110)
            self.draw_text("Desvie dos carros e obras!", self.font, WHITE, SCREEN_WIDTH/2, 150)
            
            # Ícones e Explicações
            # Crachá
            self.screen.blit(self.icon_badge_color, (150, 230))
            self.draw_text("CRACHÁ: Pontuação para passar.", self.small_font, (200,200,200), SCREEN_WIDTH/2 + 20, 240)

            # Escudo
            self.screen.blit(self.icon_shield_color, (150, 310))
            self.draw_text("CAPACETE: Protege de 1 dano.", self.small_font, (200,200,200), SCREEN_WIDTH/2 + 20, 320)

            # Energético
            self.screen.blit(self.icon_refri, (150, 390))
            self.draw_text("ENERGÉTICO: Câmera Lenta (5s).", self.small_font, (200,200,200), SCREEN_WIDTH/2 + 20, 400)

            self.draw_text("Pressione ENTER para voltar", self.font, (255, 255, 0), SCREEN_WIDTH/2, 520)
            pygame.display.flip()

    # --- CRÉDITOS (COM OVERLAY ESCURO) ---
    def show_credits_screen(self):
        waiting = True
        pygame.event.clear()
        
        team = [
            "Davi de Souza Mello",
            "Davi Rosendo Carvalho",
            "Gabriel Godoy Carvalho",
            "João Felipe Costa",
            "João Pedro Medeiros",
            "Vitor Costa Nunes"
        ]

        while waiting:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                        self.state = MENU
                        waiting = False

            self.screen.blit(self.background_image, (0, 0))
            self.draw_dim_overlay() # <--- APLICA O FILTRO ESCURO
            
            self.draw_text("CRÉDITOS", self.alert_font, WHITE, SCREEN_WIDTH/2, 60)
            self.draw_text("Equipe de Desenvolvimento:", self.font, (200,200,200), SCREEN_WIDTH/2, 120)

            for i, name in enumerate(team):
                self.draw_text(name, self.font, WHITE, SCREEN_WIDTH/2, 180 + (i * 40))

            self.draw_text("Pressione ENTER para voltar", self.font, (255, 255, 0), SCREEN_WIDTH/2, 520)
            pygame.display.flip()

    def show_character_select(self): 
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

    # --- DIFICULDADE (CORRIGIDO: POSIÇÃO DO TÍTULO EMBAIXO) ---
    def show_difficulty_screen(self):
        options = [("FÁCIL", 0.6), ("MÉDIO", 1.2), ("DIFÍCIL", 2.0)]
        index = 1 
        waiting = True
        self.difficulty_multiplier = 1.0
        
        pygame.event.clear()
        
        while waiting:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    waiting = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.play_sound("jump")
                        index = (index - 1) % len(options)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.play_sound("jump")
                        index = (index + 1) % len(options)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.play_sound("collect")
                        self.difficulty_multiplier = options[index][1]
                        
                        if self.difficulty_multiplier >= 2.0: 
                            self.required_badges = 3  
                        else:
                            self.required_badges = 8  
                        
                        waiting = False

            self.screen.blit(self.background_image, (0, 0))
            
            # --- CORREÇÃO AQUI: Mudança do Y para 480 (embaixo, como pedido) ---
            self.draw_text("SELECIONE A DIFICULDADE", self.alert_font, SHADOWCOLOR, SCREEN_WIDTH/2 + 2, 480 + 2)
            self.draw_text("SELECIONE A DIFICULDADE", self.alert_font, WHITE, SCREEN_WIDTH/2, 480)
            # -------------------------------------------------------------------

            for i, (text, mult) in enumerate(options):
                color = (255, 255, 0) if i == index else WHITE
                prefix = "> " if i == index else "  "
                pos_y = 300 + (i * 60)
                
                if text == "DIFÍCIL":
                     extra_info = " (Meta: 3 Crachás)"
                else:
                     extra_info = " (Meta: 8 Crachás)"

                self.draw_text(f"{prefix}{text}{extra_info}", self.home_font, SHADOWCOLOR, SCREEN_WIDTH/2 + 2, pos_y + 2)
                self.draw_text(f"{prefix}{text}{extra_info}", self.home_font, color, SCREEN_WIDTH/2, pos_y)

            pygame.display.flip()

    def show_game_over_screen(self):
        self.screen.blit(self.gameover_image, (0, 0))
        if self.idle_frames >= 5 * 60:
            motivo = "Você ficou parado muito tempo!"
        elif self.score < self.required_badges and self.distance_traveled >= GOAL_DISTANCE:
            motivo = f"Faltaram crachás! {self.score}/{self.required_badges}"
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
        self.draw_text(f"Crachás: {self.score}/{self.required_badges}", self.alert_font, SHADOWCOLOR, SCREEN_WIDTH/2 + OFFSET_SMALL, SCREEN_HEIGHT/2 + OFFSET_SMALL)
        self.draw_text(f"Crachás: {self.score}/{self.required_badges}", self.alert_font, WHITE, SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
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
        
        ratio = min(self.score / self.required_badges, 1.0) 
        if ratio > 0:
            pixel_height = int(32 * ratio) 
            rect_area = (0, 32 - pixel_height, 32, pixel_height)
            self.screen.blit(self.icon_badge_color, (badge_x, badge_y + (32 - pixel_height)), area=rect_area)

        cor_score = (0, 180, 0) if self.score >= self.required_badges else BLACK
        self.draw_text(f"{self.score}/{self.required_badges}", self.font, cor_score, badge_x + 60, badge_y + 5)

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
            if self.state == MENU:
                self.show_main_menu()
            
            elif self.state == SETTINGS:
                self.show_settings_screen()
            
            elif self.state == TUTORIAL:
                self.show_tutorial_screen()

            elif self.state == CREDITS:
                self.show_credits_screen()

            elif self.state == CHARACTER_SELECT:
                self.show_character_select()
                if self.running:
                    self.state = DIFFICULTY_SELECT
            
            elif self.state == DIFFICULTY_SELECT:
                self.show_difficulty_screen()
                if self.running:
                    self.new_game()
                    self.state = PLAYING
            
            elif self.state == GAME_OVER:
                self.show_game_over_screen()
                self.state = MENU 
            
            elif self.state == VICTORY:
                self.show_victory_screen()
                self.state = MENU 
            
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