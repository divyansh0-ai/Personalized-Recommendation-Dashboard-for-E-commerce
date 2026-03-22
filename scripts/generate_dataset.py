"""
generate_dataset.py
-------------------
Generates a large, realistic synthetic e-commerce dataset and writes four CSV
files into the `data/` directory (relative to the repository root):

  data/products.csv  – product catalogue
  data/users.csv     – customer profiles
  data/orders.csv    – order / transaction records
  data/reviews.csv   – product reviews

Usage
-----
  # defaults: 500 products, 2 000 users, 10 000 orders, 8 000 reviews
  python scripts/generate_dataset.py

  # custom sizes
  python scripts/generate_dataset.py \
      --products 2000 --users 10000 --orders 100000 --reviews 80000

  # write to a different directory
  python scripts/generate_dataset.py --out-dir /path/to/output

Real-World Public Datasets (alternatives / supplements)
---------------------------------------------------------
If you need actual transactional data with real product names/images you can
download these freely available datasets and drop them into data/:

  • Brazilian E-Commerce (Olist) — 100 k orders, 9 linked tables
      https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

  • Amazon Product Reviews (UCSD) — millions of reviews across 29 categories
      https://cseweb.ucsd.edu/~jmcauley/datasets/amazon_v2/

  • Online Retail II (UCI) — real UK retailer transactions 2009-2011
      https://archive.ics.uci.edu/dataset/502/online+retail+ii

  • Instacart Market Basket — 3 M grocery orders from 200 k users
      https://www.kaggle.com/competitions/instacart-market-basket-analysis/data
"""

import argparse
import csv
import os
import random
import uuid
from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# Configuration / seed
# ---------------------------------------------------------------------------

SEED = 42
random.seed(SEED)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_OUT_DIR = os.path.join(REPO_ROOT, "data")

# ---------------------------------------------------------------------------
# Lookup tables
# ---------------------------------------------------------------------------

CATEGORIES = {
    "Electronics": [
        "Laptop", "Smartphone", "Tablet", "Smartwatch", "Wireless Earbuds",
        "Bluetooth Speaker", "Gaming Console", "Mechanical Keyboard",
        "4K Monitor", "Webcam", "USB-C Hub", "External SSD",
        "Noise-Cancelling Headphones", "Action Camera", "Smart TV",
    ],
    "Clothing": [
        "Men's T-Shirt", "Women's Dress", "Denim Jeans", "Winter Jacket",
        "Running Shoes", "Formal Shirt", "Casual Shorts", "Hoodie",
        "Activewear Leggings", "Polo Shirt", "Leather Belt", "Wool Sweater",
        "Raincoat", "Sneakers", "Socks (6-pack)",
    ],
    "Home & Kitchen": [
        "Air Fryer", "Coffee Maker", "Stand Mixer", "Blender", "Instant Pot",
        "Non-Stick Pan Set", "Knife Block Set", "Cutting Board",
        "Storage Organizer", "Vacuum Cleaner", "Electric Kettle",
        "Toaster Oven", "Rice Cooker", "Mattress Topper", "Pillow Set",
    ],
    "Books": [
        "Python Programming", "Data Science Handbook", "Atomic Habits",
        "Deep Work", "The Pragmatic Programmer", "Clean Code",
        "Designing Data-Intensive Applications", "Thinking Fast and Slow",
        "The Lean Startup", "Zero to One", "Sapiens", "The Almanack",
        "Rich Dad Poor Dad", "The Psychology of Money", "Can't Hurt Me",
    ],
    "Sports & Outdoors": [
        "Yoga Mat", "Resistance Bands Set", "Adjustable Dumbbells",
        "Cycling Helmet", "Running Watch", "Water Bottle (32oz)",
        "Camping Tent", "Trekking Poles", "Foam Roller",
        "Pull-Up Bar", "Jump Rope", "Gym Gloves",
        "Protein Shaker Bottle", "Sleeping Bag", "Hiking Backpack",
    ],
    "Beauty & Personal Care": [
        "Vitamin C Serum", "Moisturising Sunscreen SPF50",
        "Electric Toothbrush", "Hair Dryer", "Beard Trimmer",
        "Facial Cleanser", "Lip Balm Set", "Eyeshadow Palette",
        "Perfume", "Nail Polish Set", "Shampoo & Conditioner Bundle",
        "Face Mask Sheet Pack", "Body Lotion", "Makeup Brush Set",
        "Anti-Aging Cream",
    ],
    "Toys & Games": [
        "LEGO City Set", "Board Game (Catan)", "RC Car",
        "Puzzle (1000 pieces)", "Action Figure Set", "Play-Doh Bundle",
        "Card Game (UNO)", "Drone for Kids", "Educational Robot Kit",
        "Stuffed Animal", "Water Guns Set", "Magnetic Tiles",
        "Science Experiment Kit", "Musical Toy Piano", "Bike for Kids",
    ],
    "Grocery & Gourmet": [
        "Organic Olive Oil", "Premium Coffee Beans (1 kg)", "Green Tea (100 bags)",
        "Dark Chocolate Box", "Protein Bars (12-pack)", "Mixed Nuts (500g)",
        "Honey (Raw, 500g)", "Hot Sauce Set", "Pasta (5-pack)",
        "Quinoa (1 kg)", "Coconut Oil (500ml)", "Spice Gift Set",
        "Matcha Powder", "Dried Fruit Mix", "Oat Granola (1 kg)",
    ],
}

