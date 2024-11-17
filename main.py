import pygame
import random
import math
import json
import os

# --- Inicialización ---
pygame.init()
pygame.mixer.init()

# --- Colores ---

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# --- Inicializar la pantalla en modo pantalla completa ---
def initialize_screen():
    global screen, SCREEN_WIDTH, SCREEN_HEIGHT
    # Obtener el tamaño de la pantalla completa
    SCREEN_WIDTH = pygame.display.Info().current_w
    SCREEN_HEIGHT = pygame.display.Info().current_h
    # Establecer el modo de pantalla completa
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)

# No es necesario ajustar la escala en pantalla completa
def adjust_scale():
    pass  # Puedes eliminar esta función si no la necesitas

# Llamar a initialize_screen para inicializar la pantalla
initialize_screen()

# --- Crear la ventana del juego ---

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Zombies Dead')

# --- Función para cargar imágenes ---

def load_image(name, width, height):
    image = pygame.image.load(name).convert_alpha()
    return pygame.transform.scale(image, (width, height))

# --- Función para cargar animaciones ---

def load_animation(frames, width, height):
    return [load_image(frame, width, height) for frame in frames]

# --- Cargar sonidos ---

def load_sound(name):
    return pygame.mixer.Sound(name)

# --- Cargar música ---

def load_music(name):
    pygame.mixer.music.load(name)
    pygame.mixer.music.play(-1)

# --- Cargar imágenes y sonidos ---

player_images = load_animation(['player_walk1.png', 'player_walk2.png'], 50, 50)
zombie_images = load_animation(['zombie_walk1.png', 'zombie_walk2.png'], 50, 50)
fast_zombie_images = load_animation(['fast_zombie_walk1.png', 'fast_zombie_walk2.png'], 50, 50)
strong_zombie_images = load_animation(['strong_zombie_walk1.png', 'strong_zombie_walk2.png'], 50, 50)
bullet_img = load_image('bullet.png', 10, 10)
health_pack_img = load_image('health_pack.png', 40, 40)
ammo_pack_img = load_image('ammo_pack.png', 40, 40)
explosive_img = load_image('explosive.png', 50, 50)
boss_img = load_image('boss_zombie.jpg', 100, 100)

bullet_sound = load_sound('shoot.mp3')
zombie_hit_sound = load_sound('zombiee.mp3')
explosion_sound = load_sound('explosive_sound.mp3')

# --- Inicializar la música de fondo ---

load_music('musica_inicio.mp3')

# --- Función para cargar fuentes ---

font = pygame.font.Font(None, 36)
title_font = pygame.font.Font(None, 72)

