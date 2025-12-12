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
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("CIn Road: Rumo ao Diploma")
        self.clock = pygame.time.Clock()
        
        self.font = pygame.font.SysFont("Arial", 24)
        self.title_font = pygame.font.SysFont("Arial", 48, bold=True)
        
        self.state = START
        self.running = True

    def new_game(self):
        self.all_sprites = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.items = pygame.sprite.Group()

        # Jogador começa lá embaixo
        start_x = GRID_WIDTH // 2
        start_y = GRID_HEIGHT - 2
        
        # AQUI ESTÁ A MUDANÇA MÁGICA:
        # Passamos self.selected_skin que definimos na tela inicial
        self.player = Player(start_x, start_y, self.selected_skin) 
        
        self.all_sprites.add(self.player)

        self.spawn_timer = 0
        self.score = 0
        
        # NOVO: Contador de progresso
        self.distance_traveled = 0 

    def scroll_world(self):
        """
        NOVO: Move o mundo para baixo para simular a câmera subindo.
        """
        self.distance_traveled += 1
        
        # 1. Move tudo que NÃO é o player para baixo
        for sprite in self.all_sprites:
            if sprite != self.player:
                sprite.rect.y += BLOCK_SIZE
                # Se tiver atributo de grid, atualiza também (para lógica futura)
                if hasattr(sprite, 'grid_y'):
                    sprite.grid_y += 1

                # Se sair da tela por baixo, remove para economizar memória
                if sprite.rect.top > SCREEN_HEIGHT:
                    sprite.kill()

        # 2. Gera novos obstáculos no TOPO da tela (Horizonte)
        self.spawn_on_horizon()

    def spawn_on_horizon(self):
        """NOVO: Cria inimigos com dificuldade progressiva"""
        if random.random() < 0.6: 
            if random.random() < 0.7:
                # --- CALCULA DIFICULDADE ---
                # Começa em 1.0 e vai até 2.0 (dobro da velocidade) quando chegar perto da meta
                progress = self.distance_traveled / GOAL_DISTANCE
                dificuldade = 1.0 + (progress * 1.0) # Máximo 2.0x
                
                # Passa a dificuldade para o obstáculo
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
        """
        Mantemos esse spawn aleatório APENAS para preencher buracos,
        mas com menor frequência, já que o scroll_world gera o mapa principal.
        """
        self.spawn_timer += 1
        if self.spawn_timer >= 60: # Mais lento agora
            self.spawn_timer = 0
            # Código de spawn aleatório (opcional manter)
            pass

    def check_collisions(self):
        # 1. NOVO: Vitória baseada na Distância, não na posição Y
        if self.distance_traveled >= GOAL_DISTANCE:
            self.state = VICTORY
            return

        # 2. Colisão Obstáculos
        hit_obstacle = pygame.sprite.spritecollideany(self.player, self.obstacles)
        if hit_obstacle:
            tomou_dano = self.player.check_damage()
            hit_obstacle.kill()

            if tomou_dano:
                if self.player.lives > 0:
                    # Se tomou dano, recua um pouco o progresso ou só reseta posição
                    self.player.reset_position()
                else:
                    self.state = GAME_OVER

        # 3. Colisão Itens
        collected_item = pygame.sprite.spritecollideany(self.player, self.items)
        if collected_item:
            if isinstance(collected_item, BadgeFragment):
                self.score += 1 
            elif isinstance(collected_item, Shield):
                self.player.has_shield = True
            elif isinstance(collected_item, EnergyDrink):
                pass
            collected_item.kill()

    # --- INPUTS COM LÓGICA DE SCROLL ---
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                # --- ESQUERDA (Seta ou A) ---
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.player.move(-1, 0)

                # --- DIREITA (Seta ou D) ---
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.player.move(1, 0)

                # --- BAIXO (Seta ou S) -> Olha para Frente ---
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.player.move(0, 1) 
                
                # --- CIMA (Seta ou W) -> Olha para Costas ---
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    # Lógica da Esteira (Scroll)
                    if self.player.grid_y < 4:
                        self.scroll_world() 
                        # CORREÇÃO: Como o player não chama 'move',
                        # forçamos a sprite de costas manualmente aqui:
                        self.player.update_sprite("back")
                    else:
                        self.player.move(0, -1)

    # ... RESTO DO CÓDIGO (draw_text, Telas, Run, Update, Draw) IGUAL AO ANTERIOR ...
    # Copie as funções draw_text, show_start_screen, etc. do código anterior ou mantenha
    
    def draw_text(self, text, font, color, x, y):
        img = font.render(text, True, color)
        rect = img.get_rect()
        rect.midtop = (x, y)
        self.screen.blit(img, rect)

    def show_start_screen(self):
        try:
            # Carrega usando os nomes EXATOS da sua pasta
            img_p1 = pygame.image.load("assets/img/aluno1frente.png").convert_alpha()
            img_p1 = pygame.transform.scale(img_p1, (100, 100))

            img_p2 = pygame.image.load("assets/img/aluno2frente.png").convert_alpha()
            img_p2 = pygame.transform.scale(img_p2, (100, 100))
        except Exception as e:
            print(f"Erro no menu: {e}")
            sys.exit()

        selection_index = 0 
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    waiting = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        selection_index = 0
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        selection_index = 1
                    elif event.key == pygame.K_RETURN:
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
                # Passamos o nome completo do arquivo inicial
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
        
        # HUD NOVO: Barra de Progresso ou Texto de Distância
        escudo_txt = "SIM" if self.player.has_shield else "NÃO"
        cor_escudo = (0, 200, 0) if self.player.has_shield else BLACK

        self.draw_text(f"Vidas: {self.player.lives}", self.font, BLACK, 60, 10)
        self.draw_text(f"Escudo: {escudo_txt}", self.font, cor_escudo, 200, 10)
        
        # Mostra quanto falta para chegar
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
                self.handle_events() # Inputs mudaram para handle_events no loop
                self.update()
                self.draw()
                self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()