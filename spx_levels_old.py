import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta
from scipy.signal import argrelextrema

def fetch_market_data(ticker="^GSPC", period="1y", interval="1d"):
    """
    Fetch historical market data using Yahoo Finance
    
    Parameters:
    ticker (str): Ticker symbol (default: ^GSPC for S&P 500)
    period (str): Data period (e.g., "1y", "6mo", "3mo")
    interval (str): Data interval (e.g., "1d", "1h")
    
    Returns:
    pandas.DataFrame: Historical market data
    """
    stock = yf.Ticker(ticker)
    data = stock.history(period=period, interval=interval)
    # Add Date column for easier access
    data['Date'] = data.index
    return data

def calculate_moving_averages(data, windows=[50, 200]):
    """Calculate moving averages"""
    df = data.copy()
    for window in windows:
        df[f'MA_{window}'] = df['Close'].rolling(window=window).mean()
    return df

def identify_swing_points(data, order=20):
    """
    Identify swing highs and lows
    
    Parameters:
    data (pandas.DataFrame): Price data
    order (int): The order of the extrema (how many points on each side to use for comparison)
    
    Returns:
    tuple: (swing_highs, swing_lows)
    """
    # Make a copy of the data
    df = data.copy()
    
    # Find local maxima and minima
    df['High_Smooth'] = df['High'].rolling(window=3).mean()  # Smooth the data
    df['Low_Smooth'] = df['Low'].rolling(window=3).mean()  # Smooth the data
    
    # Drop NaNs to avoid issues with argrelextrema
    df = df.dropna(subset=['High_Smooth', 'Low_Smooth'])
    
    if len(df) <= (2 * order + 1):  # Not enough data points
        # Return empty DataFrames
        swing_highs = pd.DataFrame(columns=['High', 'Date'])
        swing_lows = pd.DataFrame(columns=['Low', 'Date'])
        return swing_highs, swing_lows
    
    # Find local maxima (swing highs)
    max_idx = argrelextrema(df['High_Smooth'].values, np.greater, order=order)[0]
    swing_highs = pd.DataFrame({
        'High': df['High'].iloc[max_idx].values,
        'Date': df.index[max_idx]
    })
    
    # Find local minima (swing lows)
    min_idx = argrelextrema(df['Low_Smooth'].values, np.less, order=order)[0]
    swing_lows = pd.DataFrame({
        'Low': df['Low'].iloc[min_idx].values,
        'Date': df.index[min_idx]
    })
    
    return swing_highs, swing_lows

def calculate_fibonacci_levels(swing_highs, swing_lows, data, num_levels=3):
    """
    Calculate Fibonacci retracement levels for multiple swing high/low pairs
    
    Parameters:
    swing_highs (pandas.DataFrame): Swing highs
    swing_lows (pandas.DataFrame): Swing lows
    data (pandas.DataFrame): Price data
    num_levels (int): Number of recent swing high/low pairs to use
    
    Returns:
    dict: Dictionary of Fibonacci levels
    """
    # Fibonacci ratios
    ratios = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1]
    
    fib_levels = {}
    
    # Check if we have any swing points
    if swing_highs.empty or swing_lows.empty:
        return fib_levels
    
    # Get the most recent swing high and most recent swing low
    try:
        recent_highs = swing_highs.nlargest(num_levels, 'Date')
        recent_lows = swing_lows.nlargest(num_levels, 'Date')
    except Exception:
        # If there's an issue, return empty dictionary
        return fib_levels
    
    # Find the most recent significant swing (either high or low)
    latest_high_date = recent_highs.iloc[0]['Date'] if not recent_highs.empty else None
    latest_low_date = recent_lows.iloc[0]['Date'] if not recent_lows.empty else None
    
    # Determine which is more recent
    is_high = False
    if latest_high_date is not None and latest_low_date is not None:
        is_high = latest_high_date > latest_low_date
    elif latest_high_date is not None:
        is_high = True
    
    # For each pair of recent swing high and swing low
    for i in range(min(num_levels, len(recent_highs), len(recent_lows))):
        try:
            swing_high = recent_highs.iloc[i]['High']
            swing_low = recent_lows.iloc[i]['Low']
            
            # If the most recent point is a high, we're in a downtrend (high to low)
            if is_high:
                diff = swing_high - swing_low
                levels = [swing_low + ratio * diff for ratio in ratios]
                key = f"Fib_Down_{i+1}"
            # Otherwise, we're in an uptrend (low to high)
            else:
                diff = swing_high - swing_low
                levels = [swing_low + ratio * diff for ratio in ratios]
                key = f"Fib_Up_{i+1}"
                
            fib_levels[key] = dict(zip([f"{int(ratio*100)}%" if ratio != 0 and ratio != 1 else f"{int(ratio*100)}" for ratio in ratios], levels))
        except Exception:
            # Skip this pair if there's an issue
            continue
        
    return fib_levels

