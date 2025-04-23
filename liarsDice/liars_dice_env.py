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
            
            # Calculate actual count for current bet
            if value == 1:
                actual_count = np.sum(self.player1_dice == 1) + np.sum(self.player2_dice == 1)
                expected_value = 10 * (1/6)  # Expected number of ones
            else:
                actual_count = (np.sum(self.player1_dice == value) + np.sum(self.player2_dice == value) +
                              np.sum(self.player1_dice == 1) + np.sum(self.player2_dice == 1))
                expected_value = 10 * (2/6)  # Expected count including wild ones
            
            # Features about the current bet
            state[14] = expected_value
            state[15] = actual_count
            state[16] = (count - expected_value) / expected_value if expected_value > 0 else 1.0
            state[17] = (count - actual_count) / actual_count if actual_count > 0 else 1.0
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
        - For value=1: Only count actual ones (no wild cards)
        - For values 2-6: Count both the specific value AND ones (wild)
        
        Args:
            value: The dice value to count (1-6)
        
        Returns:
            Total count according to game rules
        """
        # Count actual dice showing the value
        p1_count = np.sum(self.player1_dice == value)
        p2_count = np.sum(self.player2_dice == value)
        total = p1_count + p2_count
        
        # For non-1 values, add ones as wild cards
        if value != 1:
            p1_ones = np.sum(self.player1_dice == 1)
            p2_ones = np.sum(self.player2_dice == 1)
            total += p1_ones + p2_ones
        
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
        2. ('liar', None): Challenge previous bet
        3. ('spot_on', (count, value)): Claim previous bet is exactly right
        
        Rewards:
        - Base: +1 for winning, -1 for losing
        - Betting rewards/penalties:
          * Value Bets (standard play):
            - +0.4 for making a value bet (count ≈ own_dice + expected_opponent_dice)
            - +0.2 bonus if opponent calls liar on value bet
          * Bluffs:
            - +0.6 for successful bluff (opponent calls spot on or raises)
            - -0.4 for failed bluff (opponent calls liar)
            - +0.3 for making a believable bluff (count within 1 of value bet range)
          * Low Bets:
            - +0.3 for making a low bet (count ≤ expected_opponent_dice)
            - +0.2 bonus if opponent calls liar on subsequent value bet
        - Liar Call rewards/penalties:
          * +0.5 for calling liar on definite bluff
          * +0.3 for calling liar on likely bluff
          * -0.3 for calling liar on value bet
        - Spot On rewards/penalties:
          * +0.5 for calling spot on on exact count
          * -0.5 for calling spot on on wrong count
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
                
                # Calculate dice counts and expected values
                count, value = bet
                if self.current_player == 0:
                    agent_dice = self.player1_dice
                    opponent_dice = self.player2_dice
                else:
                    agent_dice = self.player2_dice
                    opponent_dice = self.player1_dice
                
                # Count agent's dice for the bet value
                agent_count = np.sum(agent_dice == value) if value > 1 else np.sum(agent_dice == 1)
                
                # Calculate expected opponent dice
                remaining_dice = 10 - (np.sum(self.player1_dice == 1) + np.sum(self.player2_dice == 1))
                if value == 1:
                    expected_opponent = remaining_dice * (1/6)  # Only actual ones
                else:
                    expected_opponent = remaining_dice * (2/6)  # Value + wild ones
                
                # Calculate value bet range
                value_bet_min = agent_count + expected_opponent - 0.5
                value_bet_max = agent_count + expected_opponent + 0.5
                
                # Determine bet type and assign rewards
                if count <= expected_opponent:
                    # Low bet
                    reward = 0.3 if self.current_player == 0 else -0.3
                    info['bet_type'] = 'low'
                elif value_bet_min <= count <= value_bet_max:
                    # Value bet
                    reward = 0.4 if self.current_player == 0 else -0.4
                    info['bet_type'] = 'value'
                else:
                    # Bluff
                    if abs(count - value_bet_max) <= 1:
                        # Believable bluff
                        reward = 0.3 if self.current_player == 0 else -0.3
                    else:
                        # Obvious bluff
                        reward = -0.2 if self.current_player == 0 else 0.2
                    info['bet_type'] = 'bluff'
                
                # Store additional information for when the bet is challenged
                info['agent_count'] = agent_count
                info['expected_opponent'] = expected_opponent
                info['value_bet_range'] = (value_bet_min, value_bet_max)
        
        elif action_type == 'liar':
            self.round_number += 1
            bet_count, bet_value = self.current_bet
            
            # Get detailed count information
            p1_value = np.sum(self.player1_dice == bet_value)
            p2_value = np.sum(self.player2_dice == bet_value)
            p1_ones = np.sum(self.player1_dice == 1)
            p2_ones = np.sum(self.player2_dice == 1)
            
            # Calculate actual count with detailed breakdown
            if bet_value == 1:
                actual_count = p1_value + p2_value  # Only actual ones
            else:
                actual_count = p1_value + p2_value + p1_ones + p2_ones  # Value + wild ones
            
            # Store detailed count information
            info['count_details'] = {
                'p1_value': p1_value,
                'p2_value': p2_value,
                'p1_ones': p1_ones,
                'p2_ones': p2_ones,
                'total_value': p1_value + p2_value,
                'total_ones': p1_ones + p2_ones,
                'actual_count': actual_count
            }
            
            # Calculate expected value
            remaining_dice = 10 - (p1_ones + p2_ones)
            if bet_value == 1:
                expected_value = p1_value + p2_value + remaining_dice * (1/6)  # Only actual ones
            else:
                expected_value = p1_value + p2_value + p1_ones + p2_ones + remaining_dice * (2/6)  # Value + wild ones
            
            # Calculate maximum possible count and expected value
            max_possible = p1_value + p2_value + remaining_dice
            
            # Get agent's own dice count
            if self.current_player == 0:
                agent_value = p1_value
                agent_ones = p1_ones
            else:
                agent_value = p2_value
                agent_ones = p2_ones
            
            # Determine if it was a bluff based on agent's knowledge
            is_bluff = (bet_count > max_possible or 
                       bet_count > expected_value + 2 or 
                       (bet_value == 1 and agent_ones == 0 and bet_count > 5))
            
            if actual_count < bet_count:
                # Successful liar call
                reward = 1 if self.current_player == 0 else -1
                
                # Additional rewards for calling liar on bluffs
                if is_bluff:
                    if bet_count > max_possible:
                        reward += 0.8 if self.current_player == 0 else -0.8  # Definite bluff
                    elif bet_count > expected_value + 2:
                        reward += 0.5 if self.current_player == 0 else -0.5  # Likely bluff
                    else:
                        reward += 0.2 if self.current_player == 0 else -0.2  # Borderline case
                else:
                    # Penalty for calling liar on value bet
                    reward -= 0.5 if self.current_player == 0 else 0.5
            else:
                # Failed liar call
                reward = -1 if self.current_player == 0 else 1
                
                # Additional penalty for failing to call a bluff
                if is_bluff:
                    if bet_count > max_possible:
                        reward -= 0.8 if self.current_player == 0 else 0.8  # Obvious bluff
                    else:
                        reward -= 0.2 if self.current_player == 0 else 0.2  # Less obvious bluff
            
            done = True
        
        elif action_type == 'spot_on':
            self.round_number += 1
            bet_count, bet_value = self.current_bet
            
            # Get detailed count information
            p1_value = np.sum(self.player1_dice == bet_value)
            p2_value = np.sum(self.player2_dice == bet_value)
            p1_ones = np.sum(self.player1_dice == 1)
            p2_ones = np.sum(self.player2_dice == 1)
            
            # Calculate actual count with detailed breakdown
            if bet_value == 1:
                actual_count = p1_value + p2_value  # Only actual ones
            else:
                actual_count = p1_value + p2_value + p1_ones + p2_ones  # Value + wild ones
            
            # Store detailed count information
            info['count_details'] = {
                'p1_value': p1_value,
                'p2_value': p2_value,
                'p1_ones': p1_ones,
                'p2_ones': p2_ones,
                'total_value': p1_value + p2_value,
                'total_ones': p1_ones + p2_ones,
                'actual_count': actual_count
            }
            
            # Calculate expected value
            remaining_dice = 10 - (p1_ones + p2_ones)
            if bet_value == 1:
                expected_value = p1_value + p2_value + remaining_dice * (1/6)  # Only actual ones
            else:
                expected_value = p1_value + p2_value + p1_ones + p2_ones + remaining_dice * (2/6)  # Value + wild ones
            
            if actual_count == bet_count:
                # Successful spot on call
                reward = 1 if self.current_player == 0 else -1
                # Calculate deviation from expected value
                expected_deviation = abs(bet_count - expected_value) / expected_value if expected_value > 0 else 1
                # Scale bonus based on how unlikely the bet was
                if expected_deviation > 1:
                    reward += 0.4 if self.current_player == 0 else -0.4  # Lower bonus for unlikely exact count
                else:
                    reward += 0.8 if self.current_player == 0 else -0.8  # Standard bonus for likely exact count
            elif abs(actual_count - bet_count) <= 1:
                # Close but not exact
                reward = -1 if self.current_player == 0 else 1
                # Calculate deviation from expected value
                expected_deviation = abs(bet_count - expected_value) / expected_value if expected_value > 0 else 1
                # Scale reward based on how unlikely the bet was
                if expected_deviation > 1:
                    reward += 0.1 if self.current_player == 0 else -0.1  # Minimal reward for unlikely close call
                else:
                    reward += 0.3 if self.current_player == 0 else -0.3  # Standard reward for likely close call
            else:
                # Failed spot on call
                reward = -1 if self.current_player == 0 else 1
                # Calculate deviation from expected value
                expected_deviation = abs(bet_count - expected_value) / expected_value if expected_value > 0 else 1
                # Scale penalty based on how unlikely the bet was
                if expected_deviation > 1:
                    reward -= 1.5 if self.current_player == 0 else 1.5  # Higher penalty for unlikely wrong call
                else:
                    reward -= 0.8 if self.current_player == 0 else 0.8  # Standard penalty for likely wrong call
                if abs(actual_count - bet_count) > 2:
                    reward -= 0.3 if self.current_player == 0 else 0.3  # Additional penalty for being far off
            
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