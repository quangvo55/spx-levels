from schwab.auth import easy_client
import os
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

class SchwabClientSingleton:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SchwabClientSingleton, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, api_key=None, app_secret=None, callback_url=None, token_path=None):
        if self._initialized:
            return
        
        load_dotenv()

        self.api_key = api_key or os.environ.get('SCHWAB_API_KEY', 'key')
        self.app_secret = app_secret or os.environ.get('SCHWAB_APP_SECRET', 'secret')
        self.callback_url = callback_url or os.environ.get('SCHWAB_CALLBACK_URL', 'https://127.0.0.1:8182')
        self.token_path = token_path or os.environ.get('SCHWAB_TOKEN_PATH', 'token.json')
        
        self._client = None
        self._initialized = True
    
    @property
    def client(self):
        if self._client is None:
            self._client = easy_client(
                api_key=self.api_key,
                app_secret=self.app_secret,
                callback_url=self.callback_url,
                token_path=self.token_path
            )
        return self._client
    
    def _parse_period_to_datetime_range(self, period_str: str):
        end_dt = datetime.now()
        period_str = period_str.lower()
        num_str = "".join(filter(str.isdigit, period_str))
        unit = "".join(filter(str.isalpha, period_str))
        if not num_str:
            raise ValueError(f"Invalid period string: {period_str}. Number part missing.")
        num = int(num_str)
        if unit == 'y': start_dt = end_dt - timedelta(days=num * 365) 
        elif unit == 'm' or unit == 'mo': start_dt = end_dt - timedelta(days=num * 30) 
        elif unit == 'd': start_dt = end_dt - timedelta(days=num)
        elif unit == 'w': start_dt = end_dt - timedelta(weeks=num)
        else:
            print(f"Warning: Unknown period unit '{unit}' in '{period_str}'. Defaulting to 1 year.")
            start_dt = end_dt - timedelta(days=365)
        return start_dt, end_dt

    def get_daily_price_history(self, ticker: str, period_str: str = "1y", 
                                need_extended_hours_data: bool = False, 
                                need_previous_close: bool = False,
                                convert_to_spx_approx: bool = False,
                                spx_conversion_ticker: str = "SPY"):
        try:
            start_datetime, end_datetime = self._parse_period_to_datetime_range(period_str)
            
            resp = self.client.get_price_history_every_day(
                symbol=ticker,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                need_extended_hours_data=need_extended_hours_data,
                need_previous_close=need_previous_close
            )
            
            price_history_json = resp.json()

            if not price_history_json or 'candles' not in price_history_json or not price_history_json['candles']:
                print(f"No candle data returned from Schwab for {ticker} for the period '{period_str}'.")
                return pd.DataFrame()
            
            candles = price_history_json['candles']
            df = pd.DataFrame(candles)

            if df.empty:
                print(f"No candle data processed for {ticker}.")
                return pd.DataFrame()

            df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
            df.set_index('datetime', inplace=True)
            
            df.rename(columns={
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'volume': 'Volume'
            }, inplace=True)
            
            expected_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
            for col in expected_cols:
                if col not in df.columns:
                    df[col] = float('nan')
                    print(f"Warning: Column '{col}' was missing from Schwab data for {ticker}, filled with NaN.")

            df['Date'] = df.index 

            if convert_to_spx_approx and ticker.upper() == spx_conversion_ticker.upper():
                print(f"Applying SPX approximation (x10) to OHLC data for {ticker}.")
                price_cols = ['Open', 'High', 'Low', 'Close']
                for col in price_cols:
                    if col in df.columns:
                        df[col] = df[col] * 10.0
            
            return df
        except Exception as e:
            print(f"Error in get_daily_price_history for {ticker}: {e}")
            return pd.DataFrame()
    
    def get_price_history_every_fifteen_minutes(self, ticker, need_extended_hours_data=True):
        resp = self.client.get_price_history_every_fifteen_minutes(
            symbol=ticker,
            need_extended_hours_data=need_extended_hours_data
        )
        return resp.json()
    
    def get_option_chain(self, ticker):
        resp = self.client.get_option_chain(ticker)
        return resp.json()

client = SchwabClientSingleton()