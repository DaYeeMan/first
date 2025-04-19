import numpy as np
import pygame
import sys # Needed for sys.exit

def value_iteration(grid_size, rewards, terminal_states, gamma=0.9, theta=1e-6):
    """
    Performs value iteration on a 2D gridworld.

    Args:
        grid_size (tuple): The dimensions of the grid (rows, cols).
        rewards (dict): A dictionary mapping grid coordinates (row, col) to rewards.
                        Default reward for non-specified states is the living penalty.
        terminal_states (set): A set of coordinates (row, col) representing terminal states.
        gamma (float): The discount factor (0 < gamma <= 1).
        theta (float): The convergence threshold. Iteration stops when the maximum
                       change in value across all states is less than theta.

    Returns:
        tuple: A tuple containing:
            - V (np.array): The converged value function for each state.
            - policy (np.array): The optimal policy (actions) for each state.
                                 Actions: 0: Up, 1: Down, 2: Left, 3: Right, -1: Terminal
    """
    rows, cols = grid_size
    # Initialize value function V(s) to zeros for all states s
    V = np.zeros(grid_size)
    # Define the living reward (penalty)
    living_reward = -1

    # Define possible actions (Up, Down, Left, Right)
    # Order: 0: Up (-1, 0), 1: Down (1, 0), 2: Left (0, -1), 3: Right (0, 1)
    actions = [(-1, 0), (1, 0), (0, -1), (0, 1)] # (d_row, d_col)

    iteration = 0
    while True:
        iteration += 1
        delta = 0  # Maximum change in value in this iteration
        V_new = np.copy(V) # Use a copy to store new values for synchronous update

        # Iterate through each state (cell) in the grid
        for r in range(rows):
            for c in range(cols):
                state = (r, c)

                # If it's a terminal state, its value is fixed by the reward received upon entering.
                # The value iteration process effectively calculates this.
                # No actions are possible *from* a terminal state in the MDP sense.
                if state in terminal_states:
                     # The value is determined by the reward received when entering.
                     # We calculate this reward within the loop for non-terminal states
                     # transitioning *to* terminal states.
                     # For simplicity, we can set V_new[state] = rewards.get(state, 0)
                     # but Bellman update naturally handles this for states *leading* to terminal.
                     # Let's keep calculating V for terminal states based on transitions *into* them.
                     # We will handle policy extraction separately.
                     pass # Value is updated based on transitions into it

                # --- Value Iteration Update (Bellman Update) ---
                action_values = []
                # Calculate the expected value for taking each action 'a' from state 's'
                for dr, dc in actions:
                    next_r, next_c = r + dr, c + dc

                    # Check grid boundaries - if action leads off-grid, stay in the same state
                    if not (0 <= next_r < rows and 0 <= next_c < cols):
                        next_r, next_c = r, c # Stay in place

                    next_state = (next_r, next_c)

                    # Get the immediate reward for transitioning to the next state
                    # This includes the living reward unless it's a special reward state
                    # Note: The reward is associated with *arriving* at next_state
                    immediate_reward = rewards.get(next_state, living_reward)

                    # Bellman equation component: R(s, a, s') + gamma * V(s')
                    # Assuming deterministic transitions: P(s'|s, a) = 1
                    # V[next_state] holds the value from the *previous* iteration
                    q_value = immediate_reward + gamma * V[next_state]
                    action_values.append(q_value)

                # Update the value of the current state to the maximum value achievable
                # V(s) = max_a [ Sum_{s'} P(s'|s,a) * (R(s,a,s') + gamma * V(s')) ]
                # Since P=1, V(s) = max_a [ R(s, a, s') + gamma * V(s') ]
                if state not in terminal_states: # Only update non-terminal states
                    V_new[state] = max(action_values)
                else:
                    # Keep terminal state values based on their reward (implicitly handled by transitions into them)
                    # Or explicitly set V_new[state] = rewards.get(state, 0) if preferred.
                    # Let's ensure terminal states have fixed values based on rewards dict
                     V_new[state] = rewards.get(state, 0)


                # Track the maximum change in value for convergence check (only for non-terminal states)
                if state not in terminal_states:
                    delta = max(delta, abs(V_new[state] - V[state]))

        # Update the value function for the next iteration
        V = V_new

        # Check for convergence
        if delta < theta:
            print(f"Value iteration converged after {iteration} iterations (delta={delta:.2g} < {theta}).")
            break
        elif iteration > 2000: # Safety break
             print(f"Value iteration stopped after {iteration} iterations (max reached).")
             break


    # --- Policy Extraction ---
    policy = np.zeros(grid_size, dtype=int) # Stores the index of the best action
    for r in range(rows):
        for c in range(cols):
            state = (r, c)

            if state in terminal_states:
                # No action needed from terminal states
                policy[state] = -1 # Special value for terminal
                continue

            action_values = []
            for dr, dc in actions:
                next_r, next_c = r + dr, c + dc

                # Boundary check
                if not (0 <= next_r < rows and 0 <= next_c < cols):
                    next_r, next_c = r, c # Stay in place

                next_state = (next_r, next_c)
                immediate_reward = rewards.get(next_state, living_reward)
                # Use the *converged* value function V for policy extraction
                q_value = immediate_reward + gamma * V[next_state]
                action_values.append(q_value)

            # Choose the action that maximizes the expected value
            # Handle potential ties (e.g., np.argmax might always pick the first max)
            # For simplicity, np.argmax is used here.
            best_action_index = np.argmax(action_values)
            policy[state] = best_action_index

    return V, policy

