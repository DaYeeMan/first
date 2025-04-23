"""
Q-Learning Agent for Liar's Dice

This agent learns to play Liar's Dice using Q-learning, a model-free reinforcement
learning algorithm. The agent learns by playing against itself and updating its
Q-values based on the rewards it receives.

Strategy Overview:
-----------------
1. State Representation:
   - Includes both players' dice counts
   - Current bet information
   - Expected values and probabilities
   - Game progress features

2. Action Selection:
   - Uses epsilon-greedy strategy with decay
   - Enhanced heuristics for Liar and Spot On calls
   - Balances exploration and exploitation

3. Learning Process:
   - Updates Q-values based on rewards and next state values
   - Uses additional rewards for good strategic decisions
   - Tracks betting patterns and bluffing behavior

4. Bluffing Strategy:
   - Learns to make occasional high bets (bluffs)
   - Distinguishes between true bluffs and semi-bluffs
   - Adapts bluffing frequency based on success
"""

import numpy as np
from typing import Tuple, List, Dict
import random
from liars_dice_env import LiarsDiceEnv
from collections import defaultdict

class QLearningAgent:
    def __init__(self, env: LiarsDiceEnv, learning_rate=0.05, discount_factor=0.95, 
                 exploration_rate=1.0, exploration_decay=0.999, min_exploration=0.01):
        """
        Initialize the Q-learning agent.
        
        Args:
            env: The Liar's Dice environment
            learning_rate: How quickly the agent updates its Q-values (α)
            discount_factor: How much future rewards are valued (γ)
            exploration_rate: Initial probability of random action (ε)
            exploration_decay: Rate at which exploration probability decreases
            min_exploration: Minimum exploration probability
        """
        self.env = env
        self.learning_rate = learning_rate  # Smaller for more stable learning
        self.discount_factor = discount_factor  # Higher to value future rewards more
        self.exploration_rate = exploration_rate
        self.exploration_decay = exploration_decay  # Slower decay for more exploration
        self.min_exploration = min_exploration
        self.q_table = defaultdict(float)
        
    def get_state_key(self, state: np.ndarray) -> tuple:
        """
        Convert state to a tuple key for Q-table.
        
        Discretizes continuous features (like expected values and deviations)
        into 5 bins for better generalization. This helps the agent learn
        similar strategies for similar situations.
        
        Args:
            state: The current state array
        
        Returns:
            Tuple that can be used as a dictionary key
        """
        discretized_state = []
        for i, value in enumerate(state):
            if i in [14, 15, 16, 17]:  # Continuous features
                # Discretize into 5 bins
                discretized_state.append(int(value * 5))
            else:
                discretized_state.append(int(value))
        return tuple(discretized_state)
    
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
        """
        Choose action using epsilon-greedy policy with enhanced heuristics.
        
        Strategy:
        1. Random Action: With probability ε, choose random action
        2. Heuristic Actions:
           - Call Liar on significantly high bets
           - Call Spot On on bets close to expected value
        3. Q-Value Based: Otherwise choose action with highest Q-value
        
        Args:
            state: Current game state
        
        Returns:
            Chosen action in format (action_type, (count, value))
        """
        legal_actions = self.env.get_legal_actions()
        
        if random.random() < self.exploration_rate:
            return random.choice(legal_actions)
        
        # Calculate expected value for current bet if it exists
        if self.env.current_bet is not None:
            current_count, current_value = self.env.current_bet
            
            # Get expected value from state features
            if current_value == 1:
                expected_value = state[20]  # Expected ones
            else:
                expected_value = state[19 + current_value]  # Expected value + wild ones
            
            # Enhanced heuristic for calling liar
            if current_count > expected_value + 2:  # Significantly above expected
                # Check if liar is a legal action
                liar_action = ('liar', None)
                if liar_action in legal_actions:
                    # Higher probability of calling liar for more unreasonable bets
                    probability = min(0.9, (current_count - expected_value) / 5)
                    if random.random() < probability:
                        return liar_action
            
            # Enhanced heuristic for calling spot on
            if abs(current_count - expected_value) <= 1:  # Close to expected
                spot_on_action = ('spot_on', self.env.current_bet)
                if spot_on_action in legal_actions:
                    probability = 0.3  # Moderate probability for reasonable bets
                    if random.random() < probability:
                        return spot_on_action
        
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
        """
        Analyze betting patterns and track bluffing behavior.
        
        Tracks:
        - Distribution of bet values and sizes
        - True bluffs (betting high on non-wild values)
        - Semi-bluffs (betting high on ones)
        
        Improved bluff detection considers:
        1. Agent's actual dice count for the bet value
        2. Expected value from remaining dice
        3. Whether the bet is significantly above possible
        
        Args:
            state: Current game state
            action: Chosen action
            stats: Dictionary to store statistics
        """
        action_type, bet_info = action
        
        if action_type == 'bet':
            count, value = bet_info
            stats['bet_values'][value] += 1
            stats['bet_sizes'][count] += 1
            
            # Get agent's actual dice count for this value
            if self.env.current_player == 0:
                agent_dice_count = state[value-2] if value > 1 else state[10]  # Player 1's dice
            else:
                agent_dice_count = state[value+3] if value > 1 else state[11]  # Player 2's dice
            
            # Calculate maximum possible count from remaining dice
            remaining_dice = 10 - (state[10] + state[11])  # Total dice minus ones
            if value == 1:
                max_possible = agent_dice_count + remaining_dice  # All remaining dice could be ones
            else:
                max_possible = agent_dice_count + remaining_dice  # All remaining dice could be this value
            
            # Enhanced bluff detection
            if count > max_possible:
                # Definitely a bluff - betting more than possible
                if value == 1:
                    stats['semi_bluffs'][value] += 1
                else:
                    stats['bluffs'][value] += 1
            elif count > agent_dice_count + 2:
                # Likely a bluff - betting significantly more than what agent has
                if value == 1:
                    stats['semi_bluffs'][value] += 1
                else:
                    stats['bluffs'][value] += 1
            elif count > agent_dice_count and count > max_possible * 0.8:
                # Potential bluff - betting close to maximum possible
                if value == 1:
                    stats['semi_bluffs'][value] += 1
                else:
                    stats['bluffs'][value] += 1
    
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

    def save_compressed_q_table(self, filename: str) -> None:
        """Save a compressed version of the Q-table that maintains agent behavior."""
        import gzip
        import pickle
        import numpy as np
        
        # Convert defaultdict to regular dict for serialization
        q_dict = dict(self.q_table)
        
        # Convert state tuples to numpy arrays for better compression
        compressed_q = {}
        for (state, action), value in q_dict.items():
            # Convert state tuple to numpy array if it's not already
            if isinstance(state, tuple):
                state = np.array(state, dtype=np.int8)  # Use int8 to save space
            compressed_q[(state.tobytes(), action)] = value
        
        # Save with highest protocol and compression
        with gzip.open(filename, 'wb', compresslevel=9) as f:
            pickle.dump(compressed_q, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    def load_compressed_q_table(self, filename: str) -> None:
        """Load a compressed Q-table."""
        import gzip
        import pickle
        import numpy as np
        
        with gzip.open(filename, 'rb') as f:
            compressed_q = pickle.load(f)
        
        # Convert back to original format
        self.q_table = defaultdict(float)
        for (state_bytes, action), value in compressed_q.items():
            state = np.frombuffer(state_bytes, dtype=np.int8)
            self.q_table[(tuple(state), action)] = value 