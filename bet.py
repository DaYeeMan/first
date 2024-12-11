import numpy as np
import matplotlib.pyplot as plt

def simulate_betting_strategies(initial_bet=10, 
                                initial_take_profit=500, 
                                total_simulations=10000, 
                                sigma=0.2, 
                                max_bet_multiplier=8):
    """
    Simulate Martingale and Normal betting strategies with zero-mean payout distribution
    
    Args:
        initial_bet: Starting bet amount
        initial_take_profit: Initial amount at which to end the current simulation
        total_simulations: Number of independent betting simulations
        sigma: Standard deviation of the payout distribution
        max_bet_multiplier: Limit on bet size growth
    """
    # Arrays to track results
    martingale_results = np.zeros(total_simulations)
    normal_results = np.zeros(total_simulations)
    
    # Arrays to track cumulative means
    martingale_cumulative_means = np.zeros(total_simulations)
    normal_cumulative_means = np.zeros(total_simulations)

    for i in range(total_simulations):
        # Martingale Strategy
        current_bet = initial_bet
        martingale_balance = 0
        martingale_bet_count = 0
        take_profit = initial_take_profit
        consecutive_losses = 0

        while martingale_balance < take_profit and martingale_bet_count < 100:
            # Generate payout from standard normal distribution
            payout = np.random.normal(0, sigma)
            
            # Win if positive, lose if negative
            if payout > 0:
                # Multiply initial bet by positive payout
                martingale_balance += current_bet * (payout)
                current_bet = initial_bet  # Reset bet after win
                consecutive_losses = 0
                # Restore take profit after a win
                take_profit = initial_take_profit
            else:
                martingale_balance -= current_bet * payout
                consecutive_losses += 1
                
                # Dynamically adjust take profit based on consecutive losses
                take_profit *= 0.9  # Reduce take profit by 10% after consecutive losses
                
                # Double bet, but limit growth
                current_bet = min(current_bet * 2, initial_bet * max_bet_multiplier)
            
            martingale_bet_count += 1
        
        martingale_results[i] = martingale_balance
        
        # Calculate cumulative mean up to this point
        martingale_cumulative_means[i] = np.mean(martingale_results[:i+1])

        # Normal Strategy (constant bet)
        normal_balance = 0
        normal_bet_count = 0

        while normal_balance < initial_take_profit and normal_bet_count < 100:
            # Generate payout from standard normal distribution
            payout = np.random.normal(0, sigma)
            
            # Win if positive, lose if negative
            if payout > 0:
                # Multiply initial bet by positive payout
                normal_balance += initial_bet * (payout)
            else:
                normal_balance -= initial_bet * payout
            
            normal_bet_count += 1
        
        normal_results[i] = normal_balance
        
        # Calculate cumulative mean up to this point
        normal_cumulative_means[i] = np.mean(normal_results[:i+1])

    # Compute statistics
    print("Martingale Strategy Statistics:")
    print(f"Mean Profit: ${martingale_results.mean():.2f}")
    print(f"Median Profit: ${np.median(martingale_results):.2f}")
    print(f"Success Rate: {100 * np.mean(martingale_results >= initial_take_profit):.2f}%")
    print(f"Standard Deviation: ${martingale_results.std():.2f}\n")

    print("Normal Strategy Statistics:")
    print(f"Mean Profit: ${normal_results.mean():.2f}")
    print(f"Median Profit: ${np.median(normal_results):.2f}")
    print(f"Success Rate: {100 * np.mean(normal_results >= initial_take_profit):.2f}%")
    print(f"Standard Deviation: ${normal_results.std():.2f}")

    # Plotting
    plt.figure(figsize=(16, 6))
    
    # Histogram
    plt.subplot(1, 3, 1)
    plt.hist(martingale_results, bins=50, alpha=0.5, label='Martingale')
    plt.hist(normal_results, bins=50, alpha=0.5, label='Normal')
    plt.title('Profit Distribution')
    plt.xlabel('Final Balance')
    plt.ylabel('Frequency')
    plt.legend()
    
    # Box Plot
    plt.subplot(1, 3, 2)
    plt.boxplot([martingale_results, normal_results], labels=['Martingale', 'Normal'])
    plt.title('Profit Comparison')
    plt.ylabel('Final Balance')
    
    # Cumulative Mean Plot
    plt.subplot(1, 3, 3)
    plt.plot(martingale_cumulative_means, label='Martingale')
    plt.plot(normal_cumulative_means, label='Normal')
    plt.title('Cumulative Mean Profit')
    plt.xlabel('Simulation Number')
    plt.ylabel('Cumulative Mean Profit')
    plt.legend()
    
    plt.tight_layout()
    plt.show()

# Run simulation
simulate_betting_strategies()