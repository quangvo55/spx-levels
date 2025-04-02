"""
Fibonacci retracement analysis.
"""

class FibonacciAnalysis:
    """Calculate Fibonacci retracement levels"""
    
    def __init__(self, data):
        """
        Initialize Fibonacci analysis
        
        Parameters:
        data (pandas.DataFrame): OHLC price data
        """
        self.data = data
        self.ratios = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1]
        self.ratio_labels = [f"{int(ratio*100)}%" if ratio != 0 and ratio != 1 else f"{int(ratio*100)}" 
                           for ratio in self.ratios]
    
    def calculate_fibonacci_levels(self, swing_highs, swing_lows, num_levels=3):
        """
        Calculate Fibonacci retracement levels for multiple swing high/low pairs
        
        Parameters:
        swing_highs (pandas.DataFrame): Swing highs with High and Date columns
        swing_lows (pandas.DataFrame): Swing lows with Low and Date columns
        num_levels (int): Number of recent swing high/low pairs to use
        
        Returns:
        dict: Dictionary of Fibonacci levels
        """
        fib_levels = {}
        
        # Check if we have any swing points
        if swing_highs.empty or swing_lows.empty:
            return fib_levels
        
        # Get the most recent swing high and most recent swing low
        try:
            recent_highs = swing_highs.nlargest(num_levels, 'Date')
            recent_lows = swing_lows.nlargest(num_levels, 'Date')
        except Exception:
            # If there's an issue, return empty dictionary
            return fib_levels
        
        # Find the most recent significant swing (either high or low)
        latest_high_date = recent_highs.iloc[0]['Date'] if not recent_highs.empty else None
        latest_low_date = recent_lows.iloc[0]['Date'] if not recent_lows.empty else None
        
        # Determine which is more recent
        is_high = False
        if latest_high_date is not None and latest_low_date is not None:
            is_high = latest_high_date > latest_low_date
        elif latest_high_date is not None:
            is_high = True
        
        # For each pair of recent swing high and swing low
        for i in range(min(num_levels, len(recent_highs), len(recent_lows))):
            try:
                swing_high = recent_highs.iloc[i]['High']
                swing_low = recent_lows.iloc[i]['Low']
                
                # If the most recent point is a high, we're in a downtrend (high to low)
                if is_high:
                    diff = swing_high - swing_low
                    levels = [swing_low + ratio * diff for ratio in self.ratios]
                    key = f"Fib_Down_{i+1}"
                # Otherwise, we're in an uptrend (low to high)
                else:
                    diff = swing_high - swing_low
                    levels = [swing_low + ratio * diff for ratio in self.ratios]
                    key = f"Fib_Up_{i+1}"
                    
                fib_levels[key] = dict(zip(self.ratio_labels, levels))
            except Exception:
                # Skip this pair if there's an issue
                continue
        
        return fib_levels