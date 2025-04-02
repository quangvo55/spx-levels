from setuptools import setup, find_packages

setup(
    name="spx_levels",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "numpy", 
        "yfinance",
        "matplotlib",
        "scipy"
    ],
    entry_points={
        'console_scripts': [
            'spx-levels=spx_levels.main:main',
        ],
    },
    author="James Vo",
    author_email="james.quang.vo@gmail.com",
    description="A tool for calculating key technical levels for market analysis",
    keywords="trading, technical analysis, finance, S&P 500",
    python_requires=">=3.7",
)