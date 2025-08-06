# WFM Checker Package

A Python package for retrieving and managing Warframe Market item prices with support for multiple input formats and advanced features like Ayatan sculpture star configurations.

## Features

- **Multiple Input Formats**: Supports TXT, CSV, and XLSX files
- **Flexible Pricing**: Access both statistics and listings APIs
- **Mod Ranking**: Handles ranked mods with proper pricing
- **Ayatan Sculptures**: Smart handling of star configurations (max stars vs empty)
- **Excel Export**: Export results with price calculations
- **CLI Interface**: Command-line tool for quick operations
- **Comprehensive API**: Clean Python API for integration

## Installation

```bash
pip install wfm-checker
```

## Quick Start

### Python API

```python
from wfm_checker import get_item_price_stat, parse_input, write_to_excel

# Get a basic item price
price = get_item_price_stat("ash prime systems")
print(f"Ash Prime Systems: {price} platinum")

# Get price for a ranked mod
mod_price = get_item_price_stat("primed continuity", rank=10)
print(f"Primed Continuity R10: {mod_price} platinum")

# Get Ayatan sculpture prices with star configurations
# Max stars configuration
max_price = get_item_price_stat("anasa ayatan sculpture", amber_stars=3, cyan_stars=1)
# Empty (no stars) configuration  
empty_price = get_item_price_stat("anasa ayatan sculpture", amber_stars=0, cyan_stars=0)

# Parse an input file and export to Excel (clean format)
items = parse_input("my_inventory.csv")  # Supports CSV/XLSX with star columns
write_to_excel(items, "prices.xlsx")    # Excel shows EMPTY/FULL for sculptures
```

### Command Line

```bash
# Basic usage
wfm-checker input.txt output.xlsx

# Use listings API instead of statistics
wfm-checker input.txt output.xlsx --api-method listings

# Use minimum price instead of median
wfm-checker input.txt output.xlsx --price-method minimum
```

## Input File Formats

### TXT Format

```txt
2 ash prime systems
1 primed continuity r10
5 anasa ayatan sculpture
```

### CSV Format

```csv
Quantity,Item,Rank,Amber Stars,Cyan Stars
2,ash prime systems,0,,
1,primed continuity,10,,
1,primed continuity,MAX,,
5,anasa ayatan sculpture,,FULL,
3,anasa ayatan sculpture,,EMPTY,
```

### XLSX Format

Excel files with columns for:

- **Quantity**: Number of items
- **Item**: Item name  
- **Rank**: Mod rank (0 for non-mods, MAX for highest available rank)
- **Amber Stars**: For Ayatan sculptures (FULL/EMPTY or specific numbers)
- **Cyan Stars**: For Ayatan sculptures (FULL/EMPTY or specific numbers)

## API Reference

### Core Functions

#### `get_item_price_stat(item_name, price_method='median', rank=0, amber_stars=None, cyan_stars=None)`

Get item price from the statistics API.

**Parameters:**

- `item_name` (str): Name of the item
- `price_method` (str): 'median' or 'minimum' price calculation
- `rank` (int): Mod rank (0 for non-mods)
- `amber_stars` (int, optional): Number of amber stars for Ayatan sculptures
- `cyan_stars` (int, optional): Number of cyan stars for Ayatan sculptures

**Returns:** Price in platinum or None if not found

#### `get_item_price(item_name, price_method='median', rank=0, amber_stars=None, cyan_stars=None)`

Get item price from the listings API (similar parameters as above).

#### `parse_input(file_path)`

Parse input file and return list of item dictionaries.

**Parameters:**

- `file_path` (str): Path to input file (TXT, CSV, or XLSX)

**Returns:** List of dictionaries with keys: quantity, item_name, rank, amber_stars, cyan_stars

#### `write_to_excel(items, output_file, price_method='median', api_method='statistics')`

Export items with price calculations to Excel.

**Parameters:**

