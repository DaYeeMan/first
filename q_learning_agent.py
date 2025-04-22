import numpy as np
from typing import Tuple, List, Dict
import random
from liars_dice_env import LiarsDiceEnv
from collections import defaultdict

class QLearningAgent:
    def __init__(self, env: LiarsDiceEnv, learning_rate=0.1, discount_factor=0.9, 
                 exploration_rate=1.0, exploration_decay=0.995, min_exploration=0.01):
        self.env = env
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_decay = exploration_decay
        self.min_exploration = min_exploration
        self.q_table = defaultdict(float)
        
    def get_state_key(self, state: np.ndarray) -> tuple:
        """Convert state to a tuple key for Q-table."""
        return tuple(state)
    
    def get_q_value(self, state: np.ndarray, action: Tuple[str, Tuple[int, int]]) -> float:
        """Get Q-value for state-action pair."""
        state_key = self.get_state_key(state)
        action_key = str(action)
        return self.q_table[(state_key, action_key)]
    
    def update_q_value(self, state: np.ndarray, action: Tuple[str, Tuple[int, int]], 
                      reward: float, next_state: np.ndarray) -> None:
        """Update Q-value using Q-learning update rule."""
        state_key = self.get_state_key(state)
        action_key = str(action)
        next_state_key = self.get_state_key(next_state)
        
        # Get current Q-value
        current_q = self.q_table[(state_key, action_key)]
        
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
    
    def choose_action(self, state: np.ndarray) -> Tuple[str, Tuple[int, int]]:
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
    
    def analyze_betting_patterns(self, state: np.ndarray, action: Tuple[str, Tuple[int, int]], 
                               stats: Dict) -> None:
        """Analyze betting patterns and bluffing behavior."""
        if action[0] == 'bet':
            count, value = action[1]
            player_dice = state[:5]  # Player 1's dice counts (2-6)
            player_ones = state[10]  # Player 1's ones
            
            # Track bet value distribution
            stats['bet_values'][value] += 1
            
            # Track bet sizes
            stats['bet_sizes'][count] += 1
            
            # Analyze bluffing
            if value > 1:  # Don't count ones as they're wild
                actual_count = player_dice[value-2]  # value-2 because array is 0-based for values 2-6
                if actual_count == 0 and player_ones == 0:  # True bluff
                    stats['bluffs'][value] += 1
                elif actual_count == 0 and player_ones > 0:  # Semi-bluff with ones
                    stats['semi_bluffs'][value] += 1
    
    def train(self, num_episodes: int) -> None:
        """Train the agent for specified number of episodes."""
        stats = {
            'action_counts': {'bet': 0, 'liar': 0, 'spot_on': 0},
            'bet_values': defaultdict(int),
            'bet_sizes': defaultdict(int),
            'bluffs': defaultdict(int),
            'semi_bluffs': defaultdict(int),
            'liar_calls': defaultdict(int),  # Track when liar is called
            'spot_on_calls': defaultdict(int)  # Track when spot_on is called
        }
        
        for episode in range(num_episodes):
            self.env.reset()
            state = self.env.get_state()
            done = False
            total_reward = 0
            round_number = 0
            
            while not done:
                round_number += 1
                # Choose and execute action
                action = self.choose_action(state)
                action_type, _ = action
                stats['action_counts'][action_type] += 1
                
                # Analyze betting patterns
                self.analyze_betting_patterns(state, action, stats)
                
                # Track when special actions are called
                if action_type == 'liar':
                    stats['liar_calls'][round_number] += 1
                elif action_type == 'spot_on':
                    stats['spot_on_calls'][round_number] += 1
                
                next_state, reward, done, _ = self.env.step(action)
                
                # Update Q-value
                self.update_q_value(state, action, reward, next_state)
                
                state = next_state
                total_reward += reward
            
            # Decay exploration rate
            self.exploration_rate = max(self.min_exploration, 
                                      self.exploration_rate * self.exploration_decay)
            
            if (episode + 1) % 1000 == 0:
                print(f"\nEpisode {episode + 1}, Total Reward: {total_reward}, "
                      f"Exploration Rate: {self.exploration_rate:.3f}")
                print("\nAction Distribution:")
                print(f"Total actions: {sum(stats['action_counts'].values())}")
                for action, count in stats['action_counts'].items():
                    print(f"{action}: {count} ({count/sum(stats['action_counts'].values())*100:.1f}%)")
                
                print("\nBet Value Distribution:")
                total_bets = sum(stats['bet_values'].values())
                for value, count in sorted(stats['bet_values'].items()):
                    print(f"Value {value}: {count} ({count/total_bets*100:.1f}%)")
                
                print("\nBet Size Distribution:")
                for size, count in sorted(stats['bet_sizes'].items()):
                    print(f"Size {size}: {count}")
                
                print("\nBluffing Analysis:")
                total_bluffs = sum(stats['bluffs'].values()) + sum(stats['semi_bluffs'].values())
                if total_bluffs > 0:
                    print("True Bluffs:")
                    for value, count in sorted(stats['bluffs'].items()):
                        print(f"Value {value}: {count} ({count/total_bluffs*100:.1f}%)")
                    print("\nSemi-Bluffs (using ones):")
                    for value, count in sorted(stats['semi_bluffs'].items()):
                        print(f"Value {value}: {count} ({count/total_bluffs*100:.1f}%)")
                
                print("\nSpecial Action Timing:")
                print("Liar calls by round:")
                for round_num, count in sorted(stats['liar_calls'].items()):
                    print(f"Round {round_num}: {count}")
                print("\nSpot-on calls by round:")
                for round_num, count in sorted(stats['spot_on_calls'].items()):
                    print(f"Round {round_num}: {count}")
                
                # Reset stats for next interval
                stats = {
                    'action_counts': {'bet': 0, 'liar': 0, 'spot_on': 0},
                    'bet_values': defaultdict(int),
                    'bet_sizes': defaultdict(int),
                    'bluffs': defaultdict(int),
                    'semi_bluffs': defaultdict(int),
                    'liar_calls': defaultdict(int),
                    'spot_on_calls': defaultdict(int)
                }
    
    def get_policy(self) -> Dict[tuple, Tuple[str, Tuple[int, int]]]:
        """Extract the learned policy."""
        policy = {}
        unique_states = set(state_key for state_key, _ in self.q_table.keys())
        
        for state_key in unique_states:
            state = np.array(state_key)
            best_action = None
            best_q = float('-inf')
            
            # Find best action for this state
            for action in self.env.get_legal_actions():
                current_q = self.get_q_value(state, action)
                if current_q > best_q:
                    best_q = current_q
                    best_action = action
            
            if best_action is not None:
                policy[state_key] = best_action
        
        return policy 