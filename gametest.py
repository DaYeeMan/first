import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wave Survival Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Clock and FPS
clock = pygame.time.Clock()
FPS = 60

# Font settings
font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 72)

# Player settings
player_pos = [WIDTH // 2, HEIGHT // 2]
player_size = 20
player_speed = 5

# Bullet settings
bullet_speed = 10
bullets = []
bullet_cooldown = 300  # Milliseconds between bullets
last_bullet_time = 0

# Enemy settings
enemies = []
enemy_size = 15
enemy_speed = 2
wave = 1

# Score tracking
score = 0

# Function to spawn enemies
def spawn_enemies(num):
    for _ in range(num):
        x, y = random.choice([(random.randint(0, WIDTH), random.choice([0, HEIGHT])),
                              (random.choice([0, WIDTH]), random.randint(0, HEIGHT))])
        enemies.append({"pos": [x, y]})

# Function to check for collision
def check_collision(rect_pos, rect_size, circle_pos, circle_radius):
    dist_x = abs(rect_pos[0] - circle_pos[0])
    dist_y = abs(rect_pos[1] - circle_pos[1])
    dist = math.sqrt(dist_x ** 2 + dist_y ** 2)
    return dist < rect_size + circle_radius

# Function to handle upgrades
def handle_upgrade():
    global player_speed, bullet_speed, bullet_cooldown, player_pos

    upgrading = True
    upgrade_text = font.render(
        "Choose Upgrade: 1. Speed 2. Bullet Speed 3. Firing Rate", True, WHITE
    )
    while upgrading:
        screen.fill(BLACK)
        screen.blit(upgrade_text, (WIDTH // 2 - 300, HEIGHT // 2 - 20))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    player_speed += 1
                    upgrading = False
                elif event.key == pygame.K_2:
                    bullet_speed += 5
                    upgrading = False
                elif event.key == pygame.K_3:
                    bullet_cooldown = max(20, bullet_cooldown - 50)
                    upgrading = False

    # Reset player position to center
    player_pos = [WIDTH // 2, HEIGHT // 2]

# Function for the start menu
def start_menu():
    menu_running = True
    title_text = big_font.render("Wave Survival Game", True, WHITE)
    start_text = font.render("Press ENTER to Start", True, WHITE)

    while menu_running:
        screen.fill(BLACK)
        screen.blit(title_text, (WIDTH // 2 - 200, HEIGHT // 2 - 100))
        screen.blit(start_text, (WIDTH // 2 - 150, HEIGHT // 2 + 50))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                menu_running = False

# Main game loop
start_menu()
running = True
spawn_enemies(wave)

while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] and player_pos[1] > 0:
        player_pos[1] -= player_speed
    if keys[pygame.K_s] and player_pos[1] < HEIGHT - player_size:
        player_pos[1] += player_speed
    if keys[pygame.K_a] and player_pos[0] > 0:
        player_pos[0] -= player_speed
    if keys[pygame.K_d] and player_pos[0] < WIDTH - player_size:
        player_pos[0] += player_speed

    # Shooting bullets with cooldown
    if pygame.mouse.get_pressed()[0]:
        current_time = pygame.time.get_ticks()
        if current_time - last_bullet_time > bullet_cooldown:
            mouse_pos = pygame.mouse.get_pos()
            direction = [mouse_pos[0] - player_pos[0], mouse_pos[1] - player_pos[1]]
            length = math.sqrt(direction[0] ** 2 + direction[1] ** 2)
            direction[0] /= length
            direction[1] /= length
            bullets.append({"pos": player_pos[:], "dir": direction})
            last_bullet_time = current_time

    # Update bullets
    for bullet in bullets[:]:
        bullet["pos"][0] += bullet["dir"][0] * bullet_speed
        bullet["pos"][1] += bullet["dir"][1] * bullet_speed

        # Remove off-screen bullets
        if not (0 <= bullet["pos"][0] <= WIDTH and 0 <= bullet["pos"][1] <= HEIGHT):
            bullets.remove(bullet)

    # Draw player
    pygame.draw.rect(screen, BLUE, (*player_pos, player_size, player_size))

    # Draw bullets
    for bullet in bullets:
        pygame.draw.circle(screen, GREEN, (int(bullet["pos"][0]), int(bullet["pos"][1])), 5)

    # Update enemies
    for enemy in enemies[:]:
        direction = [player_pos[0] - enemy["pos"][0], player_pos[1] - enemy["pos"][1]]
        length = math.sqrt(direction[0] ** 2 + direction[1] ** 2)
        direction[0] /= length
        direction[1] /= length
        enemy["pos"][0] += direction[0] * enemy_speed
        enemy["pos"][1] += direction[1] * enemy_speed

        # Check collision with player
        if check_collision(player_pos, player_size // 2, enemy["pos"], enemy_size):
            running = False

        # Check collision with bullets
        for bullet in bullets:
            if check_collision(bullet["pos"], 5, enemy["pos"], enemy_size):
                enemies.remove(enemy)
                bullets.remove(bullet)
                score += 1
                break

        # Draw enemy
        pygame.draw.circle(screen, RED, (int(enemy["pos"][0]), int(enemy["pos"][1])), enemy_size)

    # Check if wave is cleared
    if not enemies:
        wave += 1
        spawn_enemies(wave)

        # Every 5 waves, ask for an upgrade
        if wave % 5 == 0:
            handle_upgrade()

    # Display score and wave
    score_text = font.render(f"Score: {score}  Wave: {wave}", True, WHITE)
    screen.blit(score_text, (10, 10))

    # Update display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