# --- Pygame Visualization Function (Requirement 3) ---
def draw_grid(screen, policy, values, grid_size, cell_size, rewards, terminal_states):
    """Draws the grid, values, and policy arrows on the Pygame screen."""
    rows, cols = grid_size
    font = pygame.font.SysFont(None, 24) # Default system font, size 24
    small_font = pygame.font.SysFont(None, 18) # Smaller font for values

    # Define colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (200, 200, 200)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255) # Color for arrows

    for r in range(rows):
        for c in range(cols):
            rect = pygame.Rect(c * cell_size, r * cell_size, cell_size, cell_size)
            state = (r, c)

            # Determine cell background color based on reward/terminal state
            bg_color = WHITE
            if state in terminal_states:
                if rewards.get(state, 0) > 0:
                    bg_color = GREEN # Goal state
                else:
                    bg_color = RED   # Penalty state
            pygame.draw.rect(screen, bg_color, rect) # Draw cell background
            pygame.draw.rect(screen, BLACK, rect, 1) # Draw cell border

            # Display the state value (optional, can clutter)
            value_text = small_font.render(f"{values[state]:.1f}", True, BLACK)
            screen.blit(value_text, (rect.x + 5, rect.y + 5))

            # Draw policy arrow or terminal indicator
            center_x = rect.centerx
            center_y = rect.centery
            arrow_len = cell_size * 0.3 # Length of the arrow line

            action = policy[state]
            if action == -1: # Terminal state
                term_text = font.render("T", True, BLACK)
                text_rect = term_text.get_rect(center=(center_x, center_y))
                screen.blit(term_text, text_rect)
            elif action == 0: # Up
                pygame.draw.line(screen, BLUE, (center_x, center_y), (center_x, center_y - arrow_len), 3)
                pygame.draw.polygon(screen, BLUE, [(center_x, center_y - arrow_len - 5), (center_x - 5, center_y - arrow_len), (center_x + 5, center_y - arrow_len)]) # Arrowhead
            elif action == 1: # Down
                pygame.draw.line(screen, BLUE, (center_x, center_y), (center_x, center_y + arrow_len), 3)
                pygame.draw.polygon(screen, BLUE, [(center_x, center_y + arrow_len + 5), (center_x - 5, center_y + arrow_len), (center_x + 5, center_y + arrow_len)]) # Arrowhead
            elif action == 2: # Left
                pygame.draw.line(screen, BLUE, (center_x, center_y), (center_x - arrow_len, center_y), 3)
                pygame.draw.polygon(screen, BLUE, [(center_x - arrow_len - 5, center_y), (center_x - arrow_len, center_y - 5), (center_x - arrow_len, center_y + 5)]) # Arrowhead
            elif action == 3: # Right
                pygame.draw.line(screen, BLUE, (center_x, center_y), (center_x + arrow_len, center_y), 3)
                pygame.draw.polygon(screen, BLUE, [(center_x + arrow_len + 5, center_y), (center_x + arrow_len, center_y - 5), (center_x + arrow_len, center_y + 5)]) # Arrowhead


# --- Gridworld Setup (Requirement 1) ---
GRID_SIZE = (5, 5)
REWARDS = {
    (0, 0): 10,   # Goal state
    (0, 4): -10,  # Penalty corner
    (4, 4): -10,  # Penalty corner
    (4, 0): -10   # Penalty corner
}
TERMINAL_STATES = set(REWARDS.keys()) # All reward states are terminal
START_STATE = (2, 2) # As per requirement 1 (though not used by value iteration itself)

# --- Run Value Iteration (Requirement 2) ---
print("Running Value Iteration...")
final_values, optimal_policy = value_iteration(
    grid_size=GRID_SIZE,
    rewards=REWARDS,
    terminal_states=TERMINAL_STATES,
    gamma=0.9,      # Discount factor
    theta=1e-6      # Convergence threshold
)

# --- Display Results in Console (Part of Requirement 4) ---
print("\nFinal Value Map (V):")
print(np.round(final_values, 2)) # Round for display

print("\nOptimal Policy Map (0: Up, 1: Down, 2: Left, 3: Right, -1: Terminal):")
# Map policy indices to arrows for better readability (optional)
policy_symbols = {0: '^', 1: 'v', 2: '<', 3: '>', -1: 'T'}
policy_display = np.full(GRID_SIZE, ' ', dtype=str) # Create a display grid
for r in range(GRID_SIZE[0]):
    for c in range(GRID_SIZE[1]):
        policy_display[r, c] = policy_symbols[optimal_policy[r, c]]
print(policy_display)


# --- Pygame Initialization and Main Loop (Requirement 3) ---
pygame.init()

# Screen dimensions
CELL_SIZE = 100 # Size of each grid cell in pixels
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

    # Drawing
    screen.fill((255, 255, 255)) # Fill background with white
    draw_grid(screen, optimal_policy, final_values, GRID_SIZE, CELL_SIZE, REWARDS, TERMINAL_STATES)

    # Update the display
    pygame.display.flip()

pygame.quit()
sys.exit() # Ensures the program exits cleanly

# --- Next Steps (Requirement 4) ---
# Write the report discussing implementation, challenges, and visualization.
# Include screenshots of the Pygame window and the final value/policy maps printed above.
