import numpy as np
from typing import Dict, Tuple, List
import random
from liars_dice_env import LiarsDiceEnv

class QLearningAgent:
    def __init__(self, env: LiarsDiceEnv, learning_rate=0.1, discount_factor=0.9, 
                 exploration_rate=1.0, exploration_decay=0.995, min_exploration=0.01):
        self.env = env
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_decay = exploration_decay
        self.min_exploration = min_exploration
        self.q_table = {}
        
    def get_state_key(self, state: Dict) -> str:
        """Convert state to a string key for Q-table."""
        return f"{state['current_player']}_{state['current_bet']}_{tuple(state['player1_dice'])}_{tuple(state['player2_dice'])}"
    
    def get_q_value(self, state: Dict, action: Tuple[str, Tuple[int, int]]) -> float:
        """Get Q-value for state-action pair."""
        state_key = self.get_state_key(state)
        action_key = str(action)
        return self.q_table.get((state_key, action_key), 0.0)
    
    def update_q_value(self, state: Dict, action: Tuple[str, Tuple[int, int]], 
                      reward: float, next_state: Dict) -> None:
        """Update Q-value using Q-learning update rule."""
        state_key = self.get_state_key(state)
        action_key = str(action)
        next_state_key = self.get_state_key(next_state)
        
        # Get current Q-value
        current_q = self.q_table.get((state_key, action_key), 0.0)
        
        # Get max Q-value for next state
        next_actions = self.env.get_legal_actions()
        if next_actions:
            max_next_q = max(self.get_q_value(next_state, a) for a in next_actions)
        else:
            max_next_q = 0.0
        
        # Update Q-value
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * max_next_q - current_q
        )
        self.q_table[(state_key, action_key)] = new_q
    
    def choose_action(self, state: Dict) -> Tuple[str, Tuple[int, int]]:
        """Choose action using epsilon-greedy policy."""
        legal_actions = self.env.get_legal_actions()
        
        if random.random() < self.exploration_rate:
            return random.choice(legal_actions)
        
        # Choose best action based on Q-values
        best_action = None
        best_q = float('-inf')
        
        for action in legal_actions:
            q_value = self.get_q_value(state, action)
            if q_value > best_q:
                best_q = q_value
                best_action = action
        
        return best_action
    
    def train(self, num_episodes: int) -> None:
        """Train the agent for specified number of episodes."""
        for episode in range(num_episodes):
            state = self.env.reset()
            done = False
            total_reward = 0
            
            while not done:
                # Choose and execute action
                action = self.choose_action(state)
                next_state, reward, done, _ = self.env.step(action)
                
                # Update Q-value
                self.update_q_value(state, action, reward, next_state)
                
                state = next_state
                total_reward += reward
            
            # Decay exploration rate
            self.exploration_rate = max(self.min_exploration, 
                                      self.exploration_rate * self.exploration_decay)
            
            if (episode + 1) % 1000 == 0:
                print(f"Episode {episode + 1}, Total Reward: {total_reward}, "
                      f"Exploration Rate: {self.exploration_rate:.3f}")
    
    def get_policy(self) -> Dict[str, Tuple[str, Tuple[int, int]]]:
        """Extract the learned policy."""
        policy = {}
        for (state_key, _), q_value in self.q_table.items():
            if state_key not in policy:
                policy[state_key] = None
                best_q = float('-inf')
                
                # Find best action for this state
                for action in self.env.get_legal_actions():
                    current_q = self.get_q_value(eval(state_key), action)
                    if current_q > best_q:
                        best_q = current_q
                        policy[state_key] = action
        
        return policy 