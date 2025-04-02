"""
Chart styling and appearance settings.
"""

class ChartStyling:
    """Define styling for charts and visualizations"""
    
    # Default colors for chart elements
    COLORS = {
        # For price chart
        'price_line': '#000000',         # Black for price line
        'ma_50': '#0000FF',              # Blue for 50-day MA
        'ma_200': '#FF0000',             # Red for 200-day MA
        'support': '#00AA00',            # Green for support levels
        'resistance': '#AA0000',         # Red for resistance levels
        'current_price': '#0088FF',      # Blue for current price marker
        
        # For volume profile
        'volume_below': '#00FFFF',       # Cyan for volume below current price
        'volume_above': '#FF00FF',       # Magenta for volume above current price
        
        # For Fibonacci levels
        'fib_0': '#808080',              # Gray
        'fib_236': '#FFD700',            # Gold
        'fib_382': '#FFA500',            # Orange
        'fib_50': '#FF4500',             # OrangeRed
        'fib_618': '#FF0000',            # Red
        'fib_786': '#8B0000',            # DarkRed
        'fib_100': '#808080',            # Gray
    }
    
    # Line styles
    LINE_STYLES = {
        'price': '-',
        'ma': '-',
        'support': '--',
        'resistance': '--',
        'fibonacci': '-',
        'current_price': '-',
    }
    
    # Line widths
    LINE_WIDTHS = {
        'price': 1.5,
        'ma': 1.0,
        'support': 1.0,
        'resistance': 1.0,
        'fibonacci': 2.0,
        'current_price': 1.0,
    }
    
    # Alpha (transparency) values
    ALPHA = {
        'volume_bars': 0.6,
        'support': 0.7,
        'resistance': 0.7,
        'fibonacci': 0.6,
        'current_price': 0.5,
        'legend': 0.8,
    }
    
    # Font sizes
    FONT_SIZES = {
        'title': 14,
        'axis_label': 12,
        'tick_label': 10,
        'legend': 9,
        'annotation': 9,
        'fib_label': 9,
    }
    
    @classmethod
    def get_fibonacci_color(cls, percentage):
        """
        Get color for a Fibonacci percentage
        
        Parameters:
        percentage (str): Fibonacci percentage as string (e.g., '23.6%')
        
        Returns:
        str: Color hex code
        """
        percentage = percentage.strip('%')
        
        # Map percentage to color key
        color_map = {
            '0': 'fib_0',
            '23.6': 'fib_236',
            '38.2': 'fib_382',
            '50': 'fib_50',
            '61.8': 'fib_618',
            '78.6': 'fib_786',
            '100': 'fib_100',
        }
        
        color_key = color_map.get(percentage, 'fib_50')  # Default to 50% color if not found
        return cls.COLORS[color_key]