"""
Liar's Dice Game Environment

Game Rules:
-----------
1. Setup:
   - 2 players, each with 5 dice
   - Dice are rolled secretly at the start of each game
   - Each player can only see their own dice

2. Gameplay:
   - Players take turns making one of three possible actions:
     a) Bet: Declare a quantity and value (e.g., "four 3s")
        - Must be higher than previous bet in either quantity or value
        - Example: "four 3s" can be followed by "four 4s" or "five 3s"
     b) Call Liar: Challenge the previous bet
     c) Call Spot On: Claim the previous bet is exactly correct

3. Special Rules for Counting Dice:
   - When counting dice for a bet of any value except 1:
     * Count all dice showing that value
     * Plus all 1s (they are wild and count as any value)
   - When betting or counting 1s:
     * Only actual 1s count (no wild dice)

4. Winning Conditions:
   - When Liar is Called:
     * If actual count < bet: Caller wins
     * If actual count >= bet: Previous better wins
   - When Spot On is Called:
     * If actual count = bet exactly: Caller wins
     * If actual count != bet: Previous better wins

Example:
--------
Player 1 dice: [1,2,3,4,5]
Player 2 dice: [1,3,3,4,6]
Total dice: 10

For a bet of "four 3s":
- Actual 3s: 3 (one from P1, two from P2)
- Wild 1s: 2 (one from each player)
- Total count: 5 (exceeds the bet of four 3s)

For a bet of "three 1s":
- Only actual 1s count: 2 (one from each player)
- Total count: 2 (less than the bet of three 1s)
"""

import numpy as np
from typing import Tuple, List, Dict
import random

