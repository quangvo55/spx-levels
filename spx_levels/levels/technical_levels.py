"""
Main technical level identification and consolidation.
"""

class TechnicalLevels:
    """Identify and manage technical price levels"""
    
    def __init__(self, data, price_action, fibonacci, volume, moving_averages, psychological, vix_analysis=None):
        """
        Initialize technical level analyzer
        
        Parameters:
        data (pandas.DataFrame): OHLC price data
        price_action: Price action analyzer
        fibonacci: Fibonacci analyzer
        volume: Volume analyzer
        moving_averages: Moving averages analyzer
        psychological: Psychological level analyzer
        vix_analysis: Optional VIX analyzer
        """
        self.data = data
        self.price_action = price_action
        self.fibonacci = fibonacci
        self.volume = volume
        self.moving_averages = moving_averages
        self.psychological = psychological
        self.vix_analysis = vix_analysis
        
        self.current_price = data['Close'].iloc[-1]
        self.all_levels = []
        self.grouped_levels = []
        self.level_strength = {}
        self.support_levels = []
        self.resistance_levels = []
        
    def identify_levels(self, swing_highs=None, swing_lows=None):
        """
        Identify all technical levels using various methods
        
        Parameters:
        swing_highs: Optional pre-calculated swing highs
        swing_lows: Optional pre-calculated swing lows
        
        Returns:
        dict: Results dictionary containing all level information
        """
        # Get swing points if not provided
        if swing_highs is None or swing_lows is None:
            swing_highs, swing_lows = self.price_action.identify_swing_points()
            
        # Get Fibonacci levels
        fib_levels = self.fibonacci.calculate_fibonacci_levels(swing_highs, swing_lows)
        
        # Get volume-based levels
        volume_levels = self.volume.find_volume_clusters()
        
        # Get psychological levels
        psych_levels = self.psychological.find_psychological_levels()
        
        # Get support/resistance from price action
        support, resistance = self.price_action.identify_support_resistance()
        
        # Get moving average levels
        ma_levels = self.moving_averages.get_ma_levels()
        
        # Combine all levels
        self.all_levels = volume_levels + psych_levels + support + resistance + ma_levels
        
        # Add Fibonacci levels
        for key, fib_dict in fib_levels.items():
            for ratio, level in fib_dict.items():
                self.all_levels.append((level, f"Fibonacci {ratio} ({key})"))
        
        # Sort levels by price
        self.all_levels.sort(key=lambda x: x[0])
        
        # Group nearby levels
        self._group_levels()
        
        # Calculate level strength
        from .strength import LevelStrength
        self.level_strength = LevelStrength.calculate_strength(self.grouped_levels)
        
        # Classify as support or resistance
        self._classify_levels()
        
        # Sort by strength
        self.support_levels = LevelStrength.sort_by_strength(self.support_levels, self.level_strength)
        self.resistance_levels = LevelStrength.sort_by_strength(self.resistance_levels, self.level_strength)
        
        # Get VIX analysis if available
        vix_analysis_text = None
        if self.vix_analysis:
            vix_analysis_text = self.vix_analysis.analyze_vix()
            
        # Return results
        return {
            'current_price': self.current_price,
            'support_levels': self.support_levels,
            'resistance_levels': self.resistance_levels,
            'level_strength': self.level_strength,
            'vix_analysis': vix_analysis_text,
            'all_levels': self.grouped_levels  # Include all levels for debugging
        }
    
    def _group_levels(self, threshold=0.002):
        """
        Group nearby levels to reduce noise
        
        Parameters:
        threshold (float): Price difference threshold as percentage
        """
        self.grouped_levels = []
        
        if not self.all_levels:
            return
            
        current_group = [self.all_levels[0]]
        
        for i in range(1, len(self.all_levels)):
            current_level = self.all_levels[i][0]
            prev_level = current_group[-1][0]
            
            # If current level is within threshold of previous level, add to current group
            if abs(current_level - prev_level) / prev_level < threshold:
                current_group.append(self.all_levels[i])
            else:
                # Create a new group
                avg_level = sum(level[0] for level in current_group) / len(current_group)
                sources = [level[1] for level in current_group]
                self.grouped_levels.append((avg_level, sources))
                current_group = [self.all_levels[i]]
        
        # Add the last group
        if current_group:
            avg_level = sum(level[0] for level in current_group) / len(current_group)
            sources = [level[1] for level in current_group]
            self.grouped_levels.append((avg_level, sources))
    
    def _classify_levels(self):
        """Classify levels as support or resistance based on current price"""
        # Debug: Make sure we have levels both above and below current price
        print(f"Current price: {self.current_price}")
        
        above_count = sum(1 for level, _ in self.grouped_levels if level > self.current_price)
        below_count = sum(1 for level, _ in self.grouped_levels if level < self.current_price)
        
        print(f"Found {above_count} levels above current price")
        print(f"Found {below_count} levels below current price")
        
        # Assign levels to support and resistance
        self.support_levels = [(level, sources) for level, sources in self.grouped_levels 
                              if level < self.current_price]
        self.resistance_levels = [(level, sources) for level, sources in self.grouped_levels 
                                 if level >= self.current_price]