# --- Clases del juego ---

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # Animaciones de caminar (usando las imágenes existentes)
        self.walk_right_images = load_animation(['player_walk1.png', 'player_walk2.png'], 50, 50)
        self.walk_left_images = load_animation(['player_walk1.png', 'player_walk2.png'], 50, 50)  # Podrías agregar imágenes separadas si tienes
        self.walk_up_images = load_animation(['player_walk1.png', 'player_walk2.png'], 50, 50)  # Igualmente si tienes imágenes para arriba
        self.walk_down_images = load_animation(['player_walk1.png', 'player_walk2.png'], 50, 50)  # Y para abajo

        # Imagen de reposo
        self.idle_image = load_image('player_idle.png', 50, 50)

        # Inicializamos la imagen y el rectángulo
        self.image = self.idle_image
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

        # Propiedades del jugador
        self.speed = 5
        self.health = 100
        self.max_health = 100
        self.ammo = 10
        self.score = 0
        self.level = 1
        self.experience = 0
        self.is_paused = False
        self.animation_index = 0
        self.animation_speed = 0.1
        self.last_update = pygame.time.get_ticks()

    def update(self):
        keys = pygame.key.get_pressed()
        if not self.is_paused:
            movement_x = 0
            movement_y = 0

            # Mover al jugador y elegir la animación según la dirección
            if keys[pygame.K_LEFT]:
                movement_x = -self.speed
                self.image = self.walk_left_images[int(self.animation_index)]  # Usar las animaciones de caminar hacia la izquierda
            elif keys[pygame.K_RIGHT]:
                movement_x = self.speed
                self.image = self.walk_right_images[int(self.animation_index)]  # Usar las animaciones de caminar hacia la derecha
            elif keys[pygame.K_UP]:
                movement_y = -self.speed
                self.image = self.walk_up_images[int(self.animation_index)]  # Usar las animaciones de caminar hacia arriba
            elif keys[pygame.K_DOWN]:
                movement_y = self.speed
                self.image = self.walk_down_images[int(self.animation_index)]  # Usar las animaciones de caminar hacia abajo

            # Si no se mueve, se mantiene la imagen de reposo
            if movement_x == 0 and movement_y == 0:
                self.image = self.idle_image

            # Actualizar la posición del jugador
            self.rect.x += movement_x
            self.rect.y += movement_y

            # Cambiar la animación cada 200 ms (más fluido)
            now = pygame.time.get_ticks()
            if now - self.last_update > 200:
                self.animation_index = (self.animation_index + 1) % len(self.walk_right_images)  # Cambiar según el número de frames en la animación
                self.last_update = now

    def draw_health_bar(self, surface):
        health_ratio = self.health / self.max_health
        pygame.draw.rect(surface, RED, (self.rect.x, self.rect.y - 10, 50, 5))
        pygame.draw.rect(surface, GREEN, (self.rect.x, self.rect.y - 10, 50 * health_ratio, 5))

    def shoot(self):
        if self.ammo > 0 and not self.is_paused:
            bullet = Bullet(self.rect.centerx, self.rect.centery)
            all_sprites.add(bullet)
            bullets.add(bullet)
            self.ammo -= 1
            bullet_sound.play()

    def special_attack(self):
        if self.special_attack_cooldown == 0:
            explosion = Explosion(self.rect.centerx, self.rect.centery)
            all_sprites.add(explosion)
            explosion_sound.play()
            self.special_attack_cooldown = self.special_attack_max_cooldown

    def is_dead(self):
        # Método para verificar si el jugador está muerto (salud <= 0)
        return self.health <= 0
    
class Zombie(pygame.sprite.Sprite):
    def __init__(self, type='normal'):
        super().__init__()
        self.type = type
        if type == 'normal':
            self.images = zombie_images
            self.health = 50
            self.speed = 2  # Velocidad normal del zombie
        elif type == 'fast':
            self.images = fast_zombie_images
            self.health = 30
            self.speed = 3  # Un poco más rápido
        elif type == 'strong':
            self.images = strong_zombie_images
            self.health = 80
            self.speed = 2  # Velocidad normal del zombie

        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH)
        self.rect.y = random.randint(0, SCREEN_HEIGHT)
        self.animation_index = 0
        self.animation_speed = 0.1
        self.last_update = pygame.time.get_ticks()

    def update(self):
        if not player.is_paused:  # Solo mueve el zombie si el juego no está pausado
            direction = math.atan2(player.rect.y - self.rect.y, player.rect.x - self.rect.x)
            self.rect.x += math.cos(direction) * self.speed
            self.rect.y += math.sin(direction) * self.speed

            # Manejar animaciones (Aumenta el intervalo de actualización)
            now = pygame.time.get_ticks()
            if now - self.last_update > 200:  # Cambia la animación cada 200 ms
                self.animation_index = (self.animation_index + 1) % len(self.images)
                self.image = self.images[self.animation_index]
                self.last_update = now

            # Verificar colisiones con el jugador
            if self.rect.colliderect(player.rect):
                player.health -= 5
                self.kill()  # Eliminar el zombie al colisionar

class BossZombie(Zombie):
    def __init__(self):
        super().__init__(type='strong')
        self.image = boss_img
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.health = 200
        self.speed = 1

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = bullet_img
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 10

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()

