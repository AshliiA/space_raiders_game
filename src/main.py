import sys
import random
import pygame
from pygame import mixer

# --- Audio init (before pygame.init for best results) ---
pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

# =========================
# Window / FPS
# =========================
fps = 60
clock = pygame.time.Clock()

# Use invaders dimensions for that same feel
WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Raiders")

# =========================
# Fonts / Colors
# =========================
title_font = pygame.font.SysFont(None, 64)
body_font = pygame.font.SysFont(None, 28)
small_font = pygame.font.SysFont(None, 22)

font30 = pygame.font.SysFont("Constantia", 30)
font40 = pygame.font.SysFont("Constantia", 40)

WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# =========================
# Game State
# =========================
MENU = "menu"
PLAYING = "playing"
game_state = MENU
blink_timer = 0

# =========================
# Assets paths
# =========================
IMG_DIR = "assets/images/"
SND_DIR = "assets/sounds/"

# =========================
# Load images / sounds
# =========================
bg = pygame.image.load(IMG_DIR + "bg.png").convert()

laser_fx = pygame.mixer.Sound(SND_DIR + "laser.wav")
laser_fx.set_volume(0.25)

explosion_fx = pygame.mixer.Sound(SND_DIR + "explosion.wav")
explosion_fx.set_volume(0.25)

explosion2_fx = pygame.mixer.Sound(SND_DIR + "explosion2.wav")
explosion2_fx.set_volume(0.25)


# =========================
# Helper: centered text
# =========================
def draw_centered_text(text, font, color, y):
    surface = font.render(text, True, color)
    rect = surface.get_rect(center=(WIDTH // 2, y))
    screen.blit(surface, rect)


def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))


def draw_bg():
    screen.blit(bg, (0, 0))


# =========================
# Invaders-style Classes
# =========================
class Spaceship(pygame.sprite.Sprite):
    def __init__(self, x, y, health):
        super().__init__()
        self.image = pygame.image.load(IMG_DIR + "spaceship.png").convert_alpha()
        self.rect = self.image.get_rect(center=(x, y))

        self.health_start = health
        self.health_remaining = health

        self.last_shot = pygame.time.get_ticks()

    def update(self):
        speed = 8
        cooldown = 500  # ms

        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= speed
        if key[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += speed

        # Shoot
        time_now = pygame.time.get_ticks()
        if key[pygame.K_SPACE] and time_now - self.last_shot > cooldown:
            laser_fx.play()
            bullet = Bullet(self.rect.centerx, self.rect.top)
            bullet_group.add(bullet)
            self.last_shot = time_now

        # Mask for pixel-perfect collision
        self.mask = pygame.mask.from_surface(self.image)

        # Health bar
        pygame.draw.rect(screen, RED, (self.rect.x, self.rect.bottom + 10, self.rect.width, 15))
        if self.health_remaining > 0:
            pygame.draw.rect(
                screen,
                GREEN,
                (
                    self.rect.x,
                    self.rect.bottom + 10,
                    int(self.rect.width * (self.health_remaining / self.health_start)),
                    15,
                ),
            )


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load(IMG_DIR + "bullet.png").convert_alpha()
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.y -= 7
        if self.rect.bottom < 0:
            self.kill()

        # Bullet hits alien
        hit = pygame.sprite.spritecollide(self, alien_group, True)
        if hit:
            self.kill()
            explosion_fx.play()
            explosion_group.add(Explosion(self.rect.centerx, self.rect.centery, 2))


class Alien(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load(
            IMG_DIR + f"alien{random.randint(1, 5)}.png"
        ).convert_alpha()
        self.rect = self.image.get_rect(center=(x, y))
        self.move_counter = 0
        self.move_direction = 1

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 75:
            self.move_direction *= -1
            self.move_counter *= self.move_direction


class AlienBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load(IMG_DIR + "alien_bullet.png").convert_alpha()
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.y += 4
        if self.rect.top > HEIGHT:
            self.kill()

        # Collision with spaceship (pixel-perfect)
        if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask):
            self.kill()
            explosion2_fx.play()
            spaceship.health_remaining -= 1
            explosion_group.add(Explosion(self.rect.centerx, self.rect.centery, 1))


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        super().__init__()
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(IMG_DIR + f"exp{num}.png").convert_alpha()
            if size == 1:
                img = pygame.transform.scale(img, (20, 20))
            elif size == 2:
                img = pygame.transform.scale(img, (40, 40))
            elif size == 3:
                img = pygame.transform.scale(img, (160, 160))
            self.images.append(img)

        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect(center=(x, y))
        self.counter = 0

    def update(self):
        explosion_speed = 3
        self.counter += 1

        if self.counter >= explosion_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]

        if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
            self.kill()


# =========================
# Sprite groups (global)
# =========================
spaceship_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
alien_group = pygame.sprite.Group()
alien_bullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()

# =========================
# Invaders gameplay variables
# =========================
rows = 5
cols = 5