class LiarsDiceEnv:
    def __init__(self):
        """Initialize the Liar's Dice environment with 5 dice per player."""
        self.num_dice = 5  # Each player gets 5 dice
        self.dice_values = 6  # Standard 6-sided dice
        self.reset()
        
    def reset(self) -> None:
        """
        Reset the game state:
        - Roll new dice for both players
        - Clear current bet
        - Reset to player 1's turn
        - Reset round counter and bet counter
        """
        self.player1_dice = np.random.randint(1, 7, self.num_dice)
        self.player2_dice = np.random.randint(1, 7, self.num_dice)
        self.current_bet = None  # Tuple of (count, value) or None
        self.current_player = 0  # 0 for player 1, 1 for player 2
        self.round_number = 0
        self.bets_made = 0
        
    def get_state(self) -> np.ndarray:
        """
        Return the current game state as a numpy array.
        
        State representation (26 features):
        [0-4]: Player 1's dice counts (2s through 6s)
        [5-9]: Player 2's dice counts (2s through 6s)
        [10]: Player 1's number of 1s
        [11]: Player 2's number of 1s
        [12-13]: Current bet (count, value) or 0 if no bet
        [14]: Expected value for current bet
        [15]: Actual count for current bet
        [16]: Normalized deviation from expected
        [17]: Normalized deviation from actual
        [18]: Round number
        [19]: Number of bets made
        [20-25]: Expected values for each possible bet (1-6)
        """
        state = np.zeros(26, dtype=np.float32)
        
        # Player 1's dice counts (excluding 1s)
        for i in range(2, 7):
            state[i-2] = np.sum(self.player1_dice == i)
        
        # Player 2's dice counts (excluding 1s)
        for i in range(2, 7):
            state[i+3] = np.sum(self.player2_dice == i)
        
        # Number of 1s for each player
        state[10] = np.sum(self.player1_dice == 1)
        state[11] = np.sum(self.player2_dice == 1)
        
        # Current bet information and derived features
        if self.current_bet is not None:
            count, value = self.current_bet
            state[12] = count
            state[13] = value
            
            # Calculate expected value and probability features
            if value == 1:
                # For ones, only count actual ones
                expected_value = 10 * (1/6)  # Expected number of ones
                actual_count = self.count_dice(1)
            else:
                # For other values, count both the value and ones (wild)
                expected_value = 10 * (2/6)  # Expected count including wild ones
                actual_count = self.count_dice(value)
            
            # Features about the current bet
            state[14] = expected_value
            state[15] = actual_count
            state[16] = (count - expected_value) / expected_value  # Normalized deviation from expected
            state[17] = (count - actual_count) / actual_count if actual_count > 0 else 0
        else:
            state[12:18] = 0
        
        # Game progress features
        state[18] = self.round_number
        state[19] = self.bets_made
        
        # Expected values for each possible bet value
        for value in range(1, 7):
            if value == 1:
                state[19 + value] = 10 * (1/6)  # Expected ones
            else:
                state[19 + value] = 10 * (2/6)  # Expected value + wild ones
        
        return state
    
    def count_dice(self, value: int) -> int:
        """
        Count total number of dice showing a specific value.
        
        Rules:
        - For value=1: Only count actual ones
        - For values 2-6: Count both the specific value AND ones (wild)
        
        Args:
            value: The dice value to count (1-6)
        
        Returns:
            Total count according to game rules
        """
        if value == 1:
            # For ones, only count actual ones
            return np.sum(self.player1_dice == 1) + np.sum(self.player2_dice == 1)
        else:
            # For other values, count both the value and ones (wild)
            total = np.sum(self.player1_dice == value) + np.sum(self.player2_dice == value)
            total += np.sum(self.player1_dice == 1) + np.sum(self.player2_dice == 1)
            return total
    
    def is_valid_bet(self, bet: Tuple[int, int]) -> bool:
        """
        Check if a bet is valid given the current bet.
        
        Rules:
        - First bet: Any valid count (≥1) and value (1-6)
        - Subsequent bets must be higher in either:
          a) Count: New count > current count
          b) Value: New count = current count AND new value > current value
        
        Args:
            bet: Tuple of (count, value)
        
        Returns:
            bool: Whether the bet is valid
        """
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
        Execute an action and return (next_state, reward, done, info).
        
        Actions:
        1. ('bet', (count, value)): Make a new bet
        2. ('liar', None): Challenge previous bet as too high
        3. ('spot_on', (count, value)): Claim previous bet is exactly right
        
        Rewards:
        - Base: +1 for winning, -1 for losing
        - Bluffing rewards/penalties:
          * +0.8 for successful bluff (opponent calls liar on reasonable bet)
          * -0.8 for failed bluff (opponent calls liar on actual bluff)
          * +0.5 for calling liar on definite bluff
          * +0.3 for calling liar on likely bluff
          * -0.3 for calling liar on reasonable bet
        - Spot On rewards/penalties:
          * +0.5 for calling spot on on exact count
          * -0.5 for calling spot on on wrong count
        
        Returns:
            Tuple of (next_state, reward, done, info)
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
                self.bets_made += 1
                
                # Calculate if this is a bluff
                count, value = bet
                if self.current_player == 0:
                    agent_dice_count = np.sum(self.player1_dice == value) if value > 1 else np.sum(self.player1_dice == 1)
                else:
                    agent_dice_count = np.sum(self.player2_dice == value) if value > 1 else np.sum(self.player2_dice == 1)
                
                remaining_dice = 10 - (np.sum(self.player1_dice == 1) + np.sum(self.player2_dice == 1))
                max_possible = agent_dice_count + remaining_dice
                
                # Store bluff information for when the bet is challenged
                info['is_bluff'] = count > max_possible or count > agent_dice_count + 2 or (count > agent_dice_count and count > max_possible * 0.8)
                info['bluff_type'] = 'semi_bluff' if value == 1 else 'true_bluff'
        
        elif action_type == 'liar':
            self.round_number += 1
            actual_count = self.count_dice(self.current_bet[1])
            bet_count, bet_value = self.current_bet
            
            # Get opponent's dice count for the bet value
            if self.current_player == 0:
                opponent_dice_count = np.sum(self.player2_dice == bet_value) if bet_value > 1 else np.sum(self.player2_dice == 1)
            else:
                opponent_dice_count = np.sum(self.player1_dice == bet_value) if bet_value > 1 else np.sum(self.player1_dice == 1)
            
            # Calculate maximum possible count
            remaining_dice = 10 - (np.sum(self.player1_dice == 1) + np.sum(self.player2_dice == 1))
            max_possible = opponent_dice_count + remaining_dice
            
            # Determine if it was a bluff
            is_bluff = bet_count > max_possible or bet_count > opponent_dice_count + 2 or (bet_count > opponent_dice_count and bet_count > max_possible * 0.8)
            
            if actual_count < bet_count:
                # Successful liar call
                reward = 1 if self.current_player == 0 else -1
                
                # Additional rewards for calling liar on bluffs
                if is_bluff:
                    if bet_count > max_possible:
                        reward += 0.5 if self.current_player == 0 else -0.5  # Definite bluff
                    else:
                        reward += 0.3 if self.current_player == 0 else -0.3  # Likely bluff
                else:
                    # Penalty for calling liar on reasonable bet
                    reward -= 0.3 if self.current_player == 0 else 0.3
            else:
                # Failed liar call
                reward = -1 if self.current_player == 0 else 1
                
                # Additional penalty for failing to call a bluff
                if is_bluff:
                    reward -= 0.8 if self.current_player == 0 else 0.8
            
            done = True
        
        elif action_type == 'spot_on':
            self.round_number += 1
            actual_count = self.count_dice(self.current_bet[1])
            bet_count, bet_value = self.current_bet
            
            if actual_count == bet_count:
                # Successful spot on call
                reward = 1 if self.current_player == 0 else -1
                reward += 0.5 if self.current_player == 0 else -0.5  # Bonus for exact count
            else:
                # Failed spot on call
                reward = -1 if self.current_player == 0 else 1
                reward -= 0.5 if self.current_player == 0 else 0.5  # Penalty for wrong count
            
            done = True
        
        return self.get_state(), reward, done, info
    
    def get_max_possible_count(self, value: int) -> int:
        """
        Calculate the maximum possible count of a value including ones.
        
        This is used to limit the range of possible bets to reasonable values.
        For non-1 values, includes both the specific value and wild 1s.
        For value=1, only counts actual 1s.
        
        Args:
            value: The dice value to count (1-6)
        
        Returns:
            Maximum possible count for this value
        """
        if value == 1:
            return np.sum(self.player1_dice == 1) + np.sum(self.player2_dice == 1)
        else:
            # Count actual dice showing this value
            count = np.sum(self.player1_dice == value) + np.sum(self.player2_dice == value)
            # Add all ones as they can be wild
            count += np.sum(self.player1_dice == 1) + np.sum(self.player2_dice == 1)
            return count
    
    def get_legal_actions(self) -> List[Tuple[str, Tuple[int, int]]]:
        """
        Return list of all legal actions in the current state.
        
        Legal actions:
        1. If no current bet:
           - Can bet any value (1-6) with count from 1 up to max_count + 2
        2. If there is a current bet:
           - Can bet higher count or same count with higher value
           - Can call 'liar'
           - Can call 'spot_on'
        
        The max_count + 2 allows for some bluffing while keeping bets reasonable.
        
        Returns:
            List of legal actions in the format (action_type, (count, value))
        """
        actions = []
        
        # Add all possible bets
        if self.current_bet is None:
            for value in range(1, 7):
                max_count = self.get_max_possible_count(value)
                # Allow bets up to max_count + 2 for bluffing
                for count in range(1, min(max_count + 3, self.num_dice * 2 + 1)):
                    actions.append(('bet', (count, value)))
        else:
            current_count, current_value = self.current_bet
            for value in range(1, 7):
                max_count = self.get_max_possible_count(value)
                # Allow bets up to max_count + 2 for bluffing
                for count in range(current_count, min(max_count + 3, self.num_dice * 2 + 1)):
                    if count > current_count or (count == current_count and value > current_value):
                        actions.append(('bet', (count, value)))
        
        # Add liar and spot_on actions if there's a current bet
        if self.current_bet is not None:
            actions.append(('liar', None))
            actions.append(('spot_on', self.current_bet))
        
        return actions 