class HealthPack(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = health_pack_img
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        if self.rect.colliderect(player.rect):
            player.health += 30
            player.health = min(player.health, player.max_health)
            self.kill()

class AmmoPack(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = ammo_pack_img
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        if self.rect.colliderect(player.rect):
            player.ammo += 5
            player.ammo = min(player.ammo, 30)
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.images = [load_image('explosion1.png', 50, 50),
                       load_image('explosion2.png', 70, 70),
                       load_image('explosion3.png', 90, 90),
                       load_image('explosion4.png', 110, 110),
                       load_image('explosion5.png', 130, 130)]
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.animation_index = 0
        self.animation_speed = 0.2
        self.last_update = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 100:  # Cambia la animación cada 100 ms
            self.animation_index = (self.animation_index + 1) % len(self.images)
            self.image = self.images[self.animation_index]
            self.last_update = now

        if self.animation_index == len(self.images) - 1:
            self.kill()

# --- Función para guardar el progreso del jugador ---

def save_game():
    data = {
        'score': player.score,
        'health': player.health,
        'ammo': player.ammo,
        'level': player.level,
        'experience': player.experience
    }
    with open('save_data.json', 'w') as f:
        json.dump(data, f)

# --- Función para cargar el progreso del jugador ---

def load_game():
    if os.path.exists('save_data.json'):
        with open('save_data.json', 'r') as f:
            data = json.load(f)
            player.score = data.get('score', 0)
            player.health = data.get('health', 100)
            if player.health <= 0:  # Para evitar comenzar con salud 0 o negativa
                player.health = player.max_health
            player.ammo = data.get('ammo', 10)
            player.level = data.get('level', 1)
            player.experience = data.get('experience', 0)

# --- Inicializar grupos de sprites ---

all_sprites = pygame.sprite.Group()
zombies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
health_packs = pygame.sprite.Group()
ammo_packs = pygame.sprite.Group()
explosions = pygame.sprite.Group()

# --- Crear el jugador ---

player = Player()
all_sprites.add(player)

# --- Pantalla de inicio ---
def show_start_screen():
    running = True
    title_pos_y = SCREEN_HEIGHT // 2 - 50
    title_scale = 1.0
    scale_direction = 0.01  # Para escalar el título

    # Cargar un fondo de apocalipsis (asegúrate de tener esta imagen)
    background_image = load_image('apocalypse_background.jpg', SCREEN_WIDTH, SCREEN_HEIGHT)

    while running:
        screen.blit(background_image, (0, 0))  # Mostrar el fondo

        # Animar título con escalado suave
        title_surface = title_font.render('Zombies Dead', True, WHITE)
        title_surface = pygame.transform.scale(title_surface, (int(title_surface.get_width() * title_scale), int(title_surface.get_height() * title_scale)))
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, title_pos_y))

        title_pos_y += 0.5  # Movimiento hacia abajo
        if title_pos_y > SCREEN_HEIGHT // 2 - 20:  # Limitar el movimiento
            title_pos_y = SCREEN_HEIGHT // 2 - 50

        title_scale += scale_direction
        if title_scale >= 1.1 or title_scale <= 0.9:  # Alternar dirección de escalado
            scale_direction *= -1

        screen.blit(title_surface, title_rect)

        # Mostrar efecto de oscuridad parpadeante
        fog_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        fog_surface.fill((0, 0, 0, 100 + int(100 * math.sin(pygame.time.get_ticks() * 0.005))))  # Oscuridad parpadeante
        screen.blit(fog_surface, (0, 0))

        # Mostrar botón de inicio
        button_surface = font.render('Presiona ENTER para iniciar', True, WHITE)
        button_rect = button_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        screen.blit(button_surface, button_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Iniciar el juego
                    running = False

    # --- Pantalla de inicio ---
show_start_screen()

# --- Cargar progreso si existe ---
load_game()

# --- Función para mostrar la pantalla de Game Over ---
def show_game_over_screen():
    running = True
    while running:
        screen.fill(BLACK)
        
        game_over_surface = font.render('GAME OVER', True, RED)
        game_over_rect = game_over_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(game_over_surface, game_over_rect)

        restart_surface = font.render('Presiona R para reiniciar o ESC para salir', True, WHITE)
        restart_rect = restart_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        screen.blit(restart_surface, restart_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Reiniciar el juego
                    return True  # Retornar True para reiniciar
                if event.key == pygame.K_ESCAPE:  # Salir del juego
                    return False  # Retornar False para salir

# --- Función para mostrar el menú de pausa ultra mejorado ---
def show_pause_menu():
    running = True
    selected_option = 0
    options = ["Reanudar", "Reiniciar", "Salir"]
    option_colors = [WHITE] * len(options)
    background_color = (30, 30, 30)
    fade_alpha = 0
    fading_in = True

    while running:
        screen.fill(background_color)
        pause_background = load_image('pause_background.jpg', SCREEN_WIDTH, SCREEN_HEIGHT)
        pause_background.set_alpha(fade_alpha)
        screen.blit(pause_background, (0, 0))

        title_surface = title_font.render('MENU DE PAUSA', True, (255, 215, 0))
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 150))
        screen.blit(title_surface, title_rect)

        for i, option in enumerate(options):
            scale_factor = 1.0 + (0.1 if i == selected_option else 0)
            option_surface = font.render(option, True, option_colors[i])
            option_surface = pygame.transform.scale(option_surface, (int(option_surface.get_width() * scale_factor), int(option_surface.get_height() * scale_factor)))
            option_rect = option_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50 + i * 60))
            screen.blit(option_surface, option_rect)

            option_colors = [WHITE] * len(options)
            option_colors[selected_option] = (255, 255, 0)

        fog_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        fog_surface.fill((0, 0, 0, 100 + int(100 * math.sin(pygame.time.get_ticks() * 0.005))))
        screen.blit(fog_surface, (0, 0))

        if fading_in:
            fade_alpha += 5
            if fade_alpha >= 255:
                fade_alpha = 255
                fading_in = False
        else:
            fade_alpha -= 5
            if fade_alpha <= 0:
                fade_alpha = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                elif event.key == pygame.K_RETURN:  # Seleccionar opción
                    if selected_option == 0:  # Reanudar
                        running = False
                    elif selected_option == 1:  # Reiniciar
                        return True  # Retornar para reiniciar
                    elif selected_option == 2:  # Salir
                        return False  # Retornar para salir

        pygame.display.flip()

  # --- Pantalla de inicio ---