BRANDS = [
    "TechNova", "UrbanEdge", "PeakLine", "NovaBrands", "ClearPath",
    "ZenCraft", "SkyForge", "EcoBloom", "PrimeSelect", "BlueMark",
    "SwiftWave", "NexGen", "AuraStyle", "BoldStep", "PureCraft",
    "LunaGoods", "TrueNorth", "SilverKey", "GoldenGate", "IronVault",
]

COUNTRIES = [
    "United States", "United Kingdom", "Canada", "Australia", "Germany",
    "France", "India", "Brazil", "Mexico", "Japan", "Singapore",
    "Netherlands", "Spain", "Italy", "Sweden",
]

CITIES_BY_COUNTRY = {
    "United States": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"],
    "United Kingdom": ["London", "Manchester", "Birmingham", "Leeds", "Glasgow"],
    "Canada": ["Toronto", "Vancouver", "Montreal", "Calgary", "Ottawa"],
    "Australia": ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide"],
    "Germany": ["Berlin", "Hamburg", "Munich", "Cologne", "Frankfurt"],
    "France": ["Paris", "Marseille", "Lyon", "Toulouse", "Nice"],
    "India": ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai"],
    "Brazil": ["São Paulo", "Rio de Janeiro", "Brasília", "Salvador", "Fortaleza"],
    "Mexico": ["Mexico City", "Guadalajara", "Monterrey", "Puebla", "Cancún"],
    "Japan": ["Tokyo", "Osaka", "Kyoto", "Yokohama", "Nagoya"],
    "Singapore": ["Singapore"],
    "Netherlands": ["Amsterdam", "Rotterdam", "The Hague", "Utrecht", "Eindhoven"],
    "Spain": ["Madrid", "Barcelona", "Valencia", "Seville", "Bilbao"],
    "Italy": ["Rome", "Milan", "Naples", "Turin", "Palermo"],
    "Sweden": ["Stockholm", "Gothenburg", "Malmö", "Uppsala", "Linköping"],
}

PAYMENT_METHODS = [
    "Credit Card", "Debit Card", "PayPal", "Apple Pay",
    "Google Pay", "Bank Transfer", "Gift Card",
]

ORDER_STATUSES = ["Delivered", "Shipped", "Processing", "Cancelled", "Returned"]
ORDER_STATUS_WEIGHTS = [0.60, 0.15, 0.10, 0.10, 0.05]

REVIEW_SENTIMENTS = {
    5: [
        "Absolutely love this product! Highly recommend.",
        "Exceeded all my expectations. Would buy again.",
        "Perfect quality and fast shipping.",
        "Best purchase I've made in years.",
        "Fantastic product, exactly as described.",
    ],
    4: [
        "Really good product, minor packaging issue.",
        "Works great, delivery was slightly delayed.",
        "Very happy with the purchase overall.",
        "Good value for money, will recommend.",
        "High quality, just as expected.",
    ],
    3: [
        "Decent product but nothing spectacular.",
        "Average quality. Does the job.",
        "It's okay, expected a bit more.",
        "Works fine, instructions could be clearer.",
        "Neither great nor terrible. Fair price.",
    ],
    2: [
        "Not what I expected. Quality is lacking.",
        "Had issues with the product on arrival.",
        "Disappointed with the build quality.",
        "Customer service was unhelpful.",
        "Would not buy this again.",
    ],
    1: [
        "Complete waste of money. Arrived broken.",
        "Terrible quality, stopped working in a week.",
        "Very disappointing. Does not match description.",
        "Returning immediately. Not as advertised.",
        "Worst product I've ever bought.",
    ],
}

FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael",
    "Linda", "William", "Barbara", "David", "Elizabeth", "Richard", "Susan",
    "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen", "Emma",
    "Liam", "Olivia", "Noah", "Ava", "Sophia", "Isabella", "Mia", "Amelia",
    "Ethan", "Lucas", "Mason", "Logan", "Alexander", "Aiden", "Harper",
    "Evelyn", "Abigail", "Emily", "Ella", "Chloe", "Victoria", "Sofia",
    "Arjun", "Priya", "Raj", "Anika", "Wei", "Mei", "Yuki", "Hiroshi",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
    "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
    "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green",
    "Patel", "Kumar", "Sharma", "Singh", "Zhang", "Wang", "Liu", "Chen",
]

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------


def rand_date(start: datetime, end: datetime) -> datetime:
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))


def weighted_choice(choices, weights):
    total = sum(weights)
    r = random.uniform(0, total)
    cumulative = 0
    for choice, weight in zip(choices, weights):
        cumulative += weight
        if r <= cumulative:
            return choice
    return choices[-1]


def round2(x):
    return round(x, 2)


# ---------------------------------------------------------------------------
# Generators
# ---------------------------------------------------------------------------


def generate_products(n: int) -> list[dict]:
    """Generate `n` product records."""
    products = []
    categories = list(CATEGORIES.keys())
    used_names: set[str] = set()

    for i in range(1, n + 1):
        category = random.choice(categories)
        base_name = random.choice(CATEGORIES[category])
        brand = random.choice(BRANDS)
        name = f"{brand} {base_name}"
        # ensure uniqueness by appending a variant suffix
        variant = 1
        unique_name = name
        while unique_name in used_names:
            unique_name = f"{name} v{variant}"
            variant += 1
        used_names.add(unique_name)

        cost_price = round2(random.uniform(5, 800))
        markup = random.uniform(1.15, 2.5)
        selling_price = round2(cost_price * markup)
        stock = random.randint(0, 1000)
        rating = round2(random.gauss(4.1, 0.6))
        rating = max(1.0, min(5.0, rating))
        reviews_count = random.randint(0, 5000)
        discount_pct = random.choice([0, 0, 0, 5, 10, 15, 20, 25, 30])
        discounted_price = round2(selling_price * (1 - discount_pct / 100))

        products.append(
            {
                "product_id": f"P{i:05d}",
                "product_name": unique_name,
                "brand": brand,
                "category": category,
                "base_item": base_name,
                "cost_price": cost_price,
                "selling_price": selling_price,
                "discount_pct": discount_pct,
                "discounted_price": discounted_price,
                "stock_quantity": stock,
                "avg_rating": round2(rating),
                "reviews_count": reviews_count,
                "is_active": random.choices([True, False], weights=[0.9, 0.1])[0],
            }
        )
    return products


def generate_users(n: int) -> list[dict]:
    """Generate `n` user/customer records."""
    users = []
    start = datetime(2018, 1, 1)
    end = datetime(2024, 12, 31)

    for i in range(1, n + 1):
        country = random.choice(COUNTRIES)
        city = random.choice(CITIES_BY_COUNTRY[country])
        reg_date = rand_date(start, end)
        last_active = rand_date(reg_date, end)
        age = random.randint(18, 72)
        gender = random.choices(["Male", "Female", "Non-binary", "Prefer not to say"],
                                weights=[0.48, 0.48, 0.02, 0.02])[0]
        fname = random.choice(FIRST_NAMES)
        lname = random.choice(LAST_NAMES)

        users.append(
            {
                "user_id": f"U{i:06d}",
                "first_name": fname,
                "last_name": lname,
                "email": f"{fname.lower()}.{lname.lower()}{i}@example.com",
                "age": age,
                "gender": gender,
                "country": country,
                "city": city,
                "registration_date": reg_date.strftime("%Y-%m-%d"),
                "last_active_date": last_active.strftime("%Y-%m-%d"),
                "is_premium": random.choices([True, False], weights=[0.25, 0.75])[0],
            }
        )
    return users


