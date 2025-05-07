"""
Main entry point for SPX Levels technical analysis tool.
"""

import argparse
from datetime import datetime
import pandas as pd # Still needed for DataFrame checks, but not for yfinance VIX data

# The file market_data.py now contains SchwabClientSingleton
from .data import SchwabClientSingleton
from .analysis import PriceAction, FibonacciAnalysis, VolumeAnalysis, MovingAverages, VolatilityAnalysis
from .levels import TechnicalLevels, PsychologicalLevels
from .visualization import ChartGenerator
from .output import TextOutput, FileOutput


def analyze_market(ticker="SPY", period="6m", include_vix=True, plot=True, output_folder="outputs"):
    """
    Analyze market data and generate technical levels using Schwab API.
    
    Parameters:
    ticker (str): Ticker symbol (default: SPX. Schwab may require different symbols, e.g., $SPX.X for S&P 500 index).
    period (str): Data period (e.g., "1y", "6m", "90d") for main ticker and VIX.
    include_vix (bool): Whether to include VIX analysis (fetched via Schwab API using a VIX ticker like $VIX.X).
    plot (bool): Whether to generate and show plot.
    output_folder (str): Folder to save outputs.
    
    Returns:
    dict: Results dictionary
    """
    # Setup output handler
    file_output = FileOutput(output_folder)
    
    # Instantiate Schwab client
    schwab_client = SchwabClientSingleton()

    print(f"Fetching daily data for {ticker} using Schwab API for period: {period}...")
    
    schwab_ticker_main = ticker

    data = schwab_client.get_daily_price_history(ticker=schwab_ticker_main, period_str=period)
    
    if data.empty:
        print(f"Failed to fetch or process data for {schwab_ticker_main} from Schwab. Exiting analysis.")
        return {}
    
    # Fetch VIX data using Schwab API if requested
    vix_data = None
    volatility_analyzer = None
    if include_vix:
        # Common Schwab ticker for VIX. User might need to verify/change this.
        schwab_vix_ticker = "$VIX.X" 
        print(f"Fetching VIX data ({schwab_vix_ticker}) using Schwab API for period {period}...")
        
        vix_data = schwab_client.get_daily_price_history(ticker=schwab_vix_ticker, period_str=period)
        
        if not vix_data.empty:
            # The get_daily_price_history method already ensures 'Date' column exists if data is present.
            volatility_analyzer = VolatilityAnalysis(vix_data)
        else:
            print(f"Could not fetch VIX data for {schwab_vix_ticker} from Schwab API. Proceeding without VIX analysis.")
            
    # Initialize analyzers
    price_action = PriceAction(data)
    fibonacci = FibonacciAnalysis(data)
    volume = VolumeAnalysis(data)
    
    moving_averages = MovingAverages(data)
    data = moving_averages.calculate_mas(windows=[50, 200])
    
    psychological = PsychologicalLevels(data)
    
    print("Identifying swing points...")
    swing_highs, swing_lows = price_action.identify_swing_points()
    
    print("Calculating technical levels...")
    level_analyzer = TechnicalLevels(
        data, 
        price_action, 
        fibonacci, 
        volume, 
        moving_averages, 
        psychological,
        volatility_analyzer # Will be None if VIX fetching failed or was disabled
    )
    
    results = level_analyzer.identify_levels(swing_highs, swing_lows)
    
    text_output = TextOutput()
    levels_text = text_output.format_levels_output(results)
    swing_points_text = text_output.format_swing_points_output(swing_highs, swing_lows)
    
    print("\n" + levels_text)
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    file_output.save_levels_text(levels_text, ticker, date_str)
    file_output.save_swing_points_text(swing_points_text, ticker, date_str)
    
    if plot:
        chart_path = file_output.get_chart_path(ticker, date_str)
        chart_generator = ChartGenerator(data, results, volume)
        chart_generator.plot_levels_chart(save_path=chart_path)
    
    return results


def main():
    """Command-line entry point"""
    parser = argparse.ArgumentParser(description='Calculate technical levels for a stock or index using Schwab API for all market data.')
    parser.add_argument('--ticker', type=str, default='SPY', help='Ticker symbol (default: SPX. Schwab may require specific format e.g. $SPX.X for indices)')
    parser.add_argument('--period', type=str, default='1y', help='Data period for main ticker and VIX (e.g., "1y", "6m", "90d", default: 1y).')
    parser.add_argument('--no-vix', action='store_false', dest='include_vix', help='Exclude VIX analysis (VIX is also fetched via Schwab API, e.g., $VIX.X)')
    parser.add_argument('--no-plot', action='store_false', dest='plot', help='Do not display plot')
    parser.add_argument('--output', type=str, default='outputs', help='Output folder for results (default: outputs)')
    
    args = parser.parse_args()
    
    analyze_market(
        ticker=args.ticker, 
        period=args.period, 
        include_vix=args.include_vix, 
        plot=args.plot, 
        output_folder=args.output
    )


if __name__ == "__main__":
    main()