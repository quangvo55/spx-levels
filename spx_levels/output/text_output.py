"""
Format analysis results as text output.
"""

from datetime import datetime
from ..levels.strength import LevelStrength


class TextOutput:
    """Format results as text output for display or saving"""
    
    @staticmethod
    def format_levels_output(results, num_levels=8):
        """
        Format the technical levels into a readable output
        
        Parameters:
        results (dict): Results from technical level analysis
        num_levels (int): Number of support and resistance levels to include
        
        Returns:
        str: Formatted text output
        """
        output = []
        
        # Add header
        output.append(f"Technical Levels Report - {datetime.now().strftime('%Y-%m-%d')}")
        output.append(f"Current Price: {results['current_price']:.2f}")
        output.append("")
        
        # Add VIX analysis if available
        if results.get('vix_analysis'):
            output.append(f"VIX Analysis: {results['vix_analysis']}")
            output.append("")
        
        # Add resistance levels
        output.append("Resistance Levels:")
        for i, (level, sources) in enumerate(results['resistance_levels'][:num_levels]):
            strength = results['level_strength'][level]
            strength_indicator = LevelStrength.get_strength_indicator(strength)
            sources_str = ", ".join(set(sources))
            output.append(f"{level:.2f} {strength_indicator} - {sources_str}")
        
        output.append("")
        
        # Add support levels
        output.append("Support Levels:")
        for i, (level, sources) in enumerate(results['support_levels'][:num_levels]):
            strength = results['level_strength'][level]
            strength_indicator = LevelStrength.get_strength_indicator(strength)
            sources_str = ", ".join(set(sources))
            output.append(f"{level:.2f} {strength_indicator} - {sources_str}")
        
        # Add legend
        output.append("")
        output.append("Strength Indicator: * (weak) to ***** (very strong)")
        
        return "\n".join(output)
    
    @staticmethod
    def format_swing_points_output(swing_highs, swing_lows):
        """
        Format swing high and low points into a readable output
        
        Parameters:
        swing_highs (pandas.DataFrame): Dataframe of swing high points
        swing_lows (pandas.DataFrame): Dataframe of swing low points
        
        Returns:
        str: Formatted text output
        """
        output = []
        
        # Add header
        output.append(f"Swing Points Analysis - {datetime.now().strftime('%Y-%m-%d')}")
        output.append("=" * 60)
        output.append("")
        
        # Add swing highs
        output.append("SWING HIGHS (used for Fibonacci calculations)")
        output.append("-" * 60)
        if swing_highs.empty:
            output.append("No significant swing highs identified in the current data")
        else:
            # Sort by date, most recent first
            try:
                sorted_highs = swing_highs.sort_values('Date', ascending=False)
                for i, row in sorted_highs.iterrows():
                    date_str = row['Date'].strftime('%Y-%m-%d')
                    output.append(f"{date_str}: {row['High']:.2f}")
            except Exception as e:
                output.append(f"Error sorting swing highs: {str(e)}")
        
        output.append("")
        
        # Add swing lows
        output.append("SWING LOWS (used for Fibonacci calculations)")
        output.append("-" * 60)
        if swing_lows.empty:
            output.append("No significant swing lows identified in the current data")
        else:
            # Sort by date, most recent first
            try:
                sorted_lows = swing_lows.sort_values('Date', ascending=False)
                for i, row in sorted_lows.iterrows():
                    date_str = row['Date'].strftime('%Y-%m-%d')
                    output.append(f"{date_str}: {row['Low']:.2f}")
            except Exception as e:
                output.append(f"Error sorting swing lows: {str(e)}")
        
        output.append("")
        output.append("Note: Fibonacci retracements are calculated using combinations")
        output.append("of these swing highs and lows, prioritizing recent swings.")
        
        return "\n".join(output)