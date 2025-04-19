import numpy as np

gamma = 0.9
states = ['A', 'B', 'C', 'D', 'E']
rewards = {'A': 10, 'B': -1, 'C': -1, 'D': -1, 'E': -10}

# V(E) can only go left

def bellman_system():
    # V(A) = 10
    # We need to solve for V(B), V(C), V(D), and V(E)

    # Solving for unknowns V(B, C, D, and E)
    # V(B) = max(left: V(A), right: V(C)) or max(10 + 0.9*V(A), -1 + 0.9*V(C))
    # V(C) = max(left: V(B), right: V(D)) or max(-1 + 0.9*V(B), -1 + 0.9*V(D))
    # V(D) = max(left: V(C), right: V(E)) or max(-1 + 0.9*V(C), -10 + 0.9*V(E))
    # V(E) = left: V(D) or -10 + 0.9 * V(D) since right isn't an option
    A = np.array([
        [1, -gamma, 0, 0],
        [-gamma, 1, -gamma, 0],
        [0, -gamma, 1, -gamma],
        [0, 0, -gamma, 1]
    ])

    b = np.array([
        max(10 + gamma * 0, -1 + gamma * 0), # V(B)
        -1, # V(C)
        -1, # V(D)
        -10 + gamma * 0 # V(E)
    ])

    # Using linear algebra to solve the system
    V_unknown = np.linalg.solve(A, b)
    V = [10, V_unknown[0], V_unknown[1], V_unknown[2], V_unknown[3]]
    return dict(zip(states, V))

# - is used because you dont want the game to run forever
def get_policy(V):
    policy = {}
    for s in states:
        if s == 'A':
            policy[s] = '-'
        elif s == 'B':
            left = 10 + gamma * V['A']
            right = -1 + gamma * V['C']
            policy[s] = 'L' if left > right else 'R'
        elif s == 'C':
            left = -1 + gamma * V['B']
            right = -1 + gamma * V['D']
            policy[s] = 'L' if left > right else 'R'
        elif s == 'D':
            left = -1 + gamma * V['C']
            right = -10 + gamma * V['E']
            policy[s] = 'L' if left > right else 'R'
        elif s == 'E':
            left = -10 + gamma * V['D']
            policy[s] = 'L'
    return policy

# Numerical Solution
def value_iteration(gamma=0.9, theta=1e-6):
    V = {s: 0 for s in states}
    V['A'] = 10
    # V['E'] = -10
    
    # Calculate expected return when taking action a from state s
    def step(s, a):
        if s == 'A':
            return V[s]
        if a == 'L':
            s_next = states[max(0, states.index(s) - 1)]
        elif a == 'R':
            if s == 'E':  # You can't move right from E
                return -100
            s_next = states[min(len(states) - 1, states.index(s) + 1)]
        return rewards[s] + gamma * V[s_next]

    # Keep iteratively updating the policy based on the expected reward for each move
    while True:
        delta = 0
        for s in states:
            if s in ['A']:
                continue
            v = V[s]
            if s != 'E':
                V[s] = max(step(s, 'L'), step(s, 'R'))
            else:
                V[s] = step(s, 'L')
            delta = max(delta, abs(v - V[s]))
        if delta < theta:
            break
    return V

def extract_policy(V):
    policy = {}
    for s in states:
        if s == 'A':
            policy[s] = '-'
        elif s != 'E':
            left = rewards[s] + gamma * V[states[max(0, states.index(s) - 1)]]
            right = rewards[s] + gamma * V[states[min(len(states) - 1, states.index(s) + 1)]]
            policy[s] = 'L' if left > right else 'R'
        else:
            policy[s] = 'L'
    return policy

if __name__ == '__main__':
    print("Analytical Solution:")
    V_analytical = bellman_system()
    for s in states:
        print(f"V({s}) = {V_analytical[s]:.4f}")

    policy_analytical = get_policy(V_analytical)
    print("\nOptimal Policy (Analytical):")
    for s in states:
        print(f"π({s}) = {policy_analytical[s]}")

    print("\nNumerical Solution (Value Iteration):")
    V_numerical = value_iteration()
    for s in states:
        print(f"V({s}) = {V_numerical[s]:.4f}")

    policy_numerical = extract_policy(V_numerical)
    print("\nOptimal Policy (Numerical):")
    for s in states:
        print(f"π({s}) = {policy_numerical[s]}")