"""
Chart generation for technical analysis visualization.
"""

import os
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from .styling import ChartStyling


class ChartGenerator:
    """Generate charts for technical analysis visualization"""
    
    def __init__(self, data, results, volume_analyzer):
        """
        Initialize chart generator
        
        Parameters:
        data (pandas.DataFrame): OHLC price data
        results (dict): Results from technical level analysis
        volume_analyzer: Volume analyzer instance for profile calculation
        """
        self.data = data
        self.results = results
        self.volume_analyzer = volume_analyzer
        self.styling = ChartStyling()
        
    def plot_levels_chart(self, save_path=None, show=True):
        """
        Plot price chart with technical levels and volume profile
        
        Parameters:
        save_path (str, optional): Path to save the chart
        show (bool): Whether to display the chart
        
        Returns:
        matplotlib.figure.Figure: The figure object
        """
        # Create a figure with gridspec for complex layout
        fig = plt.figure(figsize=(16, 9))
        gs = fig.add_gridspec(1, 5)  # 1 row, 5 columns
        
        # Volume profile on the left (1/5 of the width)
        ax_vol_profile = fig.add_subplot(gs[0, 0])
        # Price chart taking the remaining 4/5
        ax_price = fig.add_subplot(gs[0, 1:])
        
        # Plot volume profile
        self._plot_volume_profile(ax_vol_profile)
        
        # Plot price data
        self._plot_price_data(ax_price)
        
        # Plot technical levels
        self._plot_fibonacci_levels(ax_price, ax_vol_profile)
        self._plot_support_resistance(ax_price, ax_vol_profile)
        self._plot_current_price(ax_price, ax_vol_profile)
        
        # Add legends
        self._add_legends(ax_price)
        
        # Set titles and labels
        title = f'S&P 500 Technical Levels - {datetime.now().strftime("%Y-%m-%d")}'
        ax_price.set_title(title)
        ax_price.set_ylabel('Price')
        ax_price.grid(True, alpha=0.3)
        
        # Link y-axes
        price_range = self._get_price_range()
        ax_price.set_ylim(price_range['min'], price_range['max'])
        ax_vol_profile.set_ylim(price_range['min'], price_range['max'])
        
        plt.tight_layout()
        
        # Debug info
        print("Chart generation:")
        print(f"- Resistance levels to plot: {len(self.results['resistance_levels'])}")
        print(f"- Support levels to plot: {len(self.results['support_levels'])}")
        
        # Save if requested
        if save_path:
            self._save_chart(fig, save_path)
        
        # Show if requested
        if show:
            plt.show()
            
        return fig
        
    def _plot_volume_profile(self, ax):
        """Plot volume profile on the left side of the chart"""
        # Calculate volume profile
        bin_centers, volume, min_price, max_price, bin_size = self.volume_analyzer.calculate_volume_profile()
        
        # Normalize volume for display
        if volume.max() > 0:  # Avoid division by zero
            normalized_volume = volume / volume.max()
        else:
            normalized_volume = volume
        
        # Determine colors based on current price
        current_price = self.results['current_price']
        colors = []
        for center in bin_centers:
            if center <= current_price:
                colors.append(self.styling.COLORS['volume_below'])  # Cyan
            else:
                colors.append(self.styling.COLORS['volume_above'])  # Magenta
        
        # Plot horizontal volume bars
        ax.barh(bin_centers, normalized_volume, height=bin_size*0.8, 
               color=colors, alpha=self.styling.ALPHA['volume_bars'])
        
        # Set labels and styling
        ax.set_title('Volume Profile')
        ax.set_xlabel('Relative Volume')
        ax.grid(True, alpha=0.3)
        
        # Hide y-tick labels (will use price chart's y-axis)
        ax.tick_params(axis='y', which='both', labelleft=False)
        
    def _plot_price_data(self, ax):
        """Plot price data and moving averages"""
        # Plot close price
        ax.plot(self.data.index, self.data['Close'], 
               color=self.styling.COLORS['price_line'], 
               linewidth=self.styling.LINE_WIDTHS['price'],
               label='Price')
        
        # Plot moving averages
        for ma in ['MA_50', 'MA_200']:
            if ma in self.data.columns:
                color_key = 'ma_50' if ma == 'MA_50' else 'ma_200'
                ax.plot(self.data.index, self.data[ma], 
                       color=self.styling.COLORS[color_key],
                       linewidth=self.styling.LINE_WIDTHS['ma'],
                       label=f"{ma.replace('_', '-')}")
    
    def _plot_fibonacci_levels(self, ax_price, ax_vol_profile):
        """Plot Fibonacci retracement levels"""
        # Extract Fibonacci levels from the results
        fib_levels = {}
        
        # Extract Fibonacci levels from resistance and support
        for level_list in [self.results['resistance_levels'], self.results['support_levels']]:
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
        
        # Plot each Fibonacci level
        for level, (percentage, source) in fib_levels.items():
            color = self.styling.get_fibonacci_color(percentage)
            
            # Plot on price chart
            ax_price.axhline(
                y=level, 
                color=color, 
                linestyle=self.styling.LINE_STYLES['fibonacci'],
                alpha=self.styling.ALPHA['fibonacci'],
                linewidth=self.styling.LINE_WIDTHS['fibonacci']
            )
            
            # Add label with background
            ax_price.text(
                self.data.index[0], level, 
                f"Fib {percentage}", 
                color='white', 
                ha='left', 
                va='center',
                fontsize=self.styling.FONT_SIZES['fib_label'],
                fontweight='bold',
                bbox=dict(facecolor=color, alpha=0.8, pad=3)
            )
            
            # Also plot on volume profile
            ax_vol_profile.axhline(
                y=level, 
                color=color, 
                linestyle=self.styling.LINE_STYLES['fibonacci'],
                alpha=self.styling.ALPHA['fibonacci'],
                linewidth=self.styling.LINE_WIDTHS['fibonacci']
            )
    
    def _plot_support_resistance(self, ax_price, ax_vol_profile):
        """Plot support and resistance levels"""
        # Get all Fibonacci levels to avoid duplicate plotting
        fib_levels = {}
        for level_list in [self.results['resistance_levels'], self.results['support_levels']]:
            for level, sources in level_list:
                for source in sources:
                    if 'Fibonacci' in source:
                        fib_levels[level] = True
        
        # Debug information about the levels
        print("Support/Resistance Debug:")
        print(f"Current price: {self.results['current_price']}")
        resistance_count = len(self.results['resistance_levels'])
        support_count = len(self.results['support_levels'])
        print(f"Resistance levels: {resistance_count}, Support levels: {support_count}")
        
        # Plot resistance levels
        for i, (level, sources) in enumerate(self.results['resistance_levels'][:8]):
            # Skip if it's already plotted as a Fibonacci level
            if level in fib_levels:
                continue
                
            print(f"Plotting resistance level: {level}")
            
            ax_price.axhline(
                y=level, 
                color=self.styling.COLORS['resistance'],
                linestyle=self.styling.LINE_STYLES['resistance'],
                alpha=self.styling.ALPHA['resistance'],
                linewidth=self.styling.LINE_WIDTHS['resistance']
            )
            
            ax_price.text(
                self.data.index[-1], level, 
                f"{level:.2f}", 
                color=self.styling.COLORS['resistance'],
                ha='right', 
                va='bottom',
                fontsize=self.styling.FONT_SIZES['annotation']
            )
            
            # Add to volume profile chart too
            ax_vol_profile.axhline(
                y=level, 
                color=self.styling.COLORS['resistance'],
                linestyle=self.styling.LINE_STYLES['resistance'],
                alpha=self.styling.ALPHA['resistance'],
                linewidth=self.styling.LINE_WIDTHS['resistance']
            )
        
        # Plot support levels
        for i, (level, sources) in enumerate(self.results['support_levels'][:8]):
            # Skip if it's already plotted as a Fibonacci level
            if level in fib_levels:
                continue
                
            print(f"Plotting support level: {level}")
            
            ax_price.axhline(
                y=level, 
                color=self.styling.COLORS['support'],
                linestyle=self.styling.LINE_STYLES['support'],
                alpha=self.styling.ALPHA['support'],
                linewidth=self.styling.LINE_WIDTHS['support']
            )
            
            ax_price.text(
                self.data.index[-1], level, 
                f"{level:.2f}", 
                color=self.styling.COLORS['support'],
                ha='right', 
                va='top',
                fontsize=self.styling.FONT_SIZES['annotation']
            )
            
            # Add to volume profile chart too
            ax_vol_profile.axhline(
                y=level, 
                color=self.styling.COLORS['support'],
                linestyle=self.styling.LINE_STYLES['support'],
                alpha=self.styling.ALPHA['support'],
                linewidth=self.styling.LINE_WIDTHS['support']
            )
    
    def _plot_current_price(self, ax_price, ax_vol_profile):
        """Plot current price marker"""
        current_price = self.results['current_price']
        
        # Plot on price chart
        ax_price.axhline(
            y=current_price, 
            color=self.styling.COLORS['current_price'],
            linestyle=self.styling.LINE_STYLES['current_price'],
            alpha=self.styling.ALPHA['current_price'],
            linewidth=self.styling.LINE_WIDTHS['current_price']
        )
        
        ax_price.text(
            self.data.index[-1], current_price, 
            f"Current: {current_price:.2f}", 
            color=self.styling.COLORS['current_price'],
            ha='right', 
            va='center', 
            fontweight='bold',
            fontsize=self.styling.FONT_SIZES['annotation']
        )
        
        # Plot on volume profile
        ax_vol_profile.axhline(
            y=current_price, 
            color=self.styling.COLORS['current_price'],
            linestyle=self.styling.LINE_STYLES['current_price'],
            alpha=self.styling.ALPHA['current_price'],
            linewidth=self.styling.LINE_WIDTHS['current_price']
        )
    
    def _add_legends(self, ax_price):
        """Add legends to the plot"""
        # Create separate legends for MAs and Fibonacci levels
        ma_legend_elements = []
        if 'MA_50' in self.data.columns:
            ma_legend_elements.append(plt.Line2D(
                [0], [0], 
                color=self.styling.COLORS['ma_50'], 
                lw=self.styling.LINE_WIDTHS['ma'], 
                label='50-day MA'
            ))
            
        if 'MA_200' in self.data.columns:
            ma_legend_elements.append(plt.Line2D(
                [0], [0], 
                color=self.styling.COLORS['ma_200'], 
                lw=self.styling.LINE_WIDTHS['ma'], 
                label='200-day MA'
            ))
        
        # Create Fibonacci legend elements
        fib_legend_elements = []
        fib_percentages = ['0%', '23.6%', '38.2%', '50%', '61.8%', '78.6%', '100%']
        
        for percentage in fib_percentages:
            color = self.styling.get_fibonacci_color(percentage)
            fib_legend_elements.append(plt.Line2D(
                [0], [0], 
                color=color, 
                lw=self.styling.LINE_WIDTHS['fibonacci'], 
                label=f'Fib {percentage}'
            ))
        
        # Add MA legend at top left
        if ma_legend_elements:
            first_legend = ax_price.legend(
                handles=ma_legend_elements, 
                loc='upper left', 
                fontsize=self.styling.FONT_SIZES['legend']
            )
            ax_price.add_artist(first_legend)
        
        # Add Fibonacci legend at bottom right with transparent background
        if fib_legend_elements:
            ax_price.legend(
                handles=fib_legend_elements, 
                loc='lower right', 
                fontsize=self.styling.FONT_SIZES['legend'],
                title='Fibonacci Levels', 
                title_fontsize=self.styling.FONT_SIZES['legend']+1,
                framealpha=self.styling.ALPHA['legend'], 
                edgecolor='gray'
            )
    
    def _get_price_range(self):
        """Get the price range for the chart"""
        min_price = self.data['Low'].min()
        max_price = self.data['High'].max()
        
        # Add some padding
        padding = (max_price - min_price) * 0.05
        
        return {
            'min': min_price - padding,
            'max': max_price + padding
        }
    
    def _save_chart(self, fig, save_path):
        """Save the chart to file"""
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Save with high resolution
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Chart saved to {save_path}")