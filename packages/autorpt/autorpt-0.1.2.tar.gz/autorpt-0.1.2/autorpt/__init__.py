"""Top-level package for autorpt."""

__author__ = """Vance Russell"""
__email__ = 'vance@3point.xyz'
__version__ = '0.1.2'

# Import main functionality for easy access
from .autorpt import ReportGenerator, main

# Make it easy to use the package
def generate_report(excel_file='budget.xlsx', output_file=None):
    """
    Generate an automated budget report.
    
    Args:
        excel_file (str): Path to the Excel budget file (default: 'budget.xlsx')
        output_file (str): Output Word document filename (optional)
    
    Returns:
        bool: True if successful, False otherwise
    """
    generator = ReportGenerator(excel_file, output_file)
    return generator.generate_report()
