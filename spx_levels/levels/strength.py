"""
Level strength calculation and sorting.
"""

class LevelStrength:
    """Calculate the strength of technical levels"""
    
    @staticmethod
    def calculate_strength(grouped_levels):
        """
        Calculate level strength based on number of confluent factors
        
        Parameters:
        grouped_levels (list): List of (level, sources) tuples
        
        Returns:
        dict: Dictionary mapping level to its strength value
        """
        level_strength = {}
        
        for level, sources in grouped_levels:
            strength = len(sources)
            
            # Volume clusters and price action get extra weight
            for source in sources:
                if "Volume" in source or "price action" in source:
                    strength += 1
                    
            # Fibonacci levels with multiple confluent ratios get extra weight
            fib_count = sum(1 for src in sources if "Fibonacci" in src)
            if fib_count > 1:
                strength += fib_count - 1
                
            level_strength[level] = strength
            
        return level_strength
    
    @staticmethod
    def sort_by_strength(levels, level_strength):
        """
        Sort levels by their strength
        
        Parameters:
        levels (list): List of (level, sources) tuples
        level_strength (dict): Dictionary mapping level to its strength
        
        Returns:
        list: Sorted levels list
        """
        return sorted(levels, key=lambda x: level_strength[x[0]], reverse=True)
    
    @staticmethod
    def get_strength_indicator(strength, max_stars=5):
        """
        Get a visual indicator of level strength
        
        Parameters:
        strength (int): Numeric strength value
        max_stars (int): Maximum number of stars to display
        
        Returns:
        str: String of stars (*) representing strength
        """
        return '*' * min(strength, max_stars)