show_start_screen()

# --- Cargar progreso si existe ---
load_game()

# --- Función para mostrar la pantalla de Game Over ---
def show_game_over_screen():
    running = True
    while running:
        screen.fill(BLACK)
        
        game_over_surface = font.render('GAME OVER', True, RED)
        game_over_rect = game_over_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(game_over_surface, game_over_rect)

        restart_surface = font.render('Presiona R para reiniciar o ESC para salir', True, WHITE)
        restart_rect = restart_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        screen.blit(restart_surface, restart_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Reiniciar el juego
                    return True  # Retornar True para reiniciar
                if event.key == pygame.K_ESCAPE:  # Salir del juego
                    return False  # Retornar False para salir

# --- Función para mostrar el menú de pausa ultra mejorado ---
def show_pause_menu():
    running = True
    selected_option = 0
    options = ["Reanudar", "Reiniciar", "Salir"]
    option_colors = [WHITE] * len(options)
    background_color = (30, 30, 30)
    fade_alpha = 0
    fading_in = True

    while running:
        screen.fill(background_color)
        pause_background = load_image('pause_background.jpg', SCREEN_WIDTH, SCREEN_HEIGHT)
        pause_background.set_alpha(fade_alpha)
        screen.blit(pause_background, (0, 0))

        title_surface = title_font.render('MENU DE PAUSA', True, (255, 215, 0))
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 150))
        screen.blit(title_surface, title_rect)

        for i, option in enumerate(options):
            scale_factor = 1.0 + (0.1 if i == selected_option else 0)
            option_surface = font.render(option, True, option_colors[i])
            option_surface = pygame.transform.scale(option_surface, (int(option_surface.get_width() * scale_factor), int(option_surface.get_height() * scale_factor)))
            option_rect = option_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50 + i * 60))
            screen.blit(option_surface, option_rect)

            option_colors = [WHITE] * len(options)
            option_colors[selected_option] = (255, 255, 0)

        fog_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        fog_surface.fill((0, 0, 0, 100 + int(100 * math.sin(pygame.time.get_ticks() * 0.005))))
        screen.blit(fog_surface, (0, 0))

        if fading_in:
            fade_alpha += 5
            if fade_alpha >= 255:
                fade_alpha = 255
                fading_in = False
        else:
            fade_alpha -= 5
            if fade_alpha <= 0:
                fade_alpha = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                elif event.key == pygame.K_RETURN:  # Seleccionar opción
                    if selected_option == 0:  # Reanudar
                        running = False
                    elif selected_option == 1:  # Reiniciar
                        return True  # Retornar para reiniciar
                    elif selected_option == 2:  # Salir
                        return False  # Retornar para salir

        pygame.display.flip()

