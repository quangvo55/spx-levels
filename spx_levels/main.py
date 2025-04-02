"""
Main entry point for SPX Levels technical analysis tool.
"""

import argparse
from datetime import datetime

from .data import MarketData
from .analysis import PriceAction, FibonacciAnalysis, VolumeAnalysis, MovingAverages, VolatilityAnalysis
from .levels import TechnicalLevels, PsychologicalLevels
from .visualization import ChartGenerator
from .output import TextOutput, FileOutput


def analyze_market(ticker="^GSPC", period="1y", include_vix=True, plot=True, output_folder="outputs"):
    """
    Analyze market data and generate technical levels
    
    Parameters:
    ticker (str): Ticker symbol (default: ^GSPC for S&P 500)
    period (str): Data period (e.g., "1y", "6mo", "3mo")
    include_vix (bool): Whether to include VIX analysis
    plot (bool): Whether to generate and show plot
    output_folder (str): Folder to save outputs
    
    Returns:
    dict: Results dictionary
    """
    # Setup output handler
    file_output = FileOutput(output_folder)
    
    # Fetch market data
    print(f"Fetching data for {ticker}...")
    market_data = MarketData(ticker=ticker, period=period)
    data = market_data.fetch_data()
    
    # Fetch VIX data if requested
    vix_data = None
    volatility_analyzer = None
    if include_vix:
        print("Fetching VIX data...")
        vix_data = market_data.fetch_vix_data()
        volatility_analyzer = VolatilityAnalysis(vix_data)
    
    # Initialize analyzers
    price_action = PriceAction(data)
    fibonacci = FibonacciAnalysis(data)
    volume = VolumeAnalysis(data)
    
    # Calculate moving averages
    moving_averages = MovingAverages(data)
    data = moving_averages.calculate_mas(windows=[50, 200])
    
    # Get psychological levels
    psychological = PsychologicalLevels(data)
    
    # Identify swing points
    print("Identifying swing points...")
    swing_highs, swing_lows = price_action.identify_swing_points()
    
    # Analyze technical levels
    print("Calculating technical levels...")
    level_analyzer = TechnicalLevels(
        data, 
        price_action, 
        fibonacci, 
        volume, 
        moving_averages, 
        psychological,
        volatility_analyzer
    )
    
    results = level_analyzer.identify_levels(swing_highs, swing_lows)
    
    # Format output
    text_output = TextOutput()
    levels_text = text_output.format_levels_output(results)
    swing_points_text = text_output.format_swing_points_output(swing_highs, swing_lows)
    
    # Print results
    print("\n" + levels_text)
    
    # Save output files
    date_str = datetime.now().strftime("%Y-%m-%d")
    file_output.save_levels_text(levels_text, ticker, date_str)
    file_output.save_swing_points_text(swing_points_text, ticker, date_str)
    
    # Generate chart if requested
    if plot:
        chart_path = file_output.get_chart_path(ticker, date_str)
        chart_generator = ChartGenerator(data, results, volume)
        chart_generator.plot_levels_chart(save_path=chart_path)
    
    return results


def main():
    """Command-line entry point"""
    parser = argparse.ArgumentParser(description='Calculate technical levels for a stock or index')
    parser.add_argument('--ticker', type=str, default='^GSPC', help='Ticker symbol (default: ^GSPC for S&P 500)')
    parser.add_argument('--period', type=str, default='1y', help='Data period (default: 1y)')
    parser.add_argument('--no-vix', action='store_false', dest='include_vix', help='Exclude VIX analysis')
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