import numpy as np
import pygame
import sys

def value_iteration(grid_size, rewards, terminal_states, gamma=0.9, theta=1e-6):
    rows, cols = grid_size
    V = np.zeros(grid_size)
    living_reward = -1

    actions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    iteration = 0
    while True:
        iteration += 1
        delta = 0
        V_new = np.copy(V)

        # Iterate through each state in the grid
        for r in range(rows):
            for c in range(cols):
                state = (r, c)

                # If it's a terminal state, its value is set by the reward at that state
                if state in terminal_states:
                     pass

                # Value Iteration
                action_values = []
                # Calculate expected value
                for dr, dc in actions:
                    next_r, next_c = r + dr, c + dc

                    # Check if off grid
                    if not (0 <= next_r < rows and 0 <= next_c < cols):
                        next_r, next_c = r, c
                    next_state = (next_r, next_c)

                    immediate_reward = rewards.get(next_state, living_reward)

                    # Bellman equation component: R(s,a,s') + gamma * V(s')
                    # Assuming deterministic actions (P = 1)
                    q_value = immediate_reward + gamma * V[next_state]
                    action_values.append(q_value)

                # V(s) = max(sum of (R(s,a,s') + gamma * V(s'))) because P = 1
                if state not in terminal_states:
                    V_new[state] = max(action_values)
                else:
                     V_new[state] = rewards.get(state, 0)

                # Track the maximum change in value
                if state not in terminal_states:
                    delta = max(delta, abs(V_new[state] - V[state]))

        # Update the value function for the next iteration
        V = V_new

        # Check for convergence
        if delta < theta:
            print(f"Value iteration converged after {iteration} iterations (delta={delta:.2g} < {theta}).")
            break
        elif iteration > 2000: # Stops if not converging
             print(f"Value iteration stopped after {iteration} iterations (max reached).")
             break


    # Policy Extraction
    policy = np.zeros(grid_size, dtype=int)
    for r in range(rows):
        for c in range(cols):
            state = (r, c)

            if state in terminal_states:
                # No action needed if in terminal state
                policy[state] = -1
                continue

            action_values = []
            for dr, dc in actions:
                next_r, next_c = r + dr, c + dc

                # Check if off grid
                if not (0 <= next_r < rows and 0 <= next_c < cols):
                    next_r, next_c = r, c

                next_state = (next_r, next_c)
                immediate_reward = rewards.get(next_state, living_reward)
                q_value = immediate_reward + gamma * V[next_state]
                action_values.append(q_value)

            # Uses argmax instead of max to get optimal policy
            best_action_index = np.argmax(action_values)
            policy[state] = best_action_index

    return V, policy

# Pygame Visualization
def draw_grid(screen, policy, values, grid_size, cell_size, rewards, terminal_states):
    rows, cols = grid_size
    font = pygame.font.SysFont(None, 24)
    small_font = pygame.font.SysFont(None, 18)

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (200, 200, 200)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)

    for r in range(rows):
        for c in range(cols):
            rect = pygame.Rect(c * cell_size, r * cell_size, cell_size, cell_size)
            state = (r, c)

            bg_color = WHITE
            if state in terminal_states:
                if rewards.get(state, 0) > 0:
                    bg_color = GREEN
                else:
                    bg_color = RED 
            pygame.draw.rect(screen, bg_color, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)

            # Display the state value
            value_text = small_font.render(f"{values[state]:.1f}", True, BLACK)
            screen.blit(value_text, (rect.x + 5, rect.y + 5))

            # Draw policy arrow
            center_x = rect.centerx
            center_y = rect.centery
            arrow_len = cell_size * 0.3

            action = policy[state]
            if action == -1:
                term_text = font.render("T", True, BLACK)
                text_rect = term_text.get_rect(center=(center_x, center_y))
                screen.blit(term_text, text_rect)
            elif action == 0:
                pygame.draw.line(screen, BLUE, (center_x, center_y), (center_x, center_y - arrow_len), 3)
                pygame.draw.polygon(screen, BLUE, [(center_x, center_y - arrow_len - 5), (center_x - 5, center_y - arrow_len), (center_x + 5, center_y - arrow_len)]) # Arrowhead
            elif action == 1:
                pygame.draw.line(screen, BLUE, (center_x, center_y), (center_x, center_y + arrow_len), 3)
                pygame.draw.polygon(screen, BLUE, [(center_x, center_y + arrow_len + 5), (center_x - 5, center_y + arrow_len), (center_x + 5, center_y + arrow_len)]) # Arrowhead
            elif action == 2:
                pygame.draw.line(screen, BLUE, (center_x, center_y), (center_x - arrow_len, center_y), 3)
                pygame.draw.polygon(screen, BLUE, [(center_x - arrow_len - 5, center_y), (center_x - arrow_len, center_y - 5), (center_x - arrow_len, center_y + 5)]) # Arrowhead
            elif action == 3:
                pygame.draw.line(screen, BLUE, (center_x, center_y), (center_x + arrow_len, center_y), 3)
                pygame.draw.polygon(screen, BLUE, [(center_x + arrow_len + 5, center_y), (center_x + arrow_len, center_y - 5), (center_x + arrow_len, center_y + 5)]) # Arrowhead


# Gridworld
GRID_SIZE = (5, 5)
REWARDS = {
    (0, 0): 10,
    (0, 4): -10,
    (4, 4): -10,
    (4, 0): -10
}
TERMINAL_STATES = set(REWARDS.keys())
START_STATE = (2, 2)

# Running Value Iteration
print("Running Value Iteration...")
final_values, optimal_policy = value_iteration(
    grid_size=GRID_SIZE,
    rewards=REWARDS,
    terminal_states=TERMINAL_STATES,
    gamma=0.9,
    theta=1e-6
)

print("\nFinal Value Map (V):")
print(np.round(final_values, 2))

print("\nOptimal Policy Map (0: Up, 1: Down, 2: Left, 3: Right, -1: Terminal):")
policy_symbols = {0: '^', 1: 'v', 2: '<', 3: '>', -1: 'T'}
policy_display = np.full(GRID_SIZE, ' ', dtype=str)
for r in range(GRID_SIZE[0]):
    for c in range(GRID_SIZE[1]):
        policy_display[r, c] = policy_symbols[optimal_policy[r, c]]
print(policy_display)


pygame.init()

CELL_SIZE = 100
WIDTH = GRID_SIZE[1] * CELL_SIZE
HEIGHT = GRID_SIZE[0] * CELL_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gridworld Optimal Policy")

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((255, 255, 255))
    draw_grid(screen, optimal_policy, final_values, GRID_SIZE, CELL_SIZE, REWARDS, TERMINAL_STATES)

    pygame.display.flip()

pygame.quit()
sys.exit()