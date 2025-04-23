import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from liars_dice_env import LiarsDiceEnv
from q_learning_agent import QLearningAgent
from collections import deque
import json
import os

class LiarsDiceGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Liar's Dice")
        
        # Initialize game components
        self.env = LiarsDiceEnv()
        self.ai_agent = QLearningAgent(self.env)
        policy_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'liars_dice_policy.gz')
        self.ai_agent.load_compressed_q_table(policy_path)
        
        # Game state
        self.current_player = 0
        self.game_history = deque(maxlen=10)
        self.stats = {
            'wins': 0,
            'losses': 0,
            'total_games': 0,
            'user_bets': [],
            'ai_bets': []
        }
        
        # Load saved stats if they exist
        self.load_stats()
        
        # Create main game frame
        self.create_main_frame()
        
        # Create stats window
        self.create_stats_window()
        
        # Start new game
        self.start_new_game()
    
    def create_main_frame(self):
        # Main container
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Player info
        self.player_label = ttk.Label(self.main_frame, text="Current Player: 1")
        self.player_label.grid(row=0, column=0, columnspan=3, pady=5)
        
        # Dice display
        self.dice_frame = ttk.Frame(self.main_frame)
        self.dice_frame.grid(row=1, column=0, columnspan=3, pady=10)
        self.dice_labels = []
        for i in range(5):
            label = ttk.Label(self.dice_frame, text="?", width=3, relief="solid")
            label.grid(row=0, column=i, padx=2)
            self.dice_labels.append(label)
        
        # Current bet display
        self.current_bet_label = ttk.Label(self.main_frame, text="Current Bet: None")
        self.current_bet_label.grid(row=2, column=0, columnspan=3, pady=5)
        
        # Betting controls
        self.bet_frame = ttk.Frame(self.main_frame)
        self.bet_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        ttk.Label(self.bet_frame, text="Count:").grid(row=0, column=0)
        self.count_var = tk.StringVar()
        self.count_combo = ttk.Combobox(self.bet_frame, textvariable=self.count_var, width=5)
        self.count_combo.grid(row=0, column=1, padx=5)
        
        ttk.Label(self.bet_frame, text="Value:").grid(row=0, column=2)
        self.value_var = tk.StringVar()
        self.value_combo = ttk.Combobox(self.bet_frame, textvariable=self.value_var, width=5)
        self.value_combo.grid(row=0, column=3, padx=5)
        
        self.bet_button = ttk.Button(self.bet_frame, text="Place Bet", command=self.place_bet)
        self.bet_button.grid(row=0, column=4, padx=5)
        
        # Action buttons
        self.action_frame = ttk.Frame(self.main_frame)
        self.action_frame.grid(row=4, column=0, columnspan=3, pady=10)
        
        self.liar_button = ttk.Button(self.action_frame, text="Call Liar", command=self.call_liar)
        self.liar_button.grid(row=0, column=0, padx=5)
        
        self.spot_on_button = ttk.Button(self.action_frame, text="Spot On", command=self.call_spot_on)
        self.spot_on_button.grid(row=0, column=1, padx=5)
        
        # Game history
        self.history_frame = ttk.Frame(self.main_frame)
        self.history_frame.grid(row=5, column=0, columnspan=3, pady=10)
        
        self.history_label = ttk.Label(self.history_frame, text="Game History:")
        self.history_label.grid(row=0, column=0, sticky=tk.W)
        
        self.history_text = tk.Text(self.history_frame, height=10, width=40)
        self.history_text.grid(row=1, column=0, columnspan=3)
        
        # Play again button
        self.play_again_button = ttk.Button(self.main_frame, text="Play Again", command=self.start_new_game)
        self.play_again_button.grid(row=6, column=0, columnspan=3, pady=10)
        
        # Disable buttons initially
        self.update_button_states()
    
    def create_stats_window(self):
        self.stats_window = tk.Toplevel(self.root)
        self.stats_window.title("Game Statistics")
        self.stats_window.protocol("WM_DELETE_WINDOW", self.hide_stats_window)
        
        # Stats display
        self.stats_frame = ttk.Frame(self.stats_window, padding="10")
        self.stats_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.stats_labels = {}
        stats = ['wins', 'losses', 'total_games', 'win_rate']
        for i, stat in enumerate(stats):
            ttk.Label(self.stats_frame, text=stat.replace('_', ' ').title() + ":").grid(row=i, column=0, sticky=tk.W)
            self.stats_labels[stat] = ttk.Label(self.stats_frame, text="0")
            self.stats_labels[stat].grid(row=i, column=1, sticky=tk.W)
        
        # Reset stats button
        ttk.Button(self.stats_frame, text="Reset Stats", command=self.reset_stats).grid(row=len(stats), column=0, columnspan=2, pady=10)
        
        self.update_stats_display()
    
    def hide_stats_window(self):
        self.stats_window.withdraw()
    
    def show_stats_window(self):
        self.stats_window.deiconify()
    
    def load_stats(self):
        try:
            with open('liars_dice_stats.json', 'r') as f:
                self.stats = json.load(f)
        except FileNotFoundError:
            pass
    
    def save_stats(self):
        with open('liars_dice_stats.json', 'w') as f:
            json.dump(self.stats, f)
    
    def reset_stats(self):
        self.stats = {
            'wins': 0,
            'losses': 0,
            'total_games': 0,
            'user_bets': [],
            'ai_bets': []
        }
        self.save_stats()
        self.update_stats_display()
    
    def update_stats_display(self):
        self.stats_labels['wins'].config(text=str(self.stats['wins']))
        self.stats_labels['losses'].config(text=str(self.stats['losses']))
        self.stats_labels['total_games'].config(text=str(self.stats['total_games']))
        win_rate = (self.stats['wins'] / self.stats['total_games'] * 100) if self.stats['total_games'] > 0 else 0
        self.stats_labels['win_rate'].config(text=f"{win_rate:.1f}%")
    
    def start_new_game(self):
        # Reset game state
        self.env.reset()
        self.current_player = 0
        self.game_history.clear()
        self.history_text.delete(1.0, tk.END)
        
        # Update dice display
        self.update_dice_display()
        
        # Update current bet display
        self.current_bet_label.config(text="Current Bet: None")
        
        # Update betting controls
        self.update_betting_controls()
        
        # Update button states
        self.update_button_states()
        
        # If AI is player 1, make its move
        if self.current_player == 1:
            self.make_ai_move()
    
    def update_dice_display(self):
        dice = self.env.player1_dice if self.current_player == 0 else self.env.player2_dice
        for i, (label, value) in enumerate(zip(self.dice_labels, dice)):
            label.config(text=str(value))
            if self.current_player == 0:  # Highlight user's dice
                label.config(background='lightblue')
            else:
                label.config(background='SystemButtonFace')
    
    def update_betting_controls(self):
        # Get legal actions
        legal_actions = self.env.get_legal_actions()
        
        # Filter betting actions
        betting_actions = [a for a in legal_actions if a[0] == 'bet']
        
        # Update count and value comboboxes
        if betting_actions:
            counts = sorted(set(a[1][0] for a in betting_actions))
            values = sorted(set(a[1][1] for a in betting_actions))
            
            self.count_combo['values'] = counts
            self.value_combo['values'] = values
            
            # Set default values
            if counts:
                self.count_var.set(counts[0])
            if values:
                self.value_var.set(values[0])
        else:
            self.count_combo['values'] = []
            self.value_combo['values'] = []
            self.count_var.set('')
            self.value_var.set('')
    
    def update_button_states(self):
        # Enable/disable buttons based on current player and game state
        is_user_turn = self.current_player == 0
        has_current_bet = self.env.current_bet is not None
        
        self.bet_button.config(state=tk.NORMAL if is_user_turn else tk.DISABLED)
        self.liar_button.config(state=tk.NORMAL if (is_user_turn and has_current_bet) else tk.DISABLED)
        self.spot_on_button.config(state=tk.NORMAL if (is_user_turn and has_current_bet) else tk.DISABLED)
    
    def place_bet(self):
        try:
            count = int(self.count_var.get())
            value = int(self.value_var.get())
            action = ('bet', (count, value))
            
            # Validate the bet
            if not self.env.is_valid_bet((count, value)):
                if self.env.current_bet is None:
                    messagebox.showerror("Invalid Bet", "Count must be at least 1 and value must be between 1 and 6.")
                else:
                    current_count, current_value = self.env.current_bet
                    if count <= current_count and (count < current_count or value <= current_value):
                        messagebox.showerror("Invalid Bet", 
                            f"Your bet must be higher than the current bet of {current_count} {current_value}'s.\n"
                            f"Either increase the count above {current_count}, or keep the count at {current_count} "
                            f"and increase the value above {current_value}.")
                return
            
            # Execute action
            state = self.env.get_state()
            next_state, reward, done, _ = self.env.step(action)
            
            # Update display
            self.current_bet_label.config(text=f"Current Bet: {count} {value}'s")
            self.add_to_history(f"Player {self.current_player + 1} bet {count} {value}'s", 'blue')
            
            # Switch players
            self.current_player = 1 - self.current_player
            self.player_label.config(text=f"Current Player: {self.current_player + 1}")
            
            # Update controls
            self.update_betting_controls()
            self.update_button_states()
            
            # Make AI move if it's their turn
            if self.current_player == 1 and not done:
                self.make_ai_move()
            
        except ValueError:
            messagebox.showerror("Invalid Bet", "Please select valid count and value.")
    
    def call_liar(self):
        action = ('liar', None)
        self.execute_action(action, "called Liar", 'orange')
    
    def call_spot_on(self):
        action = ('spot_on', self.env.current_bet)
        self.execute_action(action, "called Spot On", 'green')
    
    def execute_action(self, action, action_text, color):
        # Execute action
        state = self.env.get_state()
        next_state, reward, done, _ = self.env.step(action)
        
        # Update display
        self.add_to_history(f"Player {self.current_player + 1} {action_text}", color)
        
        # Check if game is over
        if done:
            self.handle_game_over(reward)
        else:
            # Switch players
            self.current_player = 1 - self.current_player
            self.player_label.config(text=f"Current Player: {self.current_player + 1}")
            
            # Update controls
            self.update_betting_controls()
            self.update_button_states()
            
            # Make AI move if it's their turn
            if self.current_player == 1:
                self.make_ai_move()
    
    def make_ai_move(self):
        # Get current state
        state = self.env.get_state()
        
        # Choose action using trained policy
        action = self.ai_agent.choose_action(state)
        
        # Execute action
        next_state, reward, done, _ = self.env.step(action)
        
        # Update display based on action type
        action_type, bet_info = action
        if action_type == 'bet':
            count, value = bet_info
            self.current_bet_label.config(text=f"Current Bet: {count} {value}'s")
            self.add_to_history(f"AI bet {count} {value}'s", 'red')
        elif action_type == 'liar':
            self.add_to_history("AI called Liar", 'orange')
        elif action_type == 'spot_on':
            self.add_to_history("AI called Spot On", 'green')
        
        # Check if game is over
        if done:
            self.handle_game_over(-reward)  # Negate reward since it's from AI's perspective
        else:
            # Switch back to user
            self.current_player = 0
            self.player_label.config(text="Current Player: 1")
            
            # Update controls
            self.update_betting_controls()
            self.update_button_states()
    
    def add_to_history(self, text, color):
        self.game_history.append((text, color))
        self.history_text.delete(1.0, tk.END)
        for text, color in self.game_history:
            self.history_text.insert(tk.END, text + '\n', color)
    
    def handle_game_over(self, reward):
        # Show opponent's dice and actual count
        if self.env.current_bet is not None:
            count, value = self.env.current_bet
            total_count = self.env.count_dice(value)
            opponent_dice = self.env.player2_dice if self.current_player == 0 else self.env.player1_dice
            
            # Create message with opponent's dice and count
            dice_str = ", ".join(map(str, opponent_dice))
            message = f"Opponent's dice: {dice_str}\n"
            message += f"Total {value}'s (including wild ones): {total_count}\n"
            
            if reward > 0:
                message += "You won!"
                self.stats['wins'] += 1
            else:
                message += "You lost!"
                self.stats['losses'] += 1
            
            messagebox.showinfo("Game Over", message)
        else:
            if reward > 0:
                messagebox.showinfo("Game Over", "You won!")
                self.stats['wins'] += 1
            else:
                messagebox.showinfo("Game Over", "You lost!")
                self.stats['losses'] += 1
        
        # Update stats
        self.stats['total_games'] += 1
        
        # Save and update stats
        self.save_stats()
        self.update_stats_display()
        
        # Disable all buttons except Play Again
        self.bet_button.config(state=tk.DISABLED)
        self.liar_button.config(state=tk.DISABLED)
        self.spot_on_button.config(state=tk.DISABLED)
        self.play_again_button.config(state=tk.NORMAL)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = LiarsDiceGame()
    game.run() 