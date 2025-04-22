import numpy as np
from typing import Tuple, List, Dict
import random

class LiarsDiceEnv:
    def __init__(self):
        self.num_dice = 5
        self.dice_values = 6
        self.reset()
        
    def reset(self) -> None:
        """Reset the game state."""
        self.player1_dice = np.random.randint(1, 7, self.num_dice)
        self.player2_dice = np.random.randint(1, 7, self.num_dice)
        self.current_bet = None
        self.current_player = 0  # 0 for player 1, 1 for player 2
        
    def get_state(self) -> np.ndarray:
        """Return the current game state as a numpy array."""
        # Create a compact state representation
        state = np.zeros(13, dtype=np.int32)  # 5 + 5 + 1 + 1 + 1
        
        # Player 1's dice counts (excluding 1s)
        for i in range(2, 7):
            state[i-2] = np.sum(self.player1_dice == i)
        
        # Player 2's dice counts (excluding 1s)
        for i in range(2, 7):
            state[i+3] = np.sum(self.player2_dice == i)
        
        # Number of 1s for each player
        state[10] = np.sum(self.player1_dice == 1)
        state[11] = np.sum(self.player2_dice == 1)
        
        # Current bet information
        if self.current_bet is not None:
            count, value = self.current_bet
            state[12] = count * 10 + value  # Encode bet as a single number
        else:
            state[12] = 0
        
        return state
    
    def count_dice(self, value: int) -> int:
        """Count total number of dice showing a specific value (including 1s)."""
        total = np.sum(self.player1_dice == value) + np.sum(self.player2_dice == value)
        total += np.sum(self.player1_dice == 1) + np.sum(self.player2_dice == 1)
        return total
    
    def is_valid_bet(self, bet: Tuple[int, int]) -> bool:
        """Check if a bet is valid given the current bet."""
        if self.current_bet is None:
            return bet[0] >= 1 and 1 <= bet[1] <= 6
        
        current_count, current_value = self.current_bet
        new_count, new_value = bet
        
        # Bet must be higher in either count or value
        if new_count > current_count:
            return True
        if new_count == current_count and new_value > current_value:
            return True
        return False
    
    def step(self, action: Tuple[str, Tuple[int, int]]) -> Tuple[np.ndarray, float, bool, Dict]:
        """
        Execute an action and return (next_state, reward, done, info)
        Action can be:
        - ('bet', (count, value))
        - ('liar', None)
        - ('spot_on', (count, value))
        """
        action_type, bet = action
        done = False
        reward = 0
        info = {}
        
        if action_type == 'bet':
            if not self.is_valid_bet(bet):
                reward = -1
                done = True
            else:
                self.current_bet = bet
                self.current_player = 1 - self.current_player
        
        elif action_type == 'liar':
            actual_count = self.count_dice(self.current_bet[1])
            if actual_count < self.current_bet[0]:
                reward = 1 if self.current_player == 0 else -1
            else:
                reward = -1 if self.current_player == 0 else 1
            done = True
        
        elif action_type == 'spot_on':
            actual_count = self.count_dice(bet[1])
            if actual_count == bet[0]:
                reward = 1 if self.current_player == 0 else -1
            else:
                reward = -1 if self.current_player == 0 else 1
            done = True
        
        return self.get_state(), reward, done, info
    
    def get_legal_actions(self) -> List[Tuple[str, Tuple[int, int]]]:
        """Return list of all legal actions in the current state."""
        actions = []
        
        # Add all possible bets
        if self.current_bet is None:
            for count in range(1, self.num_dice * 2 + 1):
                for value in range(1, 7):
                    actions.append(('bet', (count, value)))
        else:
            current_count, current_value = self.current_bet
            for count in range(current_count, self.num_dice * 2 + 1):
                for value in range(1, 7):
                    if count > current_count or (count == current_count and value > current_value):
                        actions.append(('bet', (count, value)))
        
        # Add liar and spot_on actions if there's a current bet
        if self.current_bet is not None:
            actions.append(('liar', None))
            actions.append(('spot_on', self.current_bet))
        
        return actions 