# Uber Eats Value Combo Finder

A Python-based tool that scrapes Uber Eats restaurant menus and generates optimal food combinations based on value metrics. Built out of hunger and a desire to maximize bang-for-your-buck when ordering takeaway.

## Overview

This project uses web scraping and combinatorial optimization to find the best value meal combos within a specified budget. Instead of manually browsing a menu and guessing, it analyzes all possible combinations and ranks them by different metrics: most items, best price-per-item ratio, closest to budget, and most variety.

## Features

- **Web Scraping**: Scrapes Uber Eats restaurant menus using BeautifulSoup
- **Smart Filtering**: Excludes drinks and priced-by-add-ons items, enforces minimum item prices
- **Constraint-Based**: Desserts limited to 1 per combo, most items capped at 2 per combo
- **Optimized Search**: Uses recursive backtracking with pruning to find valid combinations
- **Multi-Metric Analysis**: Ranks combos by:
  - Most items for the price
  - Best value ratio (items per dollar)
  - Premium selections (highest avg price per item)
  - Closest to maximum budget
  - Most unique items

## Installation

```bash
pip install requests beautifulsoup4
```

## Usage

1. Update `UBEREATS_RESTAURANT_URL` in `scraper.py` with your target restaurant
2. Set your `SCRAPE_TOKEN` (from scrape.do API)
3. Run the script:

```bash
python scraper.py
```

The script will:
1. Scrape the menu and save it to `ubereats_restaurant_menu.csv`
2. Generate all valid combinations within your budget ($6-$30)
3. Rank and display the top 5 combos in each category

## Example Output

```
############################################################
TOP 5 - Closest To Max
############################################################

1. Total: $30.00 | Items: 4 | Unique: 4 | Avg: $7.50
------------------------------------------------------------
  2x Sides: Single Tender Wrap - $9.10 each ($18.20 total)
  1x Sides: Golden Cup - $6.50 each ($6.50 total)
  1x Desserts: Banana Pudding - $6.50 each ($6.50 total)

2. Total: $30.00 | Items: 4 | Unique: 4 | Avg: $7.50
------------------------------------------------------------
  2x Sides: Single Tender Wrap - $9.10 each ($18.20 total)
  2x Sides: Golden Cup - $6.50 each ($13.00 total)

############################################################
TOP 5 - Most Unique Items
############################################################

1. Total: $32.00 | Items: 5 | Unique: 5 | Avg: $6.40
------------------------------------------------------------
  2x Sides: Cheese Fries - $7.20 each ($14.40 total)
  2x Sides: Golden Cup - $6.50 each ($13.00 total)
  1x Desserts: Banana Pudding - $6.50 each ($6.50 total)

2. Total: $34.00 | Items: 5 | Unique: 5 | Avg: $6.80
------------------------------------------------------------
  1x Sides: Single Tender Wrap - $9.10 each ($9.10 total)
  1x Sides: Cheese Fries - $7.20 each ($7.20 total)
  2x Sides: Golden Cup - $6.50 each ($13.00 total)
  1x Desserts: Banana Pudding - $6.50 each ($6.50 total)
```

## How It Works

The algorithm uses **recursive backtracking with pruning** to efficiently explore the combination space:

1. **Filters items** by budget and excludes ineligible categories
2. **Iterates through each item** and decides: take 0, 1, or 2 of it
3. **Prunes branches** when:
   - Total price exceeds budget
   - Item count exceeds limit
   - Dessert quota reached
4. **Collects valid combinations** that meet price range constraints
5. **Ranks results** by multiple metrics for easy browsing

## Customization

Edit these variables in `scraper.py`:

- `min_price` / `max_price`: Budget range (default: $6-$30)
- `max_per_item`: Max quantity per non-dessert item (default: 2)
- `limit`: Max combos to generate (default: 50,000)
- `drink_categories`: Categories to exclude

## Files

- `scraper.py` - Main script with scraping and combo generation logic
- `ubereats_restaurant_menu.csv` - Generated menu data
- `best_combinations.csv` - Optional export of top combos
