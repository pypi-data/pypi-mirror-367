"""
Command-line interface for the WFM Checker package.

This module provides the CLI entry point for the wfm-checker command.
"""

import argparse
import sys
from .parsers import parse_input
from .exporters import write_to_excel


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Warframe Market Price Calculator'
    )
    
    parser.add_argument('-i', '--input', 
                        default='input.txt',
                        help='Input file (TXT, CSV, or XLSX)')
    parser.add_argument('-o', '--output', 
                        default='output.xlsx',
                        help='Output Excel file')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-l', '--listings', 
                        action='store_true',
                        help='Use listings (orders) API')
    group.add_argument('-s', '--statistics', 
                        action='store_true',
                        help='Use statistics API (default)')
    group2 = parser.add_mutually_exclusive_group()
    group2.add_argument('-m', '--minimum', 
                       action='store_true',
                       help='Use minimum prices')
    group2.add_argument('-M', '--median', 
                       action='store_true',
                       help='Use median prices (default)')
    
    args = parser.parse_args()
    
    price_method = 'minimum' if args.minimum else 'median'
    api_method = 'listings' if args.listings else 'statistics'
    
    try:
        print(f"Processing input file: {args.input}")
        items = parse_input(args.input)
        
        if api_method == 'listings':
            print(f"Found {len(items)} items, fetching {price_method} prices using orders API...")
        else:
            print(f"Found {len(items)} items, fetching {price_method} prices using statistics API...")
        
        write_to_excel(items, args.output, price_method, api_method)
        print("Operation completed successfully!")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