- `items`: List of item dictionaries from parse_input()
- `output_file` (str): Output Excel file path
- `price_method` (str): 'median' or 'minimum'
- `api_method` (str): 'statistics' or 'listings'

**Excel Output Format:**

- **Quantity** | **Item** | **Rank** | **Item Value** | **Total Value**
- For mods: Rank shows the actual rank number (e.g., "10") or "MAX" for highest available
- For Ayatan sculptures: Rank shows "EMPTY" (not max stars) or "FULL" (max stars)
- For regular items: Rank is blank

## Advanced Examples

### Portfolio Analysis

```python
from wfm_checker import parse_input, get_item_price_stat, write_to_excel

def analyze_portfolio(input_file):
    # Parse inventory
    items = parse_input(input_file)
    
    total_value = 0
    high_value_items = []
    
    for item in items:
        quantity = item['quantity']
        item_name = item['item_name']
        rank = item['rank']
        amber_stars = item['amber_stars']
        cyan_stars = item['cyan_stars']
        
        # Get price with proper parameter handling
        if rank > 0:
            price = get_item_price_stat(item_name, rank=rank)
        elif amber_stars is not None or cyan_stars is not None:
            price = get_item_price_stat(item_name, amber_stars=amber_stars, cyan_stars=cyan_stars)
        else:
            price = get_item_price_stat(item_name)
        
        if price:
            item_value = quantity * price
            total_value += item_value
            
            if price > 50:  # High-value items
                high_value_items.append((item_name, price, quantity))
    
    print(f"Portfolio total value: {total_value} platinum")
    print(f"High-value items: {len(high_value_items)}")
    
    # Export to Excel
    write_to_excel(items, "portfolio_analysis.xlsx")
    
    return total_value, high_value_items

# Usage
total, high_value = analyze_portfolio("my_inventory.csv")
```

### Ayatan Sculpture Comparison

```python
def compare_ayatan_prices(sculpture_name):
    """Compare prices between max stars and empty configurations."""
    
    # Get max star configuration for this sculpture
    from wfm_checker.normalizers import get_ayatan_star_data
    max_amber, max_cyan = get_ayatan_star_data(sculpture_name)
    
    if max_amber is not None:
        # Get max stars price
        max_price = get_item_price_stat(
            sculpture_name, 
            amber_stars=max_amber, 
            cyan_stars=max_cyan
        )
        
        # Get empty price
        empty_price = get_item_price_stat(
            sculpture_name, 
            amber_stars=0, 
            cyan_stars=0
        )
        
        print(f"{sculpture_name}:")
        print(f"  Max stars ({max_amber}A/{max_cyan}C): {max_price} platinum")
        print(f"  Empty (0A/0C): {empty_price} platinum")
        
        if max_price and empty_price:
            profit = max_price - empty_price
            print(f"  Profit from stars: {profit} platinum")
    
    return max_price, empty_price

# Compare all Ayatan sculptures
sculptures = ["anasa ayatan sculpture", "arbitrations ayatan sculpture", "orta ayatan sculpture"]
for sculpture in sculptures:
    compare_ayatan_prices(sculpture)
```

## Error Handling

The package includes comprehensive error handling:

- **API Errors**: Network issues and API failures are caught and logged
- **File Parsing**: Invalid file formats return helpful error messages  
- **Item Validation**: Unknown items return None values instead of crashing
- **Rate Limiting**: Built-in delays prevent API rate limit issues

## Testing

Run the test suite:

```bash
pytest tests/
```

The package includes unit tests for all major components and integration tests for end-to-end workflows.

## Installation from PyPI

```bash
pip install wfm-checker
```

## Support

For questions or issues, please refer to the package documentation on PyPI or contact: <godlyschnoz@gmail.com>

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Changelog

### Version 1.0.0

- Initial release
- Support for TXT, CSV, XLSX input formats
- Statistics and listings API integration
- Mod ranking support
- Ayatan sculpture star configuration
- Excel export functionality
- Command-line interface
- Comprehensive test suite
