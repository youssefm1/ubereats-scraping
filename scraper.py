import requests
import urllib.parse
import csv
from bs4 import BeautifulSoup
import string
from itertools import combinations_with_replacement, product

SCRAPE_TOKEN = "8080ad010dd74476a8005408eea8acf271c96aaff70"
UBEREATS_RESTAURANT_URL = "https://www.ubereats.com/store/asads-hot-chicken-south-philly/gcLzsdD6X9q9Etm6nXYDiA?ps=1?diningMode=DELIVERY"


def uber_eats_scrape():
    api_url = (
        f"https://api.scrape.do/?url={urllib.parse.quote_plus(UBEREATS_RESTAURANT_URL)}"
        f"&token={SCRAPE_TOKEN}"
        f"&super=true"
        f"&render=true"
        f"&customWait=5000"
    )

    response = requests.get(api_url)

    soup = BeautifulSoup(response.text, "html.parser")

    results = []

    for section in soup.find_all('div', {'data-testid': 'store-catalog-section-vertical-grid'}):
        cat_h3 = section.find('h3')
        category = cat_h3.get_text(strip=True) if cat_h3 else ''
        for item in section.find_all('li', {'data-testid': True}):
            if not item['data-testid'].startswith('store-item-'):
                continue

            rich_texts = item.find_all('span', {'data-testid': 'rich-text'})
            if len(rich_texts) < 2:
                continue

            name = rich_texts[0].get_text(strip=True)
            price = rich_texts[1].get_text(strip=True)

            
            results.append({
                'category': category,
                'name': name,
                'price': price
            })


    with open('ubereats_restaurant_menu.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['category', 'name', 'price']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)
    print(f"Wrote {len(results)} menu items to ubereats_restaurant_menu.csv")

def generate_combos():
    valid_combo_items = []
    drink_categories = {'Water', 'Cans', 'Glass Bottle', '20 Oz Drinks', 'Energy Drinks', 'Fountain Drinks', 'Milkshakes', 'Fruit Smoothies', 'Drinks'}
    
    with open('ubereats_restaurant_menu.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        data = list(reader)
        for row in data:
            if row['category'] == 'Priced by add-ons':
                continue
            if row['category'] in drink_categories:
                continue
            try:
                price_value = float(row['price'].replace('$', '').strip())
                # Only include items $6 or more
                if price_value >= 6:
                    valid_combo_items.append(row)
            except ValueError:
                continue
    return valid_combo_items


def find_combinations(items, min_price=6, max_price=30, limit=50000):
    """Efficiently find combinations using recursive backtracking with pruning"""
    valid_combinations = []
    max_per_item = 2
    
    affordable_items = [item for item in items if int(item['price'].replace("$", "").split(".")[0]) <= max_price]
    print(f"\nGenerating combinations from {len(affordable_items)} affordable items (limiting to {limit} results)...")
    
    # Parse prices once
    item_prices = []
    for item in affordable_items:
        price = int(item['price'].replace("$", "").split(".")[0])
        item_prices.append(price)
    
    combo_count = [0]  # Use list to track count in nested function
    
    def backtrack(index, current_items, current_price, item_count):
        """Recursively build combinations with pruning"""
        # Early exit if we've found enough combinations
        if len(valid_combinations) >= limit:
            return
        
        combo_count[0] += 1
        
        if combo_count[0] % 100000 == 0:
            print(f"Evaluated {combo_count[0]:,} combinations, found {len(valid_combinations)} valid ones...")
        
        # Base case: reached end of items
        if index == len(affordable_items):
            if min_price <= current_price <= max_price and item_count > 0:
                avg_price_per_item = current_price / item_count
                valid_combinations.append({
                    'items': current_items[:],
                    'total_price': current_price,
                    'item_count': item_count,
                    'avg_price_per_item': avg_price_per_item,
                    'unique_items': len([x for x in current_items if x is not None])
                })
            return
        
        # Pruning: if current price already exceeds max, skip
        if current_price > max_price:
            return
        
        # Pruning: if even one more item exceeds max items, skip adding more items
        if item_count >= 10:
            # Still try without adding this item
            backtrack(index + 1, current_items, current_price, item_count)
            return
        
        # Try adding 0, 1, or 2 of current item
        for qty in range(max_per_item + 1):
            item_total_price = item_prices[index] * qty
            new_price = current_price + item_total_price
            
            # Pruning: skip if exceeds max price
            if new_price > max_price:
                break
            
            if qty > 0:
                for _ in range(qty):
                    current_items.append(affordable_items[index])
            
            backtrack(index + 1, current_items, new_price, item_count + qty)
            
            if qty > 0:
                for _ in range(qty):
                    current_items.pop()
    
    backtrack(0, [], 0, 0)
    print(f"Total combinations evaluated: {combo_count[0]:,}")
    return valid_combinations

def find_best_value_combinations(combinations, top_n=10):
    """Find the best value combinations based on various metrics"""
    
    # Sort by different criteria
    most_items = sorted(combinations, 
                       key=lambda x: (x['item_count'], -x['total_price']))[:top_n]
    
    best_bang_for_buck = sorted(combinations,
                               key=lambda x: (-x['item_count'] / x['total_price']))[:top_n]
    
    premium_selections = sorted(combinations,
                               key=lambda x: x['avg_price_per_item'],
                               reverse=True)[:top_n]
    
    closest_to_max = sorted(combinations,
                           key=lambda x: abs(30 - x['total_price']))[:top_n]
    
    most_unique = sorted(combinations,
                        key=lambda x: x['unique_items'],
                        reverse=True)[:top_n]
    
    return {
        'most_items': most_items,
        'best_value_ratio': best_bang_for_buck,
        'premium_selections': premium_selections,
        'closest_to_max': closest_to_max,
        'most_unique_items': most_unique
    }

def print_combination_with_quantities(combo, title=""):
    """Pretty print a combination showing quantities"""
    if title:
        print(f"\n{'='*60}")
        print(f"{title}")
        print(f"{'='*60}")
    
    print(f"Total: ${combo['total_price']:.2f} | "
          f"Items: {combo['item_count']} | "
          f"Unique: {combo['unique_items']} | "
          f"Avg: ${combo['avg_price_per_item']:.2f}")
    print("-" * 60)
    
    # Group items by name to show quantities
    item_counts = {}
    for item in combo['items']:
        key = f"{item['category']}: {item['name']}"
        item_counts[key] = item_counts.get(key, 0) + 1
    
    for item_desc, count in item_counts.items():
        price_item = next(item for item in combo['items'] 
                         if f"{item['category']}: {item['name']}" == item_desc)
        price = float(price_item['price'].replace('$', '').strip())
        print(f"  {count}x {item_desc} - ${price:.2f} each (${price * count:.2f} total)")


def main():
    # uber_eats_scrape()
    valid_items = generate_combos()
    all_combinations  = find_combinations(valid_items)
    #best_combos = find_best_value_combinations(combinations)


    if all_combinations:
        # Find best value combinations
        best_combos = find_best_value_combinations(all_combinations, top_n=5)
        
        # Print results
        for category, combos in best_combos.items():
            print(f"\n{'#'*60}")
            print(f"TOP 5 - {category.replace('_', ' ').title()}")
            print(f"{'#'*60}")
            
            for i, combo in enumerate(combos, 1):
                print(f"\n{i}. ", end="")
                print_combination_with_quantities(combo)

def analyze_combinations_by_category(combinations):
    """Analyze which categories appear most in good combos"""
    category_scores = {}
    
    for combo in combinations:
        # Score combo based on value (more items for less money = higher score)
        score = combo['item_count'] / combo['total_price']
        
        # Track categories in this combo
        categories_in_combo = set()
        for item in combo['items']:
            categories_in_combo.add(item['category'])
        
        # Add score to each category in the combo
        for category in categories_in_combo:
            category_scores[category] = category_scores.get(category, 0) + score
    
    # Sort categories by score
    sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
    
    print("\n" + "="*60)
    print("CATEGORY VALUE ANALYSIS")
    print("="*60)
    for category, score in sorted_categories[:10]:
        print(f"{category}: {score:.2f}")
    
    return sorted_categories

# Run analysis
# analyze_combinations_by_category(all_combinations)

def export_combinations_to_csv(combinations, filename="best_combinations.csv"):
    """Export top combinations to CSV for further analysis"""
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Rank', 'Total Price', 'Item Count', 'Unique Items', 
                        'Avg Price/Item', 'Items List'])
        
        for i, combo in enumerate(combinations[:100], 1):
            # Create a compact items list
            items_summary = []
            item_counts = {}
            for item in combo['items']:
                key = f"{item['name']} (${item['price']})"
                item_counts[key] = item_counts.get(key, 0) + 1
            
            for item_desc, count in item_counts.items():
                items_summary.append(f"{count}x {item_desc}")
            
            writer.writerow([
                i,
                f"${combo['total_price']:.2f}",
                combo['item_count'],
                combo['unique_items'],
                f"${combo['avg_price_per_item']:.2f}",
                "; ".join(items_summary)
            ])
    
    print(f"\nExported top {min(100, len(combinations))} combinations to {filename}")

if __name__ == "__main__":
    main()