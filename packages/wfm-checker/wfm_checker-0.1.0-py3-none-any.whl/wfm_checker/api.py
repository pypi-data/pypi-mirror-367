"""
Warframe Market API interaction functions.

This module contains functions to fetch item prices from the Warframe Market API
using both listings and statistics endpoints.
"""

import requests
from typing import Optional
from .normalizers import normalize_item_name, get_ayatan_star_data


def find_max_rank_in_statistics(item_name: str) -> Optional[int]:
    """
    Find the highest available rank for an item in statistics data.
    
    Args:
        item_name: Name of the item to check
        
    Returns:
        Highest rank found, or None if no ranked data available
    """
    url_name = normalize_item_name(item_name)
    api_url = f"https://api.warframe.market/v1/items/{url_name}/statistics"

    headers = {
        'accept': 'application/json',
        'platform': 'pc',
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()

        if 'payload' not in data or 'statistics_closed' not in data['payload']:
            return None
            
        stats_closed = data['payload']['statistics_closed']
        
        if '48hours' not in stats_closed or not stats_closed['48hours']:
            return None
            
        # Find the highest rank that has data
        max_rank = 0
        for entry in stats_closed['48hours']:
            if entry.get('mod_rank', 0) > max_rank:
                max_rank = entry['mod_rank']
        
        return max_rank if max_rank > 0 else None
    except Exception as e:
        print(f"Error finding max rank for '{item_name}': {e}")
        return None


def get_item_price_stat(item_name: str, price_method: str = 'median', rank: int = 0, 
                       amber_stars: Optional[int] = None, cyan_stars: Optional[int] = None) -> Optional[float]:
    """
    Fetches the most recent closed price from the statistics API.
    
    Args:
        item_name: Name of the item to fetch price for
        price_method: Price calculation method ('minimum' or 'median')
        rank: Rank/level of the item (for mods only, mutually exclusive with stars)
        amber_stars: Number of amber stars (for Ayatan sculptures, optional)
        cyan_stars: Number of cyan stars (for Ayatan sculptures, optional)
        
    Returns:
        Price as float or None if not found/error
    """
    url_name = normalize_item_name(item_name)
    api_url = f"https://api.warframe.market/v1/items/{url_name}/statistics"

    headers = {
        'accept': 'application/json',
        'platform': 'pc',
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()

        # Get the statistics_closed data
        if 'payload' not in data or 'statistics_closed' not in data['payload']:
            print(f"No statistics data available for '{item_name}'")
            return None
            
        stats_closed = data['payload']['statistics_closed']
        
        # Get the 48hours data (most recent timeframe)
        if '48hours' not in stats_closed or not stats_closed['48hours']:
            print(f"No 48-hour statistics available for '{item_name}'")
            return None
            
        closed_data = stats_closed['48hours']
        
        # Filter by rank/stars if specified
        has_mod_rank_data = any('mod_rank' in entry for entry in closed_data)
        has_cyan_stars_data = any('cyan_stars' in entry for entry in closed_data)
        has_amber_stars_data = any('amber_stars' in entry for entry in closed_data)
        
        if has_cyan_stars_data or has_amber_stars_data:
            # Handle Ayatan sculptures with star specifications
            if amber_stars is not None or cyan_stars is not None:
                # User specified star configuration
                target_amber = amber_stars if amber_stars is not None else 0
                target_cyan = cyan_stars if cyan_stars is not None else 0
                
                star_filtered_data = []
                for entry in closed_data:
                    entry_cyan = entry.get('cyan_stars', 0)
                    entry_amber = entry.get('amber_stars', 0)
                    if entry_cyan == target_cyan and entry_amber == target_amber:
                        star_filtered_data.append(entry)
                
                if star_filtered_data:
                    closed_data = star_filtered_data
                else:
                    print(f"No data available for '{item_name}' with {target_amber} amber and {target_cyan} cyan stars")
                    return None
            else:
                # Auto-detect Ayatan sculpture and use max stars OR 0 stars logic
                target_amber, target_cyan = get_ayatan_star_data(item_name)
                
                if target_amber is not None and target_cyan is not None:
                    # For Ayatan sculptures, only use max stars OR 0 stars (treat anything else as 0)
                    max_star_data = []
                    zero_star_data = []
                    
                    for entry in closed_data:
                        entry_cyan = entry.get('cyan_stars', 0)
                        entry_amber = entry.get('amber_stars', 0)
                        
                        # Check for max stars (fully socketed)
                        if entry_cyan == target_cyan and entry_amber == target_amber:
                            max_star_data.append(entry)
                        # Treat everything else as 0 stars (empty sculpture pricing)
                        else:
                            # Modify the entry to have 0 stars for pricing consistency
                            entry_copy = entry.copy()
                            entry_copy['cyan_stars'] = 0
                            entry_copy['amber_stars'] = 0
                            zero_star_data.append(entry_copy)

                    # Prefer max star data, otherwise use all non-max as 0 star data
                    if max_star_data:
                        closed_data = max_star_data
                    elif zero_star_data:
                        print(f"No max star data for '{item_name}', treating all other star configurations as empty sculpture")
                        closed_data = zero_star_data
                    else:
                        print(f"No suitable star data available for '{item_name}'")
                        return None
                
        elif has_mod_rank_data and rank > 0:
            # For mods with specific rank requested
            rank_filtered_data = [
                entry for entry in closed_data 
                if 'mod_rank' in entry and entry['mod_rank'] == rank
            ]
            if not rank_filtered_data:
                print(f"No rank {rank} data available for mod '{item_name}'")
                return None
            closed_data = rank_filtered_data
        elif has_mod_rank_data and rank == -1:
            # For mods with MAX rank requested - find highest available rank
            max_rank = find_max_rank_in_statistics(item_name)
            if max_rank is not None and max_rank > 0:
                print(f"Using max rank {max_rank} for '{item_name}'")
                rank_filtered_data = [
                    entry for entry in closed_data 
                    if 'mod_rank' in entry and entry['mod_rank'] == max_rank
                ]
                if not rank_filtered_data:
                    print(f"No rank {max_rank} data available for mod '{item_name}'")
                    return None
                closed_data = rank_filtered_data
            else:
                print(f"No ranked data available for mod '{item_name}'")
                return None
        elif has_mod_rank_data and rank == 0:
            # For mods with rank 0 (unranked)
            unranked_data = [
                entry for entry in closed_data 
                if 'mod_rank' in entry and entry['mod_rank'] == 0
            ]
            if unranked_data:
                closed_data = unranked_data
            # If no rank 0 data, use all data (fallback)

        if not closed_data:
            print(f"No suitable data found for '{item_name}' with rank {rank}")
            return None
        
        # Sort by datetime to get the most recent entry
        closed_data.sort(key=lambda x: x['datetime'], reverse=True)
        most_recent = closed_data[0]
        
        # Return the appropriate price based on method
        if price_method == 'minimum':
            return most_recent.get('min_price')
        else:  # median (default)
            return most_recent.get('median')
            
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"Item '{item_name}' not found in Warframe Market")
        else:
            print(f"HTTP Error {e.response.status_code} for '{item_name}': {e}")
        return None
    except Exception as e:
        print(f"Error fetching statistics for '{item_name}': {e}")
        return None


def get_item_price(item_name: str, price_method: str = 'median', rank: int = 0,
                   amber_stars: Optional[int] = None, cyan_stars: Optional[int] = None) -> Optional[float]:
    """
    Fetches the price of the given item from the Warframe Market API listings.
    Supports rank filtering for mods and star filtering for Ayatan sculptures.
    
    Args:
        item_name: Name of the item to fetch price for
        price_method: Price calculation method ('minimum' or 'median')
        rank: Rank/level of the item (for mods only, mutually exclusive with stars)
        amber_stars: Number of amber stars (for Ayatan sculptures, optional)
        cyan_stars: Number of cyan stars (for Ayatan sculptures, optional)
        
    Returns:
        Price as float or None if not found/error
    """
    url_name = normalize_item_name(item_name)
    api_url = f"https://api.warframe.market/v1/items/{url_name}/orders"

    headers = {
        'accept': 'application/json',
        'platform': 'pc',
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()

        orders = data['payload']['orders']
        
        # Apply filtering based on item type
        def item_filter(order):
            # Handle star filtering for Ayatan sculptures
            if amber_stars is not None or cyan_stars is not None:
                target_amber = amber_stars if amber_stars is not None else 0
                target_cyan = cyan_stars if cyan_stars is not None else 0
                return (order.get('amber_stars', 0) == target_amber and 
                        order.get('cyan_stars', 0) == target_cyan)
            
            # Handle rank filtering for mods
            if rank == 0:
                # For rank 0, include unranked mods and non-mods
                return 'mod_rank' not in order or order['mod_rank'] == 0
            else:
                # For specific ranks, only include matching mods
                return 'mod_rank' in order and order['mod_rank'] == rank
        
        # For minimum prices
        if price_method == 'minimum':
            # Filter for online sellers matching criteria
            online_orders = [
                order for order in orders 
                if order['order_type'] == 'sell' and 
                order['user']['status'] == 'ingame' and
                item_filter(order)
            ]
            
            if online_orders:
                min_price = min(order['platinum'] for order in online_orders)
                return min_price
            else:
                # Fallback to all sell orders with filter
                all_sell_orders = [
                    order for order in orders 
                    if order['order_type'] == 'sell' and
                    item_filter(order)
                ]
                if all_sell_orders:
                    min_price = min(order['platinum'] for order in all_sell_orders)
                    return min_price
                else:
                    return None
                    
        # For median prices
        else:
            # Collect all valid sell orders with quantity expansion
            all_prices = []
            for order in orders:
                if (
                    order['order_type'] == 'sell' and 
                    order['user']['status'] == 'ingame' and
                    item_filter(order)):
                    
                    # Add price for each available item in the order
                    all_prices.extend([order['platinum']] * order['quantity'])
                
            if all_prices:
                # Calculate true quantity-weighted median
                sorted_prices = sorted(all_prices)
                n = len(sorted_prices)
                
                if n % 2 == 1:
                    # Odd number of items
                    median_price = sorted_prices[n//2]
                else:
                    # Even number of items
                    median_price = (sorted_prices[n//2 - 1] + sorted_prices[n//2]) / 2
                
                return median_price
            else:
                # Fallback to minimum price among all sell orders
                sell_orders = [
                    order for order in orders 
                    if order['order_type'] == 'sell' and
                    item_filter(order)
                ]
                if sell_orders:
                    min_price = min(order['platinum'] for order in sell_orders)
                    return min_price
                else:
                    return None
    except Exception as e:
        print(f"Error fetching price for '{item_name}': {e}")
        return None
