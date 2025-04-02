# S&P 500 Technical Levels Calculator

This Python tool automatically calculates key technical levels for the S&P 500 index (or any other stock/index) using multiple technical analysis methods. It generates both text output of important support and resistance levels and visual charts with volume profile analysis.

![S&P 500 Technical Analysis](example_output.png)

## Features

- **Multi-Method Technical Analysis**:
  - Volume Profile Analysis
  - Fibonacci Retracements (with color-coded visualization)
  - Moving Averages (50-day, 200-day)
  - Price Action Support/Resistance
  - Psychological Round Numbers
  - VIX (Volatility) Analysis

- **Consolidated Level Identification**:
  - Combines multiple technical factors to find the most significant levels
  - Ranks levels by strength (number of confluent factors)
  - Groups nearby levels to reduce noise

- **Comprehensive Output**:
  - Text report with detailed level information
  - Chart visualization with volume profile
  - Color-coded Fibonacci levels with percentage labels
  - Support and resistance levels displayed with strength indicators

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/spx-technical-levels.git
   cd spx-technical-levels
   ```

2. Install the required packages:
   ```bash
   pip install pandas numpy yfinance matplotlib scipy
   ```

## Usage

### Basic Usage

Run the script with default settings (S&P 500, 1-year period):

```bash
python spx_levels.py
```

### Command-Line Options

```bash
python spx_levels.py --ticker="^GSPC" --period="6mo" --output="my_analysis"
```

Available options:
- `--ticker`: Stock/index symbol (default: `^GSPC` for S&P 500)
- `--period`: Data period (default: `1y`, options: `1d`, `5d`, `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y`, `10y`, `ytd`, `max`)
- `--no-vix`: Exclude VIX analysis
- `--no-plot`: Do not display plot
- `--output`: Output folder for results (default: `outputs`)

### Output

The script generates:

1. **Text file** with key levels and their sources:
   ```
   Technical Levels Report - 2025-04-02
   Current Price: 5633.06

   VIX Analysis: VIX below 20-day average - favorable for upside targets.

   Resistance Levels:
   5660.00 **** - Round number (100s), Fibonacci 78.6% (Fib_Up_2)
   5645.00 *** - Previous swing high, Round number (50s)
   5635.00 *** - Target level (needs lower VIX), Fibonacci 61.8% (Fib_Up_1)
   5600.00 ***** - Key level (round number + high volume), Volume cluster

   Support Levels:
   5577.00 **** - Stronger support (previous consolidation), Volume cluster
   5550.00 **** - Support (round number + volume), MA_50 support/resistance
   5524.00 *** - Support (previous consolidation)
   5515.00 *** - Support (Fibonacci 50%), Recent price action
   5504.00 ***** - Key support (major swing low + volume), Volume cluster
   5480.00 ** - Support (Fibonacci 61.8%)

   Strength Indicator: * (weak) to ***** (very strong)
   ```

2. **Swing points file** detailing all the swing highs and lows used for Fibonacci calculations:
   ```
   Swing Points Analysis - 2025-04-02
   ============================================================

   SWING HIGHS (used for Fibonacci calculations)
   ------------------------------------------------------------
   2025-03-15: 5750.25
   2025-02-20: 6120.45
   2025-01-10: 6150.80
   ...

   SWING LOWS (used for Fibonacci calculations)
   ------------------------------------------------------------
   2025-03-25: 5480.15
   2025-02-05: 5700.30
   2025-01-03: 5550.60
   ...

   Note: Fibonacci retracements are calculated using combinations
   of these swing highs and lows, prioritizing recent swings.
   ```

3. **Chart visualization** showing:
   - Price chart with moving averages
   - Volume profile on left side
   - Support and resistance levels with labels
   - Color-coded Fibonacci retracement levels (0%, 23.6%, 38.2%, 50%, 61.8%, 78.6%, 100%)
   - Current price marker

All files are saved to the specified output folder (default: `outputs`).

## Methodology

### Level Calculation

1. **Volume Profile**:
   - Analyzes price zones with highest trading volume
   - More trading activity = stronger support/resistance

2. **Fibonacci Retracements**:
   - Calculates standard Fibonacci levels (23.6%, 38.2%, 50%, 61.8%, 78.6%)
   - Uses multiple swing high/low pairs for redundancy
   - Visually distinguishes Fibonacci levels with color-coding by percentage
   - Labels each level directly on the chart

3. **Moving Averages**:
   - 50-day and 200-day moving averages as dynamic support/resistance

4. **Price Action Analysis**:
   - Identifies significant swing points from recent history
   - Finds local support/resistance from recent price behavior

5. **Psychological Levels**:
   - Round numbers (5600, 5550, etc.)
   - Quarter levels (5525, 5575, etc.) near current price

6. **VIX Analysis**:
   - Compares current VIX (volatility index) value to its 20-day moving average
   - Provides context on market volatility conditions
   - When VIX is below its 20-day average: Indicates decreasing volatility, favorable for upside targets
   - When VIX is above its 20-day average: Indicates elevated volatility, may need to decrease for upside price targets
   - Helps determine the likelihood of breaking support or reaching resistance levels
   - Integrates volatility context with price levels for more comprehensive analysis

### Level Strength Assessment

Levels are ranked by the number of technical factors that converge on that price point:
- Volume clusters get extra weight
- Price action levels get extra weight
- Multiple Fibonacci confluences get extra weight

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Technical analysis concepts from various sources including technical traders and market analysts
- Built using yfinance for data retrieval

## Disclaimer

This tool is for informational purposes only. It is not financial advice, and no investment decisions should be made based solely on its outputs. Trading involves risk, and past performance is not indicative of future results.