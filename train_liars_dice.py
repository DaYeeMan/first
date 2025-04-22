from liars_dice_env import LiarsDiceEnv
from q_learning_agent import QLearningAgent
import numpy as np
import pickle
from typing import Dict, Tuple

def analyze_policy(policy: Dict[str, Tuple[str, Tuple[int, int]]]) -> None:
    """Analyze and print insights about the learned policy."""
    print("\nPolicy Analysis:")
    
    # Count different types of actions
    action_counts = {'bet': 0, 'liar': 0, 'spot_on': 0}
    for state_key, action in policy.items():
        if action is not None:
            action_type, _ = action
            action_counts[action_type] += 1
    
    print(f"Action distribution: {action_counts}")
    
    # Analyze betting patterns
    bet_counts = {}
    for state_key, action in policy.items():
        if action is not None and action[0] == 'bet':
            count, value = action[1]
            key = f"{count} {value}s"
            bet_counts[key] = bet_counts.get(key, 0) + 1
    
    print("\nMost common bets:")
    for bet, count in sorted(bet_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"{bet}: {count} times")

def main():
    # Create environment and agent
    env = LiarsDiceEnv()
    agent = QLearningAgent(env)
    
    # Train the agent
    print("Training the agent...")
    agent.train(num_episodes=100000)
    
    # Get and analyze the policy
    policy = agent.get_policy()
    analyze_policy(policy)
    
    # Save the policy
    with open('liars_dice_policy.pkl', 'wb') as f:
        pickle.dump(policy, f)
    print("\nPolicy saved to 'liars_dice_policy.pkl'")

if __name__ == "__main__":
    main() 