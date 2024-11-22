import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bullet Survivors")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Clock and FPS
clock = pygame.time.Clock()
FPS = 60

# Font settings
font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 72)

# Load images
bg_image = pygame.image.load("bg.png")  # Ensure background image exists
player_image = pygame.image.load("bgs.png")  # Replace with your player image
enemy_image = pygame.image.load("c.png")    # Replace with your enemy image

# Resize player and enemy images if needed
player_image = pygame.transform.scale(player_image, (50, 50))
enemy_image = pygame.transform.scale(enemy_image, (40, 40))

# Resize background to fit screen
bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))

# Player settings
player_pos = [WIDTH // 2, HEIGHT // 2]
player_size = 50
player_speed = 5
player_rotation = -90  # This controls the permanent rotation of the character
player_hitbox = 20  # Smaller hitbox for the player

# Bullet settings
bullet_speed = 10
bullets = []
bullet_cooldown = 300  # Milliseconds between bullets
last_bullet_time = 0

# Enemy settings
enemies = []
enemy_size = 40
enemy_speed = 2
enemy_hitbox = 15  # Smaller hitbox for enemies
wave = 1

# Score tracking
score = 0

# Special upgrades
special_upgrade_available = False
special_upgrades = {"piercing": False, "backward_shooting": False, "second_life": False}

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

# Function to handle special upgrades
def handle_special_upgrade():
    global special_upgrades, player_pos, enemies, bullets, wave

    upgrading = True
    upgrade_text = font.render(
        "1. Piercing Bullets 2. Backwards Shooting 3. Second Life",
        True,
        WHITE,
    )
    while upgrading:
        screen.fill(BLACK)
        screen.blit(upgrade_text, (WIDTH // 2 - 350, HEIGHT // 2 - 20))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    special_upgrades["piercing"] = True
                    upgrading = False
                elif event.key == pygame.K_2:
                    special_upgrades["backward_shooting"] = True
                    upgrading = False
                elif event.key == pygame.K_3:
                    special_upgrades["second_life"] = True
                    enemies = []  # Reset enemies
                    bullets = []  # Clear bullets
                    wave -= 1  # Replay current wave
                    spawn_enemies(wave)
                    player_pos = [WIDTH // 2, HEIGHT // 2]
                    upgrading = False

# Function for the start menu
def start_menu():
    menu_running = True
    title_text = big_font.render("Bullet Survivors", True, WHITE)
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

# Update bullet handling to support upgrades
last_backward_bullet_time = 0

def update_bullets():
    global last_backward_bullet_time

    # Move existing bullets
    for bullet in bullets[:]:
        bullet["pos"][0] += bullet["dir"][0] * bullet_speed
        bullet["pos"][1] += bullet["dir"][1] * bullet_speed

        # Remove off-screen bullets
        if not (0 <= bullet["pos"][0] <= WIDTH and 0 <= bullet["pos"][1] <= HEIGHT):
            bullets.remove(bullet)

    # Create backward-shooting bullets
    if special_upgrades["backward_shooting"] and pygame.mouse.get_pressed()[0]:
        current_time = pygame.time.get_ticks()
        if current_time - last_backward_bullet_time > bullet_cooldown:
            mouse_pos = pygame.mouse.get_pos()
            direction = [mouse_pos[0] - player_pos[0], mouse_pos[1] - player_pos[1]]
            length = math.sqrt(direction[0] ** 2 + direction[1] ** 2)
            direction[0] /= length
            direction[1] /= length
            bullets.append(
                {"pos": player_pos[:], "dir": [-direction[0], -direction[1]]}
            )
            last_backward_bullet_time = current_time

# Update enemy handling to support upgrades
def update_enemies():
    global score, player_pos, enemies

    for enemy in enemies[:]:
        direction = [player_pos[0] - enemy["pos"][0], player_pos[1] - enemy["pos"][1]]
        length = math.sqrt(direction[0] ** 2 + direction[1] ** 2)
        direction[0] /= length
        direction[1] /= length
        enemy["pos"][0] += direction[0] * enemy_speed
        enemy["pos"][1] += direction[1] * enemy_speed

        # Check collision with player
        if check_collision(player_pos, player_hitbox, enemy["pos"], enemy_hitbox):
            if special_upgrades["second_life"]:
                # Reset wave
                special_upgrades["second_life"] = False
                enemies.clear()  # Clear all current enemies
                spawn_enemies(wave)  # Restart the current wave
                player_pos = [WIDTH // 2, HEIGHT // 2]  # Reset player position
                return
            pygame.quit()
            exit()

        # Check collision with bullets
        for bullet in bullets[:]:
            if check_collision(bullet["pos"], 5, enemy["pos"], enemy_hitbox):
                if not special_upgrades["piercing"]:
                    bullets.remove(bullet)
                enemies.remove(enemy)
                score += 1
                break

        # Draw enemy
        screen.blit(enemy_image, (int(enemy["pos"][0]) - enemy_size // 2, int(enemy["pos"][1]) - enemy_size // 2))

# Main game loop
start_menu()
running = True
spawn_enemies(wave)

while running:
    screen.fill(BLACK)

    # Draw background image (fills the entire screen)
    screen.blit(bg_image, (0, 0))

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

    # Update bullets and enemies
    update_bullets()
    update_enemies()

    # Handle player rotation
    mouse_pos = pygame.mouse.get_pos()
    angle = math.atan2(mouse_pos[1] - player_pos[1], mouse_pos[0] - player_pos[0])
    player_rotated = pygame.transform.rotate(player_image, -math.degrees(angle) + player_rotation)  # Correct the rotation direction
    player_rect = player_rotated.get_rect(center=(player_pos[0], player_pos[1]))

    # Draw rotated player
    screen.blit(player_rotated, player_rect.topleft)

    for bullet in bullets:
            pygame.draw.circle(screen, BLACK, (int(bullet["pos"][0]), int(bullet["pos"][1])), 5)
    # Check if wave is cleared
    if not enemies:
        wave += 1
        if wave > 20:
            # Victory screen
            screen.fill(BLACK)
            victory_text = big_font.render("You Win!", True, WHITE)
            screen.blit(victory_text, (WIDTH // 2 - 150, HEIGHT // 2))
            pygame.display.flip()
            pygame.time.wait(3000)
            running = False
        else:
            spawn_enemies(wave)
            if wave % 10 == 0:
                handle_special_upgrade()
            elif wave % 5 == 0:
                handle_upgrade()

    # Display score and wave
    score_text = font.render(f"Score: {score}  Wave: {wave}", True, WHITE)
    screen.blit(score_text, (10, 10))

    # Update display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
