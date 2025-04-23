import numpy as np
from typing import Tuple, List, Dict
from liars_dice_env import LiarsDiceEnv
from q_learning_agent import QLearningAgent
from collections import defaultdict
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
import time
import os

class ParallelTrainer:
    def __init__(self, num_episodes: int, num_processes: int = None):
        self.num_episodes = num_episodes
        self.num_processes = num_processes or mp.cpu_count()
        self.stats = {
            'action_counts': {'bet': 0, 'liar': 0, 'spot_on': 0},
            'bet_values': defaultdict(int),
            'bet_sizes': defaultdict(int),
            'bluffs': defaultdict(int),
            'semi_bluffs': defaultdict(int),
            'liar_calls': defaultdict(int),
            'spot_on_calls': defaultdict(int)
        }
    
    def train_episode(self, _) -> Tuple[Dict, Dict]:
        """Train a single episode with two agents."""
        env = LiarsDiceEnv()
        agent1 = QLearningAgent(env)
        agent2 = QLearningAgent(env)
        
        env.reset()
        state = env.get_state()
        done = False
        round_number = 0
        episode_stats = {
            'action_counts': {'bet': 0, 'liar': 0, 'spot_on': 0},
            'bet_values': defaultdict(int),
            'bet_sizes': defaultdict(int),
            'bluffs': defaultdict(int),
            'semi_bluffs': defaultdict(int),
            'liar_calls': defaultdict(int),
            'spot_on_calls': defaultdict(int)
        }
        
        while not done:
            round_number += 1
            current_agent = agent1 if env.current_player == 0 else agent2
            
            # Choose and execute action
            action = current_agent.choose_action(state)
            action_type, _ = action
            episode_stats['action_counts'][action_type] += 1
            
            # Analyze betting patterns
            current_agent.analyze_betting_patterns(state, action, episode_stats)
            
            # Track special actions
            if action_type == 'liar':
                episode_stats['liar_calls'][round_number] += 1
            elif action_type == 'spot_on':
                episode_stats['spot_on_calls'][round_number] += 1
            
            next_state, reward, done, _ = env.step(action)
            
            # Update Q-value for the current agent
            current_agent.update_q_value(state, action, reward, next_state)
            
            state = next_state
        
        return episode_stats, agent1.q_table
    
    def merge_stats(self, episode_stats: Dict) -> None:
        """Merge episode statistics into global statistics."""
        for action, count in episode_stats['action_counts'].items():
            self.stats['action_counts'][action] += count
        
        for value, count in episode_stats['bet_values'].items():
            self.stats['bet_values'][value] += count
        
        for size, count in episode_stats['bet_sizes'].items():
            self.stats['bet_sizes'][size] += count
        
        for value, count in episode_stats['bluffs'].items():
            self.stats['bluffs'][value] += count
        
        for value, count in episode_stats['semi_bluffs'].items():
            self.stats['semi_bluffs'][value] += count
        
        for round_num, count in episode_stats['liar_calls'].items():
            self.stats['liar_calls'][round_num] += count
        
        for round_num, count in episode_stats['spot_on_calls'].items():
            self.stats['spot_on_calls'][round_num] += count
    
    def print_stats(self, episode: int) -> None:
        """Print current statistics."""
        print(f"\nEpisode {episode + 1}")
        print("\nAction Distribution:")
        total_actions = sum(self.stats['action_counts'].values())
        for action, count in self.stats['action_counts'].items():
            print(f"{action}: {count} ({count/total_actions*100:.1f}%)")
        
        print("\nBet Value Distribution:")
        total_bets = sum(self.stats['bet_values'].values())
        for value, count in sorted(self.stats['bet_values'].items()):
            print(f"Value {value}: {count} ({count/total_bets*100:.1f}%)")
        
        print("\nBet Size Distribution:")
        for size, count in sorted(self.stats['bet_sizes'].items()):
            print(f"Size {size}: {count}")
        
        print("\nBluffing Analysis:")
        total_bluffs = sum(self.stats['bluffs'].values()) + sum(self.stats['semi_bluffs'].values())
        if total_bluffs > 0:
            print("True Bluffs:")
            for value, count in sorted(self.stats['bluffs'].items()):
                print(f"Value {value}: {count} ({count/total_bluffs*100:.1f}%)")
            print("\nSemi-Bluffs (using ones):")
            for value, count in sorted(self.stats['semi_bluffs'].items()):
                print(f"Value {value}: {count} ({count/total_bluffs*100:.1f}%)")
        
        print("\nSpecial Action Timing:")
        # Group liar calls into ranges
        liar_ranges = defaultdict(int)
        for round_num, count in self.stats['liar_calls'].items():
            range_start = ((round_num - 1) // 5) * 5 + 1
            range_end = range_start + 4
            range_key = f"Rounds {range_start}-{range_end}"
            liar_ranges[range_key] += count
        
        print("Liar calls by round ranges:")
        for range_key, count in sorted(liar_ranges.items(), key=lambda x: int(x[0].split()[1].split('-')[0])):
            print(f"{range_key}: {count}")
        
        # Group spot-on calls into ranges
        spot_on_ranges = defaultdict(int)
        for round_num, count in self.stats['spot_on_calls'].items():
            range_start = ((round_num - 1) // 5) * 5 + 1
            range_end = range_start + 4
            range_key = f"Rounds {range_start}-{range_end}"
            spot_on_ranges[range_key] += count
        
        print("\nSpot-on calls by round ranges:")
        for range_key, count in sorted(spot_on_ranges.items(), key=lambda x: int(x[0].split()[1].split('-')[0])):
            print(f"{range_key}: {count}")
    
    def train(self) -> None:
        """Train the agents in parallel."""
        start_time = time.time()
        
        with ProcessPoolExecutor(max_workers=self.num_processes) as executor:
            for i, (episode_stats, q_table) in enumerate(executor.map(self.train_episode, range(self.num_episodes))):
                self.merge_stats(episode_stats)
                
                if (i + 1) % 1000 == 0:
                    self.print_stats(i)
                    elapsed_time = time.time() - start_time
                    print(f"\nTime elapsed: {elapsed_time:.2f} seconds")
                    print(f"Average time per 1000 episodes: {elapsed_time/((i+1)/1000):.2f} seconds")
        
        print("\nTraining completed!")
        print(f"Total time: {time.time() - start_time:.2f} seconds")
        
        # Save final Q-table
        agent1 = QLearningAgent(LiarsDiceEnv())
        agent1.q_table = q_table
        policy_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'liars_dice_policy.gz')
        agent1.save_compressed_q_table(policy_path)

if __name__ == "__main__":
    trainer = ParallelTrainer(num_episodes=50000)
    trainer.train() 