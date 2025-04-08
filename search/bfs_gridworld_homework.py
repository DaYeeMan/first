import pygame
import sys
from collections import deque

# Constants
GRID_SIZE = 20
GRID_WIDTH = 20
GRID_HEIGHT = 20
WINDOW_WIDTH = GRID_SIZE * GRID_WIDTH
WINDOW_HEIGHT = GRID_SIZE * GRID_HEIGHT + 50  # Extra space for buttons
FPS = 10

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Gridworld Environment')
clock = pygame.time.Clock()

# Initialize grid with empty cells
grid = [[WHITE for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

# Specify start and goal positions
start = (5, 5)
goal = (15, 15)
grid[start[1]][start[0]] = RED
grid[goal[1]][goal[0]] = GREEN

# Buttons
start_button = pygame.Rect(10, WINDOW_HEIGHT - 40, 80, 30)
stop_button = pygame.Rect(100, WINDOW_HEIGHT - 40, 80, 30)
reset_button = pygame.Rect(190, WINDOW_HEIGHT - 40, 80, 30)
algorithm_running = False
bfs_queue = None
visited = None

# Function to draw the grid
def draw_grid():
    for x in range(0, WINDOW_WIDTH, GRID_SIZE):
        pygame.draw.line(screen, GRAY, (x, 0), (x, GRID_HEIGHT * GRID_SIZE))
    for y in range(0, GRID_HEIGHT * GRID_SIZE, GRID_SIZE):
        pygame.draw.line(screen, GRAY, (0, y), (WINDOW_WIDTH, y))

# Function to update a cell in the grid
def update_cell(x, y, color):
    pygame.draw.rect(screen, color, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

# Function to draw buttons
def draw_buttons():
    pygame.draw.rect(screen, WHITE, start_button)
    pygame.draw.rect(screen, WHITE, stop_button)
    pygame.draw.rect(screen, WHITE, reset_button)
    pygame.draw.rect(screen, BLACK, start_button, 2)
    pygame.draw.rect(screen, BLACK, stop_button, 2)
    pygame.draw.rect(screen, BLACK, reset_button, 2)
    font = pygame.font.SysFont(None, 24)
    start_text = font.render('Start', True, BLACK)
    stop_text = font.render('Stop', True, BLACK)
    reset_text = font.render('Reset', True, BLACK)
    screen.blit(start_text, (start_button.x + 10, start_button.y + 5))
    screen.blit(stop_text, (stop_button.x + 10, stop_button.y + 5))
    screen.blit(reset_text, (reset_button.x + 10, reset_button.y + 5))

# Function to handle mouse clicks
def handle_click(pos):
    global algorithm_running
    if start_button.collidepoint(pos):
        algorithm_running = True
        start_bfs(start, goal)
    elif stop_button.collidepoint(pos):
        algorithm_running = False
    elif reset_button.collidepoint(pos):
        reset_grid()

# Function to reset the grid
def reset_grid():
    global grid, algorithm_running, bfs_queue, visited
    grid = [[WHITE for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    grid[start[1]][start[0]] = RED
    grid[goal[1]][goal[0]] = GREEN
    algorithm_running = False
    bfs_queue = None
    visited = set()

# Function to start BFS
def start_bfs(start, goal):
    global bfs_queue, visited
    bfs_queue = deque([(start, [])])
    visited = set()
    visited.add(start)

# Function to run a single step of BFS
def bfs_step():
    if bfs_queue:
        # TODO Define a current node by popping from the queue
        current_node = deque(bfs_queue)
        visited.add(current_node)
        # Get neighbors of the current node
        for neighbor in get_neighbors(current_node):
            # TODO Manage the queue
                bfs_queue.append(neighbor)
                # Update the grid for visualization (don't edit)
                if neighbor != start and neighbor != goal:
                    grid[neighbor[1]][neighbor[0]] = YELLOW
    return False

# Function to get neighbors of a node
def get_neighbors(node):
    neighbors = []
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for dx, dy in directions:
        new_node = (node[0] + dx, node[1] + dy)
        if 0 <= new_node[0] < GRID_WIDTH and 0 <= new_node[1] < GRID_HEIGHT:
            neighbors.append(new_node)
    return neighbors

# Main loop
def main():
    global algorithm_running
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                handle_click(pygame.mouse.get_pos())

        screen.fill(WHITE)
        draw_grid()

        # Update the grid cells
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                update_cell(x, y, grid[y][x])

        # Draw buttons
        draw_buttons()

        # If algorithm is running, perform BFS step
        if algorithm_running:
            finished = bfs_step()
            if finished:
                algorithm_running = False

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == '__main__':
    main()
