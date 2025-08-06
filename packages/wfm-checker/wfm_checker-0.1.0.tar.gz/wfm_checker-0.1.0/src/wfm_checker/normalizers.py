"""
Item name normalization functions.

This module contains functions to normalize item names for Warframe Market API compatibility.
"""

from typing import Tuple, Optional
from .constants import SPECIAL_CASES, EXCEPTIONS, WARFRAMES, AYATAN_SCULPTURES


def normalize_item_name(item_name: str) -> str:
    """
    Normalizes the item name to match the Warframe Market API's expected format.
    
    Args:
        item_name: Raw item name to normalize
        
    Returns:
        Normalized item name suitable for API calls
    """
    item_name = item_name.lower().strip()

    if item_name in SPECIAL_CASES:
        return SPECIAL_CASES[item_name]

    # Normalizer for most items
    item_name = (
        item_name
        .replace("&", "and")
        .replace(".", "")
        .replace("-", "_")
        .replace(" ", "_")
        .replace("'", "")
        .replace("orokin", "corrupted")
        .replace("bp", "blueprint")
    )

    # Check item suffixes and add blueprint if necessary
    if (item_name.endswith(('_systems', '_chassis', "_harness", "_wings")) or 
        any(item_name.endswith(warframe) for warframe in WARFRAMES)) and item_name not in EXCEPTIONS:
        item_name += '_blueprint'

    return item_name


def get_ayatan_star_data(item_name: str) -> Tuple[Optional[int], Optional[int]]:
    """
    Returns the maximum star counts for Ayatan sculptures.
    
    This is used to check if a sculpture has the maximum number of stars
    (fully socketed) versus an empty sculpture when fetching prices.
    
    Args:
        item_name: Item name to check for Ayatan sculpture data
        
    Returns:
        Tuple of (max_amber_stars, max_cyan_stars) or (None, None) if not an Ayatan sculpture
    """
    normalized_name = normalize_item_name(item_name)
    
    if normalized_name in AYATAN_SCULPTURES:
        return AYATAN_SCULPTURES[normalized_name]
    
    return None, None  # Not an Ayatan sculpture