def find_volume_clusters(data, num_clusters=10):
    """
    Find price levels with high volume
    
    Parameters:
    data (pandas.DataFrame): Price and volume data
    num_clusters (int): Number of volume clusters to identify
    
    Returns:
    list: Price levels with high volume
    """
    # Create price bins
    min_price = data['Low'].min()
    max_price = data['High'].max()
    price_range = max_price - min_price
    bin_size = price_range / 100  # 100 bins across the price range
    
    # Create bins and sum volume in each bin
    bins = np.arange(min_price, max_price + bin_size, bin_size)
    price_points = (data['High'] + data['Low']) / 2  # Use the middle price
    volume_by_price = pd.Series(index=bins[:-1])
    
    for i in range(len(bins) - 1):
        bin_volume = data.loc[(price_points >= bins[i]) & (price_points < bins[i + 1]), 'Volume'].sum()
        volume_by_price[bins[i]] = bin_volume
    
    # Find significant volume clusters (local maxima)
    significant_levels = volume_by_price.nlargest(num_clusters).index.tolist()
    return significant_levels

def find_psychological_levels(data, nearby_pct=1.0):
    """
    Identify psychological price levels (round numbers)
    
    Parameters:
    data (pandas.DataFrame): Price data
    nearby_pct (float): Percentage range to consider "nearby" the current price
    
    Returns:
    list: Psychological price levels
    """
    current_price = data['Close'].iloc[-1]
    
    # Calculate price range to consider
    price_range = current_price * nearby_pct / 100
    min_price = current_price - price_range
    max_price = current_price + price_range
    
    # Find round numbers within this range
    levels = []
    
    # 100-point levels (e.g., 5500, 5600)
    hundreds = np.arange(np.floor(min_price / 100) * 100, np.ceil(max_price / 100) * 100, 100)
    for level in hundreds:
        levels.append((level, "Round number (100s)"))
    
    # 50-point levels (e.g., 5550, 5650)
    fifties = np.arange(np.floor(min_price / 50) * 50, np.ceil(max_price / 50) * 50, 50)
    for level in fifties:
        if level not in hundreds:
            levels.append((level, "Round number (50s)"))
    
    # 25-point levels (e.g., 5525, 5575)
    twentyfives = np.arange(np.floor(min_price / 25) * 25, np.ceil(max_price / 25) * 25, 25)
    for level in twentyfives:
        if level not in hundreds and level not in fifties:
            levels.append((level, "Round number (25s)"))
    
    return levels

def identify_support_resistance(data, window=20):
    """
    Identify support and resistance levels from recent price action
    
    Parameters:
    data (pandas.DataFrame): Price data
    window (int): Lookback window for finding support/resistance
    
    Returns:
    tuple: (support_levels, resistance_levels)
    """
    recent_data = data.tail(window)
    
    # Find recent significant lows (support)
    support = []
    for i in range(2, len(recent_data) - 2):
        if (recent_data['Low'].iloc[i] < recent_data['Low'].iloc[i-1] and 
            recent_data['Low'].iloc[i] < recent_data['Low'].iloc[i-2] and
            recent_data['Low'].iloc[i] < recent_data['Low'].iloc[i+1] and
            recent_data['Low'].iloc[i] < recent_data['Low'].iloc[i+2]):
            support.append((recent_data['Low'].iloc[i], "Recent price action"))
    
    # Find recent significant highs (resistance)
    resistance = []
    for i in range(2, len(recent_data) - 2):
        if (recent_data['High'].iloc[i] > recent_data['High'].iloc[i-1] and 
            recent_data['High'].iloc[i] > recent_data['High'].iloc[i-2] and
            recent_data['High'].iloc[i] > recent_data['High'].iloc[i+1] and
            recent_data['High'].iloc[i] > recent_data['High'].iloc[i+2]):
            resistance.append((recent_data['High'].iloc[i], "Recent price action"))
    
    return support, resistance

