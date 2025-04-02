"""
Psychological price level identification.
"""

import numpy as np


class PsychologicalLevels:
    """Identify psychologically significant price levels"""
    
    def __init__(self, data):
        """
        Initialize psychological level finder
        
        Parameters:
        data (pandas.DataFrame): OHLC price data
        """
        self.data = data
        
    def find_psychological_levels(self, nearby_pct=2.0):
        """
        Identify psychological price levels (round numbers)
        
        Parameters:
        nearby_pct (float): Percentage range to consider "nearby" the current price
        
        Returns:
        list: Psychological price levels as (price, label) tuples
        """
        current_price = self.data['Close'].iloc[-1]
        
        # Calculate price range to consider - increased from 1% to 2%
        price_range = current_price * nearby_pct / 100
        min_price = current_price - price_range
        max_price = current_price + price_range
        
        # Debug info
        print(f"Psychological level range: {min_price:.2f} to {max_price:.2f}")
        
        # Find round numbers within this range
        levels = []
        
        # 100-point levels (e.g., 5500, 5600)
        hundreds = np.arange(np.floor(min_price / 100) * 100, np.ceil(max_price / 100) * 100, 100)
        for level in hundreds:
            levels.append((level, "Round number (100s)"))
        
        # 50-point levels (e.g., 5550, 5650)
        fifties = np.arange(np.floor(min_price / 50) * 50, np.ceil(max_price / 50) * 50, 50)
        for level in fifties:
            if level not in hundreds:
                levels.append((level, "Round number (50s)"))
        
        # 25-point levels (e.g., 5525, 5575)
        twentyfives = np.arange(np.floor(min_price / 25) * 25, np.ceil(max_price / 25) * 25, 25)
        for level in twentyfives:
            if level not in hundreds and level not in fifties:
                levels.append((level, "Round number (25s)"))
        
        # Debug info
        levels_above = sum(1 for level, _ in levels if level > current_price)
        levels_below = sum(1 for level, _ in levels if level < current_price)
        print(f"Found {levels_above} psychological levels above current price")
        print(f"Found {levels_below} psychological levels below current price")
        
        return levels