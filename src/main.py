import sys
import pygame

pygame.init()

# --- Window setup ---
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Raiders")

clock = pygame.time.Clock()

# --- Fonts ---
title_font = pygame.font.SysFont(None, 64)
body_font = pygame.font.SysFont(None, 28)
small_font = pygame.font.SysFont(None, 22)

WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)

# --- Game state ---
MENU = "menu"
PLAYING = "playing"
GAME_OVER = "game_over"
game_state = MENU

# --- Player setup (simple placeholder for now) ---
player = pygame.Rect(WIDTH // 2 - 25, HEIGHT - 80, 50, 50)
player_speed = 6

# --- Optional: add a simple "health" placeholder (we’ll build this later) ---
player_health = 3


def draw_centered_text(text, font, color, y):
    """Helper to center text horizontally."""
    surface = font.render(text, True, color)
    rect = surface.get_rect(center=(WIDTH // 2, y))
    screen.blit(surface, rect)


def draw_instructions_screen():
    screen.fill(BLACK)

    draw_centered_text("SPACE RAIDERS", title_font, WHITE, 120)

    lines = [
        "How to Play:",
        "Move: Left/Right Arrow OR A/D",
        "Shoot: Space (coming next sprint)",
        "Avoid enemies and survive as long as you can.",
        "",
        "Press ENTER to Start",
        "Press ESC to Quit",
    ]

    y = 220
    for i, line in enumerate(lines):
        color = GRAY if i != 0 else WHITE
        draw_centered_text(line, body_font, color, y)
        y += 36

    draw_centered_text("Sprint 1: Instructions Screen ✅", small_font, GRAY, HEIGHT - 40)


def draw_play_screen():
    screen.fill(BLACK)

    # Draw player (placeholder)
    pygame.draw.rect(screen, WHITE, player)

    # Example HUD (health placeholder)
    hud = body_font.render(f"Health: {player_health}", True, WHITE)
    screen.blit(hud, (20, 20))


running = True
while running:
    clock.tick(60)

    # --- Events ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            # ESC quits from anywhere
            if event.key == pygame.K_ESCAPE:
                running = False

            # Start the game from the menu
            if game_state == MENU and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                game_state = PLAYING

    # --- Update ---
    keys = pygame.key.get_pressed()

    if game_state == PLAYING:
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.x -= player_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.x += player_speed

        # Keep player on screen
        player.x = max(0, min(WIDTH - player.width, player.x))

    # --- Draw ---
    if game_state == MENU:
        draw_instructions_screen()
    elif game_state == PLAYING:
        draw_play_screen()
    else:
        screen.fill(BLACK)
        draw_centered_text("GAME OVER", title_font, WHITE, HEIGHT // 2)

    pygame.display.flip()

pygame.quit()
sys.exit()