# --- Bucle principal del juego --- 
running = True
wave = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_game()
            running = False
            # Si deseas permitir salir del modo pantalla completa, puedes usar una tecla
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # Presionar ESC para salir
                running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()
            if event.key == pygame.K_p:  # Pausar el juego
                player.is_paused = not player.is_paused
                if player.is_paused:
                    should_restart = show_pause_menu()  # Mostrar menú de pausa
                    if should_restart is False:
                        running = False  # Salir del juego
                    elif should_restart is True:
                        # Reiniciar variables del juego aquí
                        player = Player()  # Reinicia el jugador
                        all_sprites = pygame.sprite.Group()  # Reinicia todos los sprites
                        zombies.empty()  # Limpia los zombies
                        bullets.empty()  # Limpia las balas
                        health_packs.empty()  # Limpia los paquetes de salud
                        ammo_packs.empty()  # Limpia los paquetes de munición
                        explosions.empty()  # Limpia las explosiones
                        all_sprites.add(player)  # Agrega el jugador nuevamente
                        wave = 0  # Reinicia la ola
                        load_game()  # Carga el progreso si existe

            if event.key == pygame.K_s:
                save_game()
            if event.key == pygame.K_e:  # Ataque especial
                player.special_attack()

    if not player.is_paused:
        all_sprites.update()

    # --- Colisiones entre balas y zombies --- 
    hits = pygame.sprite.groupcollide(bullets, zombies, False, False)
    for bullet, zombie_list in hits.items():
        for zombie in zombie_list:
            zombie.health -= 10
            bullet.kill()
            if zombie.health <= 0:
                player.gain_experience(10)
                player.score += 100
                zombie_hit_sound.play()
                zombie.kill()

    # --- Verificar si el jugador está muerto --- 
    if player.is_dead():
        running = False  # Termina el bucle del juego
        restart = show_game_over_screen()  # Mostrar pantalla de Game Over
        if restart:
            # Reiniciar variables del juego
            player = Player()  # Reinicia el jugador
            all_sprites = pygame.sprite.Group()  # Reinicia todos los sprites
            zombies.empty()  # Limpia los zombies
            bullets.empty()  # Limpia las balas
            health_packs.empty()  # Limpia los paquetes de salud
            ammo_packs.empty()  # Limpia los paquetes de munición
            explosions.empty()  # Limpia las explosiones
            all_sprites.add(player)  # Agrega el jugador nuevamente
            wave = 0  # Reinicia la ola
            load_game()  # Carga el progreso si existe
            running = True  # Reinicia el bucle del juego

    # --- Generar más zombies por oleada --- 
    if len(zombies) == 0:
        wave += 1
        for _ in range(2 + wave):  # Crea más zombies por ola
            zombie = Zombie(type=random.choice(['normal', 'fast', 'strong']))
            all_sprites.add(zombie)
            zombies.add(zombie)

        if wave % 5 == 0:
            boss_zombie = BossZombie()
            all_sprites.add(boss_zombie)
            zombies.add(boss_zombie)

    # Generar paquetes de salud y munición
    health_pack = HealthPack(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))
    ammo_pack = AmmoPack(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))
    if random.randint(1, 300) == 1:
        all_sprites.add(health_pack)
        health_packs.add(health_pack)

    if random.randint(1, 300) == 1:
        all_sprites.add(ammo_pack)
        ammo_packs.add(ammo_pack)

    # Dibuja todo en la pantalla 
    screen.fill(BLACK)
    all_sprites.draw(screen)
    player.draw_health_bar(screen)

    # Mostrar puntuación y estado 
    score_surface = font.render(f'Score: {player.score}  Wave: {wave}  Ammo: {player.ammo}  Health: {player.health}/{player.max_health}', True, WHITE)
    screen.blit(score_surface, (10, 10))

        # Mostrar mensaje de pausa 
    if player.is_paused:
            pause_surface = font.render('Juego Pausado', True, YELLOW)
            pause_rect = pause_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(pause_surface, pause_rect)

    pygame.display.flip()