def generate_orders(
    n: int, products: list[dict], users: list[dict]
) -> list[dict]:
    """Generate `n` order records referencing existing products and users."""
    orders = []
    product_ids = [p["product_id"] for p in products]
    user_ids = [u["user_id"] for u in users]
    # Build price lookup
    price_lookup = {p["product_id"]: p["discounted_price"] for p in products}

    start = datetime(2019, 1, 1)
    end = datetime(2025, 3, 1)

    for i in range(1, n + 1):
        user_id = random.choice(user_ids)
        # Each order has 1-5 distinct line items
        n_items = random.choices([1, 2, 3, 4, 5], weights=[0.45, 0.25, 0.15, 0.10, 0.05])[0]
        chosen_products = random.sample(product_ids, min(n_items, len(product_ids)))
        order_date = rand_date(start, end)
        status = weighted_choice(ORDER_STATUSES, ORDER_STATUS_WEIGHTS)
        payment = random.choice(PAYMENT_METHODS)

        total = 0.0
        items_str_parts = []
        for pid in chosen_products:
            qty = random.randint(1, 5)
            unit_price = price_lookup[pid]
            total += qty * unit_price
            items_str_parts.append(f"{pid}×{qty}")

        orders.append(
            {
                "order_id": f"O{i:07d}",
                "user_id": user_id,
                "order_date": order_date.strftime("%Y-%m-%d %H:%M:%S"),
                "product_ids": "|".join(items_str_parts),
                "num_items": len(chosen_products),
                "order_total": round2(total),
                "payment_method": payment,
                "status": status,
                "delivery_days": (
                    random.randint(1, 14) if status not in ("Processing", "Cancelled") else None
                ),
            }
        )
    return orders


def generate_reviews(
    n: int, products: list[dict], users: list[dict]
) -> list[dict]:
    """Generate `n` product review records."""
    reviews = []
    product_ids = [p["product_id"] for p in products]
    user_ids = [u["user_id"] for u in users]

    start = datetime(2019, 1, 1)
    end = datetime(2025, 3, 1)

    for i in range(1, n + 1):
        rating = random.choices([1, 2, 3, 4, 5], weights=[0.05, 0.08, 0.15, 0.32, 0.40])[0]
        review_text = random.choice(REVIEW_SENTIMENTS[rating])
        review_date = rand_date(start, end)

        reviews.append(
            {
                "review_id": f"R{i:07d}",
                "product_id": random.choice(product_ids),
                "user_id": random.choice(user_ids),
                "rating": rating,
                "review_text": review_text,
                "helpful_votes": random.randint(0, 250),
                "verified_purchase": random.choices([True, False], weights=[0.75, 0.25])[0],
                "review_date": review_date.strftime("%Y-%m-%d"),
            }
        )
    return reviews


# ---------------------------------------------------------------------------
# CSV writer
# ---------------------------------------------------------------------------


def write_csv(path: str, records: list[dict]) -> None:
    if not records:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)
    print(f"  Written {len(records):,} rows → {path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate a large synthetic e-commerce dataset."
    )
    parser.add_argument("--products", type=int, default=500,
                        help="Number of products to generate (default: 500)")
    parser.add_argument("--users", type=int, default=2000,
                        help="Number of users to generate (default: 2 000)")
    parser.add_argument("--orders", type=int, default=10000,
                        help="Number of orders to generate (default: 10 000)")
    parser.add_argument("--reviews", type=int, default=8000,
                        help="Number of reviews to generate (default: 8 000)")
    parser.add_argument("--out-dir", type=str, default=DEFAULT_OUT_DIR,
                        help=f"Output directory (default: {DEFAULT_OUT_DIR})")
    parser.add_argument("--seed", type=int, default=SEED,
                        help=f"Random seed for reproducibility (default: {SEED})")
    return parser.parse_args()


def main():
    args = parse_args()
    random.seed(args.seed)

    print(f"\n🛒  Generating e-commerce dataset (seed={args.seed})")
    print(f"    products={args.products:,}  users={args.users:,}  "
          f"orders={args.orders:,}  reviews={args.reviews:,}")
    print(f"    output directory: {args.out_dir}\n")

    print("→ Generating products …")
    products = generate_products(args.products)
    write_csv(os.path.join(args.out_dir, "products.csv"), products)

    print("→ Generating users …")
    users = generate_users(args.users)
    write_csv(os.path.join(args.out_dir, "users.csv"), users)

    print("→ Generating orders …")
    orders = generate_orders(args.orders, products, users)
    write_csv(os.path.join(args.out_dir, "orders.csv"), orders)

    print("→ Generating reviews …")
    reviews = generate_reviews(args.reviews, products, users)
    write_csv(os.path.join(args.out_dir, "reviews.csv"), reviews)

    print("\n✅  Done! Dataset written to:", args.out_dir)


if __name__ == "__main__":
    main()