def find_key_technical_levels(data, vix_data=None, swing_highs=None, swing_lows=None):
    """
    Combine all methods to find key technical levels
    
    Parameters:
    data (pandas.DataFrame): Price and volume data
    vix_data (pandas.DataFrame, optional): VIX data
    swing_highs (pandas.DataFrame, optional): Pre-calculated swing highs
    swing_lows (pandas.DataFrame, optional): Pre-calculated swing lows
    
    Returns:
    dict: Dictionary of key levels and their sources
    """
    # Calculate moving averages
    data = calculate_moving_averages(data)
    
    # Find swing points if not provided
    if swing_highs is None or swing_lows is None:
        swing_highs, swing_lows = identify_swing_points(data)
    
    # Calculate Fibonacci levels
    fib_levels = calculate_fibonacci_levels(swing_highs, swing_lows, data)
    
    # Find volume clusters
    volume_levels = [(level, "Volume cluster") for level in find_volume_clusters(data)]
    
    # Find psychological levels
    psych_levels = find_psychological_levels(data)
    
    # Find support and resistance from recent price action
    support, resistance = identify_support_resistance(data)
    
    # Add moving averages as levels
    ma_levels = []
    for ma in ['MA_50', 'MA_200']:
        if ma in data.columns and not pd.isna(data[ma].iloc[-1]):
            ma_levels.append((data[ma].iloc[-1], f"{ma} support/resistance"))
    
    # Combine all levels
    all_levels = volume_levels + psych_levels + support + resistance + ma_levels
    
    # Extract levels from Fibonacci retracements
    for key, fib_dict in fib_levels.items():
        for ratio, level in fib_dict.items():
            all_levels.append((level, f"Fibonacci {ratio} ({key})"))
    
    # Sort levels by price
    all_levels.sort(key=lambda x: x[0])
    
    # Group nearby levels (within 0.2% of each other)
    grouped_levels = []
    
    if all_levels:  # Check if there are any levels
        current_group = [all_levels[0]]
        
        for i in range(1, len(all_levels)):
            current_level = all_levels[i][0]
            prev_level = current_group[-1][0]
            
            # If current level is within 0.2% of previous level, add to current group
            if abs(current_level - prev_level) / prev_level < 0.002:
                current_group.append(all_levels[i])
            else:
                # Create a new group
                avg_level = sum(level[0] for level in current_group) / len(current_group)
                sources = [level[1] for level in current_group]
                grouped_levels.append((avg_level, sources))
                current_group = [all_levels[i]]
        
        # Add the last group
        if current_group:
            avg_level = sum(level[0] for level in current_group) / len(current_group)
            sources = [level[1] for level in current_group]
            grouped_levels.append((avg_level, sources))
    
    # Calculate level strength based on number of confluent factors
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
    
    # Find the current price and classify levels as support or resistance
    current_price = data['Close'].iloc[-1]
    
    support_levels = [(level, sources) for level, sources in grouped_levels if level < current_price]
    resistance_levels = [(level, sources) for level, sources in grouped_levels if level >= current_price]
    
    # Sort by strength (descending)
    support_levels.sort(key=lambda x: level_strength[x[0]], reverse=True)
    resistance_levels.sort(key=lambda x: level_strength[x[0]], reverse=True)
    
    # Add VIX analysis if provided
    vix_analysis = None
    if vix_data is not None and not vix_data.empty:
        current_vix = vix_data['Close'].iloc[-1]
        vix_ma20 = vix_data['Close'].rolling(window=20).mean().iloc[-1]
        
        if current_vix < vix_ma20:
            vix_analysis = "VIX below 20-day average - favorable for upside targets."
        else:
            vix_analysis = "VIX above 20-day average - may need to decrease for upside targets."
    
    return {
        'current_price': current_price,
        'support_levels': support_levels,
        'resistance_levels': resistance_levels,
        'level_strength': level_strength,
        'vix_analysis': vix_analysis
    }

