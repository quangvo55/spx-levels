"""
File output handling for saving analysis results.
"""

import os
from datetime import datetime


class FileOutput:
    """Handle saving output files to disk"""
    
    def __init__(self, output_folder="outputs"):
        """
        Initialize file output handler
        
        Parameters:
        output_folder (str): Folder to save outputs to
        """
        self.output_folder = output_folder
        self._ensure_output_folder()
    
    def _ensure_output_folder(self):
        """Create output folder if it doesn't exist"""
        os.makedirs(self.output_folder, exist_ok=True)
    
    def save_text(self, content, filename, ticker=None, date_str=None):
        """
        Save text content to file
        
        Parameters:
        content (str): Content to save
        filename (str): Base filename
        ticker (str, optional): Ticker symbol to include in filename
        date_str (str, optional): Date string to include in filename
        
        Returns:
        str: Path to saved file
        """
        if ticker:
            ticker_clean = ticker.replace('^', '')
            filename = f"{ticker_clean}_{filename}"
        
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")
            
        full_filename = f"{filename}_{date_str}.txt"
        file_path = os.path.join(self.output_folder, full_filename)
        
        with open(file_path, 'w') as f:
            f.write(content)
            
        print(f"Saved to {file_path}")
        return file_path
    
    def save_levels_text(self, content, ticker=None, date_str=None):
        """Save levels analysis text"""
        return self.save_text(content, "levels", ticker, date_str)
    
    def save_swing_points_text(self, content, ticker=None, date_str=None):
        """Save swing points analysis text"""
        return self.save_text(content, "swing_points", ticker, date_str)
    
    def get_chart_path(self, ticker=None, date_str=None):
        """
        Get path for saving chart
        
        Parameters:
        ticker (str, optional): Ticker symbol to include in filename
        date_str (str, optional): Date string to include in filename
        
        Returns:
        str: Path for chart
        """
        filename = "chart"
        
        if ticker:
            ticker_clean = ticker.replace('^', '')
            filename = f"{ticker_clean}_{filename}"
        
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")
            
        full_filename = f"{filename}_{date_str}.png"
        return os.path.join(self.output_folder, full_filename)