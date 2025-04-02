"""
Moving average calculations and analysis.
"""

class MovingAverages:
    """Calculate and analyze moving averages"""
    
    def __init__(self, data):
        """
        Initialize moving averages analysis
        
        Parameters:
        data (pandas.DataFrame): OHLC price data
        """
        self.data = data
        self.ma_columns = []
        
    def calculate_mas(self, windows=[50, 200]):
        """
        Calculate moving averages for specified periods
        
        Parameters:
        windows (list): List of periods to calculate MAs for
        
        Returns:
        pandas.DataFrame: DataFrame with MA columns added
        """
        df = self.data.copy()
        
        for window in windows:
            column_name = f'MA_{window}'
            df[column_name] = df['Close'].rolling(window=window).mean()
            self.ma_columns.append(column_name)
            
        return df
    
    def get_ma_levels(self):
        """
        Get current MA values as support/resistance levels
        
        Returns:
        list: MA levels as (price, label) tuples
        """
        ma_levels = []
        
        for ma in self.ma_columns:
            if ma in self.data.columns and not self.data[ma].iloc[-1] != self.data[ma].iloc[-1]:  # Check for NaN
                ma_levels.append((self.data[ma].iloc[-1], f"{ma} support/resistance"))
                
        return ma_levels