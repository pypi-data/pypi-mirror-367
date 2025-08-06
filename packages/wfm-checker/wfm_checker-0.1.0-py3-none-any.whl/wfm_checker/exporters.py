"""
Export functions for writing data to various formats.

This module contains functions to export processed item data to Excel files.
"""

import openpyxl
from typing import List, Dict, Any
from .api import get_item_price, get_item_price_stat
from .normalizers import get_ayatan_star_data


def write_to_excel(items: List[Dict[str, Any]], output_file: str, 
                   price_method: str = 'median', api_method: str = 'statistics') -> None:
    """
    Writes item data to Excel with clean rank display.
    
    For Ayatan sculptures, shows 'EMPTY' or 'FULL' in rank column instead of star counts.
    
    Args:
        items: List of dictionaries containing item data
        output_file: Path to output Excel file
        price_method: Price calculation method ('minimum' or 'median')
        api_method: API endpoint to use ('listings' or 'statistics')
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Warframe Market Prices"

    # Write headers - simplified without star columns
    headers = ['Quantity', 'Item', 'Rank', 'Item Value', 'Total Value']
    ws.append(headers)

    total_sum = 0

    for item in items:
        quantity = item['quantity']
        item_name = item['item_name']
        rank = item['rank']
        amber_stars = item['amber_stars']
        cyan_stars = item['cyan_stars']
        
        # Determine rank display value and pricing strategy
        if rank > 0:
            # This is a mod with a specific rank
            rank_display = rank
            if api_method == 'listings':
                price = get_item_price(item_name, price_method, rank=rank)
            else:  # statistics (default)
                price = get_item_price_stat(item_name, price_method, rank=rank)
        elif rank == -1:
            # This is a mod with MAX rank requested
            rank_display = "MAX"
            if api_method == 'listings':
                # For listings, we can't easily find max rank, so use default
                price = get_item_price(item_name, price_method)
            else:  # statistics (default)
                price = get_item_price_stat(item_name, price_method, rank=rank)
        elif amber_stars is not None or cyan_stars is not None:
            # This is an Ayatan sculpture with specified star configuration
            # Get the maximum star configuration for this sculpture
            max_amber, max_cyan = get_ayatan_star_data(item_name)
            
            # Only show "FULL" if it has the maximum star configuration
            if (max_amber is not None and max_cyan is not None and 
                amber_stars == max_amber and cyan_stars == max_cyan):
                rank_display = "FULL"
            else:
                rank_display = "EMPTY"
            
            if api_method == 'listings':
                price = get_item_price(item_name, price_method, amber_stars=amber_stars, cyan_stars=cyan_stars)
            else:  # statistics (default)
                price = get_item_price_stat(item_name, price_method, amber_stars=amber_stars, cyan_stars=cyan_stars)
        else:
            # Regular item or Ayatan sculpture (use auto-detection)
            rank_display = rank if rank > 0 else ""
            if api_method == 'listings':
                price = get_item_price(item_name, price_method)
            else:  # statistics (default)
                price = get_item_price_stat(item_name, price_method)
        
        total_value = quantity * price if price is not None else None
        row = [quantity, item_name, rank_display, price, total_value]
        ws.append(row)

        # Accumulate the total if the value is available
        if total_value is not None:
            total_sum += total_value

    # Append the total row
    total_row = ['', 'Total', '', '', total_sum]
    ws.append(total_row)

    wb.save(output_file)
    print(f"Data written to {output_file}")