alien_cooldown = 1000
last_alien_shot = 0

countdown = 3
last_count = 0

game_over = 0  # 0 none, 1 win, -1 lose

# We'll store spaceship globally once created
spaceship = None


def create_aliens():
    alien_group.empty()
    for row in range(rows):
        for col in range(cols):
            alien = Alien(100 + col * 100, 100 + row * 70)
            alien_group.add(alien)


def start_new_game():
    """Reset everything to start Invaders-style gameplay."""
    global spaceship, last_alien_shot, countdown, last_count, game_over

    spaceship_group.empty()
    bullet_group.empty()
    alien_bullet_group.empty()
    explosion_group.empty()

    create_aliens()

    spaceship = Spaceship(WIDTH // 2, HEIGHT - 100, 3)
    spaceship_group.add(spaceship)

    last_alien_shot = pygame.time.get_ticks()
    countdown = 3
    last_count = pygame.time.get_ticks()
    game_over = 0


# =========================
# Menu screen (your Sprint 1)
# =========================
def draw_menu():
    screen.fill(BLACK)
    draw_centered_text("SPACE RAIDERS", title_font, WHITE, 140)

    lines = [
        "How to Play:",
        "Move: Left/Right Arrow OR A/D",
        "Shoot: Space",
        "Destroy all aliens to win.",
        "",
        "Press ESC to Quit",
    ]

    y = 260
    for i, line in enumerate(lines):
        color = GRAY if i != 0 else WHITE
        draw_centered_text(line, body_font, color, y)
        y += 36

    # Blinking start
    if (blink_timer // 500) % 2 == 0:
        draw_centered_text("Press ENTER to Start", body_font, WHITE, y)

    draw_centered_text("Sprint 1: Instructions Screen ✅", small_font, GRAY, HEIGHT - 40)


# =========================
# Gameplay draw/update
# =========================
def update_and_draw_invaders():
    global last_alien_shot, countdown, last_count, game_over

    draw_bg()

    # Countdown "GET READY"
    if countdown > 0:
        draw_text("GET READY!", font40, WHITE, int(WIDTH / 2 - 110), int(HEIGHT / 2 + 50))
        draw_text(str(countdown), font40, WHITE, int(WIDTH / 2 - 10), int(HEIGHT / 2 + 100))

        count_timer = pygame.time.get_ticks()
        if count_timer - last_count > 1000:
            countdown -= 1
            last_count = count_timer

    else:
        # Random alien bullets
        time_now = pygame.time.get_ticks()
        if (
            time_now - last_alien_shot > alien_cooldown
            and len(alien_bullet_group) < 5
            and len(alien_group) > 0
            and game_over == 0
        ):
            attacking_alien = random.choice(alien_group.sprites())
            alien_bullet_group.add(AlienBullet(attacking_alien.rect.centerx, attacking_alien.rect.bottom))
            last_alien_shot = time_now

        # Win condition
        if len(alien_group) == 0:
            game_over = 1

        # Update while game active
        if game_over == 0:
            spaceship.update()
            bullet_group.update()
            alien_group.update()
            alien_bullet_group.update()
        else:
            if game_over == -1:
                draw_text("GAME OVER!", font40, WHITE, int(WIDTH / 2 - 110), int(HEIGHT / 2 + 50))
                draw_text("Press ENTER for Menu", font30, WHITE, int(WIDTH / 2 - 140), int(HEIGHT / 2 + 120))
            elif game_over == 1:
                draw_text("YOU WIN!", font40, WHITE, int(WIDTH / 2 - 90), int(HEIGHT / 2 + 50))
                draw_text("Press ENTER for Menu", font30, WHITE, int(WIDTH / 2 - 140), int(HEIGHT / 2 + 120))

    # Lose condition (health <= 0)
    if spaceship and spaceship.health_remaining <= 0 and game_over == 0:
        explosion_group.add(Explosion(spaceship.rect.centerx, spaceship.rect.centery, 3))
        spaceship.kill()
        game_over = -1

    # Explosions always update
    explosion_group.update()

    # Draw everything
    spaceship_group.draw(screen)
    bullet_group.draw(screen)
    alien_group.draw(screen)
    alien_bullet_group.draw(screen)
    explosion_group.draw(screen)


# =========================
# Main loop
# =========================
running = True
while running:
    dt = clock.tick(fps)
    blink_timer += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            # ESC quits anywhere
            if event.key == pygame.K_ESCAPE:
                running = False

            # ENTER behavior depends on state
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                if game_state == MENU:
                    # Start invaders-style game
                    start_new_game()
                    game_state = PLAYING
                elif game_state == PLAYING and game_over != 0:
                    # From win/lose screen, go back to menu
                    game_state = MENU

    # Draw based on state
    if game_state == MENU:
        draw_menu()
    else:
        update_and_draw_invaders()

    pygame.display.flip()

pygame.quit()
sys.exit()