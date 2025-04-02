"""
Market data fetching and preparation for technical analysis.
"""

import pandas as pd
import yfinance as yf


class MarketData:
    """Handle fetching and managing market data"""
    
    def __init__(self, ticker="^GSPC", period="1y", interval="1d"):
        """
        Initialize market data handler
        
        Parameters:
        ticker (str): Ticker symbol (default: ^GSPC for S&P 500)
        period (str): Data period (e.g., "1y", "6mo", "3mo")
        interval (str): Data interval (e.g., "1d", "1h")
        """
        self.ticker = ticker
        self.period = period
        self.interval = interval
        self.data = None
        self.vix_data = None
    
    def fetch_data(self):
        """
        Fetch main price data
        
        Returns:
        pandas.DataFrame: Historical market data
        """
        stock = yf.Ticker(self.ticker)
        self.data = stock.history(period=self.period, interval=self.interval)
        
        # Add Date column for easier access
        self.data['Date'] = self.data.index
        
        return self.data
    
    def fetch_vix_data(self):
        """
        Fetch VIX volatility data
        
        Returns:
        pandas.DataFrame: VIX historical data
        """
        vix = yf.Ticker("^VIX")
        self.vix_data = vix.history(period=self.period, interval=self.interval)
        
        # Add Date column for easier access
        self.vix_data['Date'] = self.vix_data.index
        
        return self.vix_data
    
    def get_current_price(self):
        """Get the most recent closing price"""
        if self.data is None:
            self.fetch_data()
            
        return self.data['Close'].iloc[-1]
    
    def get_price_range(self):
        """Get the min/max price range"""
        if self.data is None:
            self.fetch_data()
            
        return {
            'min': self.data['Low'].min(),
            'max': self.data['High'].max()
        }