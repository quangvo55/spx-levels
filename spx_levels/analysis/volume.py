"""
Volume profile analysis.
"""

import pandas as pd
import numpy as np


class VolumeAnalysis:
    """Analyze volume distribution and identify volume-based levels"""
    
    def __init__(self, data):
        """
        Initialize volume analysis
        
        Parameters:
        data (pandas.DataFrame): OHLC price data with Volume column
        """
        self.data = data
        
    def find_volume_clusters(self, num_clusters=10):
        """
        Find price levels with high volume
        
        Parameters:
        num_clusters (int): Number of volume clusters to identify
        
        Returns:
        list: Price levels with high volume as (price, label) tuples
        """
        # Create price bins
        min_price = self.data['Low'].min()
        max_price = self.data['High'].max()
        price_range = max_price - min_price
        bin_size = price_range / 100  # 100 bins across the price range
        
        # Create bins and sum volume in each bin
        bins = np.arange(min_price, max_price + bin_size, bin_size)
        price_points = (self.data['High'] + self.data['Low']) / 2  # Use the middle price
        volume_by_price = pd.Series(index=bins[:-1])
        
        for i in range(len(bins) - 1):
            bin_volume = self.data.loc[(price_points >= bins[i]) & 
                                     (price_points < bins[i + 1]), 'Volume'].sum()
            volume_by_price[bins[i]] = bin_volume
        
        # Find significant volume clusters (local maxima)
        significant_levels = volume_by_price.nlargest(num_clusters).index.tolist()
        return [(level, "Volume cluster") for level in significant_levels]
    
    def calculate_volume_profile(self, num_bins=100):
        """
        Calculate full volume profile for visualization
        
        Parameters:
        num_bins (int): Number of price bins to use
        
        Returns:
        tuple: (bin_centers, volume_by_price, min_price, max_price, bin_size)
        """
        min_price = self.data['Low'].min()
        max_price = self.data['High'].max()
        price_range = max_price - min_price
        bin_size = price_range / num_bins
        
        bins = np.arange(min_price, max_price + bin_size, bin_size)
        price_points = (self.data['High'] + self.data['Low']) / 2
        volume_by_price = np.zeros(len(bins) - 1)
        
        for i in range(len(bins) - 1):
            mask = (price_points >= bins[i]) & (price_points < bins[i + 1])
            volume_by_price[i] = self.data.loc[mask, 'Volume'].sum()
        
        # Calculate bin centers
        bin_centers = (bins[:-1] + bins[1:]) / 2
        
        return bin_centers, volume_by_price, min_price, max_price, bin_size