pygame.quit()

    # --- Colisiones entre balas y zombies --- 
hits = pygame.sprite.groupcollide(bullets, zombies, False, False)
for bullet, zombie_list in hits.items():
        for zombie in zombie_list:
            zombie.health -= 10
            bullet.kill()
            if zombie.health <= 0:
                player.gain_experience(10)
                player.score += 100
                zombie_hit_sound.play()
                zombie.kill()

    # --- Verificar si el jugador está muerto --- 
if player.is_dead():
        running = False  # Termina el bucle del juego
        restart = show_game_over_screen()  # Mostrar pantalla de Game Over
        if restart:
            # Reiniciar variables del juego
            player = Player()  # Reinicia el jugador
            all_sprites = pygame.sprite.Group()  # Reinicia todos los sprites
            zombies.empty()  # Limpia los zombies
            bullets.empty()  # Limpia las balas
            health_packs.empty()  # Limpia los paquetes de salud
            ammo_packs.empty()  # Limpia los paquetes de munición
            explosions.empty()  # Limpia las explosiones
            all_sprites.add(player)  # Agrega el jugador nuevamente
            wave = 0  # Reinicia la ola
            load_game()  # Carga el progreso si existe
            running = True  # Reinicia el bucle del juego

    # --- Generar más zombies por oleada --- 
if len(zombies) == 0:
        wave += 1
        for _ in range(2 + wave):  # Crea más zombies por ola
            zombie = Zombie(type=random.choice(['normal', 'fast', 'strong']))
            all_sprites.add(zombie)
            zombies.add(zombie)

        if wave % 5 == 0:
            boss_zombie = BossZombie()
            all_sprites.add(boss_zombie)
            zombies.add(boss_zombie)

  # Generar paquetes de salud y munición
        if random.randint(1, 300) == 1:
            health_pack = HealthPack(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))
            all_sprites.add(health_pack)
            health_packs.add(health_pack)

        if random.randint(1, 300) == 1:
            ammo_pack = AmmoPack(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))
            all_sprites.add(ammo_pack)
            ammo_packs.add(ammo_pack)

    # Dibuja todo en la pantalla 
screen.fill(BLACK)
all_sprites.draw(screen)
player.draw_health_bar(screen)

    # Mostrar puntuación y estado 
score_surface = font.render(f'Score: {player.score}  Wave: {wave}  Ammo: {player.ammo}  Health: {player.health}/{player.max_health}', True, WHITE)
screen.blit(score_surface, (10, 10))

        # Mostrar mensaje de pausa 
if player.is_paused:
            pause_surface = font.render('Juego Pausado', True, YELLOW)
            pause_rect = pause_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(pause_surface, pause_rect)

pygame.display.flip()

pygame.quit()
