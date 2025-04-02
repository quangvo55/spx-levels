"""
Price action analysis including swing points and support/resistance identification.
"""

import pandas as pd
import numpy as np
from scipy.signal import argrelextrema


class PriceAction:
    """Analyze price action patterns"""
    
    def __init__(self, data):
        """
        Initialize price action analyzer
        
        Parameters:
        data (pandas.DataFrame): OHLC price data
        """
        self.data = data
        
    def identify_swing_points(self, order=20):
        """
        Identify significant swing highs and lows
        
        Parameters:
        order (int): The order of the extrema (how many points on each side to use for comparison)
        
        Returns:
        tuple: (swing_highs, swing_lows) as DataFrames
        """
        # Make a copy of the data
        df = self.data.copy()
        
        # Find local maxima and minima
        df['High_Smooth'] = df['High'].rolling(window=3).mean()  # Smooth the data
        df['Low_Smooth'] = df['Low'].rolling(window=3).mean()  # Smooth the data
        
        # Drop NaNs to avoid issues with argrelextrema
        df = df.dropna(subset=['High_Smooth', 'Low_Smooth'])
        
        if len(df) <= (2 * order + 1):  # Not enough data points
            # Return empty DataFrames
            swing_highs = pd.DataFrame(columns=['High', 'Date'])
            swing_lows = pd.DataFrame(columns=['Low', 'Date'])
            return swing_highs, swing_lows
        
        # Find local maxima (swing highs)
        max_idx = argrelextrema(df['High_Smooth'].values, np.greater, order=order)[0]
        swing_highs = pd.DataFrame({
            'High': df['High'].iloc[max_idx].values,
            'Date': df.index[max_idx]
        })
        
        # Find local minima (swing lows)
        min_idx = argrelextrema(df['Low_Smooth'].values, np.less, order=order)[0]
        swing_lows = pd.DataFrame({
            'Low': df['Low'].iloc[min_idx].values,
            'Date': df.index[min_idx]
        })
        
        return swing_highs, swing_lows
    
    def identify_support_resistance(self, window=20):
        """
        Identify support and resistance levels from recent price action
        
        Parameters:
        window (int): Lookback window for finding support/resistance
        
        Returns:
        tuple: (support_levels, resistance_levels) as lists of (price, label) tuples
        """
        recent_data = self.data.tail(window)
        
        # Find recent significant lows (support)
        support = []
        for i in range(2, len(recent_data) - 2):
            if (recent_data['Low'].iloc[i] < recent_data['Low'].iloc[i-1] and 
                recent_data['Low'].iloc[i] < recent_data['Low'].iloc[i-2] and
                recent_data['Low'].iloc[i] < recent_data['Low'].iloc[i+1] and
                recent_data['Low'].iloc[i] < recent_data['Low'].iloc[i+2]):
                support.append((recent_data['Low'].iloc[i], "Recent price action"))
        
        # Find recent significant highs (resistance)
        resistance = []
        for i in range(2, len(recent_data) - 2):
            if (recent_data['High'].iloc[i] > recent_data['High'].iloc[i-1] and 
                recent_data['High'].iloc[i] > recent_data['High'].iloc[i-2] and
                recent_data['High'].iloc[i] > recent_data['High'].iloc[i+1] and
                recent_data['High'].iloc[i] > recent_data['High'].iloc[i+2]):
                resistance.append((recent_data['High'].iloc[i], "Recent price action"))
        
        return support, resistance