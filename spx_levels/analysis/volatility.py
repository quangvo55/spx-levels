"""
Volatility analysis including VIX.
"""

class VolatilityAnalysis:
    """Analyze market volatility"""
    
    def __init__(self, vix_data=None):
        """
        Initialize volatility analysis
        
        Parameters:
        vix_data (pandas.DataFrame, optional): VIX data
        """
        self.vix_data = vix_data
        
    def analyze_vix(self):
        """
        Analyze VIX data relative to its moving average
        
        Returns:
        str: VIX analysis text or None if no VIX data
        """
        if self.vix_data is None or self.vix_data.empty:
            return None
            
        try:
            current_vix = self.vix_data['Close'].iloc[-1]
            vix_ma20 = self.vix_data['Close'].rolling(window=20).mean().iloc[-1]
            
            if current_vix < vix_ma20:
                return "VIX below 20-day average - favorable for upside targets."
            else:
                return "VIX above 20-day average - may need to decrease for upside targets."
        except Exception:
            return None