def format_levels_output(results, num_levels=8):
    """
    Format the technical levels into a readable output
    
    Parameters:
    results (dict): Results from find_key_technical_levels
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
    if results['vix_analysis']:
        output.append(f"VIX Analysis: {results['vix_analysis']}")
        output.append("")
    
    # Add resistance levels
    output.append("Resistance Levels:")
    for i, (level, sources) in enumerate(results['resistance_levels'][:num_levels]):
        strength = results['level_strength'][level]
        strength_indicator = '*' * min(strength, 5)  # Max 5 stars
        sources_str = ", ".join(set(sources))
        output.append(f"{level:.2f} {strength_indicator} - {sources_str}")
    
    output.append("")
    
    # Add support levels
    output.append("Support Levels:")
    for i, (level, sources) in enumerate(results['support_levels'][:num_levels]):
        strength = results['level_strength'][level]
        strength_indicator = '*' * min(strength, 5)  # Max 5 stars
        sources_str = ", ".join(set(sources))
        output.append(f"{level:.2f} {strength_indicator} - {sources_str}")
    
    # Add legend
    output.append("")
    output.append("Strength Indicator: * (weak) to ***** (very strong)")
    
    return "\n".join(output)

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

def plot_levels(data, results, save_path=None):
    """
    Plot the price chart with key technical levels and volume profile
    
    Parameters:
    data (pandas.DataFrame): Price data
    results (dict): Results from find_key_technical_levels
    save_path (str, optional): Path to save the plot
    
    Returns:
    None
    """
    # Create a figure with gridspec for complex layout
    fig = plt.figure(figsize=(16, 9))
    gs = fig.add_gridspec(1, 5)  # 1 row, 5 columns
    
    # Volume profile on the left (1/5 of the width)
    ax_vol_profile = fig.add_subplot(gs[0, 0])
    # Price chart taking the remaining 4/5
    ax_price = fig.add_subplot(gs[0, 1:])
    
    # Calculate volume profile
    min_price = data['Low'].min()
    max_price = data['High'].max()
    price_range = max_price - min_price
    num_bins = 100
    bin_size = price_range / num_bins
    
    bins = np.arange(min_price, max_price + bin_size, bin_size)
    price_points = (data['High'] + data['Low']) / 2
    volume_by_price = np.zeros(len(bins) - 1)
    
    for i in range(len(bins) - 1):
        mask = (price_points >= bins[i]) & (price_points < bins[i + 1])
        volume_by_price[i] = data.loc[mask, 'Volume'].sum()
    
    # Normalize volume for display
    if volume_by_price.max() > 0:  # Avoid division by zero
        normalized_volume = volume_by_price / volume_by_price.max()
    else:
        normalized_volume = volume_by_price
    
    # Plot horizontal volume bars
    bin_centers = (bins[:-1] + bins[1:]) / 2
    
    # Use cyan and magenta color scheme for volume profile (like in your example)
    colors = []
    for i in range(len(bin_centers)):
        # Current price index
        current_price = results['current_price']
        if bin_centers[i] <= current_price:
            colors.append('#00FFFF')  # Cyan for below current price
        else:
            colors.append('#FF00FF')  # Magenta for above current price
    
    # Plot volume profile bars horizontally
    ax_vol_profile.barh(bin_centers, normalized_volume, height=bin_size*0.8, color=colors, alpha=0.6)
    ax_vol_profile.set_ylim(min_price, max_price)
    ax_vol_profile.set_title('Volume Profile')
    ax_vol_profile.set_xlabel('Relative Volume')
    ax_vol_profile.grid(True, alpha=0.3)
    
    # Set y-axis to match the price chart
    ax_vol_profile.tick_params(axis='y', which='both', labelleft=False)  # Hide y-tick labels
    
    # Plot price data
    ax_price.plot(data.index, data['Close'], color='black', linewidth=1.5)
    
    # Plot moving averages
    if 'MA_50' in data.columns:
        ax_price.plot(data.index, data['MA_50'], color='blue', linewidth=1, label='50-day MA')
    if 'MA_200' in data.columns:
        ax_price.plot(data.index, data['MA_200'], color='red', linewidth=1, label='200-day MA')
    
    # Get Fibonacci levels from results
    fib_levels = {}
    fibonacci_colors = {
        '0%': '#808080',
        '23%': '#FFD700',
        '38%': '#FFA500',
        '50%': '#FF4500',
        '61%': '#FF0000',
        '78%': '#8B0000',
        '100%': '#808080'
    }
    
    # Extract Fibonacci levels from resistance and support
    for level_list in [results['resistance_levels'], results['support_levels']]:
        for level, sources in level_list:
            for source in sources:
                if 'Fibonacci' in source:
                    # Parse out the percentage and key
                    parts = source.split(' ')
                    for part in parts:
                        if '%' in part:
                            percentage = part
                            fib_levels[level] = (percentage, source)
                            break
    
    # Plot Fibonacci levels with percentage labels - make them more prominent
    for level, (percentage, source) in fib_levels.items():
        color = fibonacci_colors.get(percentage, '#FF00FF')  # Default to magenta if not found
        # Draw thicker, more visible lines
        ax_price.axhline(y=level, color=color, linestyle='-', alpha=0.6, linewidth=1)
        # Add more prominent labels with background
        ax_price.text(data.index[0], level, f"Fib {percentage}", color='white', ha='left', va='center', 
                     fontsize=9, fontweight='bold', bbox=dict(facecolor=color, alpha=0.8, pad=3))
        
        # # Repeat on volume profile with thicker lines
        # ax_vol_profile.axhline(y=level, color=color, linestyle='-', alpha=0.6, linewidth=2)
        # # Add small labels to volume profile too
        # ax_vol_profile.text(normalized_volume.max()*0.5, level, f"{percentage}", color='white', 
        #                    ha='center', va='center', fontsize=8, fontweight='bold',
        #                    bbox=dict(facecolor=color, alpha=0.8, pad=2))
    
    # Plot resistance levels
    for i, (level, sources) in enumerate(results['resistance_levels'][:8]):
        # Skip if it's already plotted as a Fibonacci level
        if level in fib_levels:
            continue
        ax_price.axhline(y=level, color='red', linestyle='--', alpha=0.7, linewidth=1)
        ax_price.text(data.index[-1], level, f"{level:.2f}", color='red', ha='right', va='bottom')
        # Add to volume profile chart too
        ax_vol_profile.axhline(y=level, color='red', linestyle='--', alpha=0.7, linewidth=1)
    
    # Plot support levels
    for i, (level, sources) in enumerate(results['support_levels'][:8]):
        # Skip if it's already plotted as a Fibonacci level
        if level in fib_levels:
            continue
        ax_price.axhline(y=level, color='green', linestyle='--', alpha=0.7, linewidth=1)
        ax_price.text(data.index[-1], level, f"{level:.2f}", color='green', ha='right', va='top')
        # Add to volume profile chart too
        ax_vol_profile.axhline(y=level, color='green', linestyle='--', alpha=0.7, linewidth=1)
    
    # Mark current price
    ax_price.axhline(y=results['current_price'], color='blue', linestyle='-', alpha=0.5)
    ax_price.text(data.index[-1], results['current_price'], f"Current: {results['current_price']:.2f}", 
             color='blue', ha='right', va='center', fontweight='bold')
    ax_vol_profile.axhline(y=results['current_price'], color='blue', linestyle='-', alpha=0.5)
    
    # Create separate legends for MAs and Fibonacci levels
    ma_legend_elements = []
    if 'MA_50' in data.columns:
        ma_legend_elements.append(plt.Line2D([0], [0], color='blue', lw=1, label='50-day MA'))
    if 'MA_200' in data.columns:
        ma_legend_elements.append(plt.Line2D([0], [0], color='red', lw=1, label='200-day MA'))
    
    # Create Fibonacci legend elements
    fib_legend_elements = []
    for percentage, color in fibonacci_colors.items():
        fib_legend_elements.append(plt.Line2D([0], [0], color=color, lw=2, label=f'Fib {percentage}'))
    
    # Add MA legend at top left
    if ma_legend_elements:
        first_legend = ax_price.legend(handles=ma_legend_elements, loc='upper left', fontsize=9)
        ax_price.add_artist(first_legend)
    
    # Add Fibonacci legend at bottom right with transparent background
    if fib_legend_elements:
        ax_price.legend(handles=fib_legend_elements, loc='lower right', fontsize=9, 
                      title='Fibonacci Levels', title_fontsize=10, 
                      framealpha=0.8, edgecolor='gray')
    
    ax_price.set_title(f'S&P 500 Technical Levels - {datetime.now().strftime("%Y-%m-%d")}')
    ax_price.set_ylabel('Price')
    ax_price.grid(True, alpha=0.3)
    
    # Share y-axis between charts
    ax_price.set_ylim(min_price, max_price)
    ax_vol_profile.set_ylim(min_price, max_price)
    
    plt.tight_layout()
    
    if save_path:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Chart saved to {save_path}")
    
    plt.show()

def main(ticker="^GSPC", period="1y", include_vix=True, plot=True, output_folder="outputs"):
    """
    Main function to calculate and display technical levels
    
    Parameters:
    ticker (str): Ticker symbol
    period (str): Data period
    include_vix (bool): Whether to include VIX analysis
    plot (bool): Whether to plot the chart
    output_folder (str): Folder to save outputs
    
    Returns:
    str: Formatted output with key levels
    """
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    print(f"Fetching data for {ticker}...")
    data = fetch_market_data(ticker=ticker, period=period)
    
    vix_data = None
    if include_vix:
        print("Fetching VIX data...")
        vix_data = fetch_market_data(ticker="^VIX", period=period)
    
    print("Identifying swing points...")
    # First, identify swing points separately so we can output them
    swing_highs, swing_lows = identify_swing_points(data)
    
    print("Calculating technical levels...")
    # Now calculate all levels using the identified swing points
    results = find_key_technical_levels(data, vix_data, swing_highs, swing_lows)
    
    # Format output
    output = format_levels_output(results)
    print("\n" + output)
    
    # Format swing points output
    swing_points_output = format_swing_points_output(swing_highs, swing_lows)
    
    # Save text output
    date_str = datetime.now().strftime("%Y-%m-%d")
    ticker_clean = ticker.replace('^', '')
    
    # Save main results
    text_file = os.path.join(output_folder, f"{ticker_clean}_levels_{date_str}.txt")
    with open(text_file, 'w') as f:
        f.write(output)
    print(f"Text results saved to {text_file}")
    
    # Save swing points
    swing_file = os.path.join(output_folder, f"{ticker_clean}_swing_points_{date_str}.txt")
    with open(swing_file, 'w') as f:
        f.write(swing_points_output)
    print(f"Swing points saved to {swing_file}")
    
    # Plot chart if requested
    if plot:
        chart_file = os.path.join(output_folder, f"{ticker_clean}_chart_old.png")
        plot_levels(data, results, save_path=chart_file)
    
    return output

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Calculate technical levels for a stock or index')
    parser.add_argument('--ticker', type=str, default='^GSPC', help='Ticker symbol (default: ^GSPC for S&P 500)')
    parser.add_argument('--period', type=str, default='1y', help='Data period (default: 1y)')
    parser.add_argument('--no-vix', action='store_false', dest='include_vix', help='Exclude VIX analysis')
    parser.add_argument('--no-plot', action='store_false', dest='plot', help='Do not display plot')
    parser.add_argument('--output', type=str, default='outputs', help='Output folder for results (default: outputs)')
    
    args = parser.parse_args()
    
    main(ticker=args.ticker, period=args.period, include_vix=args.include_vix, plot=args.plot, output_folder=args.output)