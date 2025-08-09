import sqlite3
from faker import Faker
from datetime import datetime, timedelta
import random
import json
import hashlib
import uuid

fake = Faker()

def generate_sample_data():
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()
    
    # Lists to store IDs for foreign key references
    user_ids = []
    category_ids = []
    product_ids = []
    order_ids = []
    
    # 1. Insert Users (100 users)
    print("Inserting users...")
    for _ in range(100):
        first_name = fake.first_name()
        last_name = fake.last_name()
        username = f"{first_name.lower()}{last_name.lower()}{random.randint(1, 999)}"
        email = f"{username}@{fake.domain_name()}"
        password_hash = hashlib.sha256(fake.password().encode()).hexdigest()
        
        cursor.execute('''
        INSERT INTO users (username, email, password_hash, first_name, last_name,
                         phone, date_of_birth, gender, registration_date,
                         shipping_address, billing_address)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            username, email, password_hash, first_name, last_name,
            fake.phone_number(), fake.date_of_birth(minimum_age=18, maximum_age=90).isoformat(),
            random.choice(['M', 'F', 'Other']),
            fake.date_time_between(start_date='-2y').isoformat(),
            fake.address(), fake.address()
        ))
        user_ids.append(cursor.lastrowid)
    
    # Get existing category IDs
    cursor.execute('SELECT category_id FROM categories')
    category_ids = [row[0] for row in cursor.fetchall()]
    
    # 3. Insert Products (200 products)
    print("Inserting products...")
    product_names = [
        "Premium Laptop", "Smartphone Pro", "Classic T-Shirt", "Denim Jeans",
        "Running Shoes", "Wireless Earbuds", "Smart Watch", "Gaming Console",
        "Coffee Maker", "Backpack", "Sunglasses", "Desk Chair"
    ]
    brands = ["TechPro", "StyleX", "ComfortPlus", "SportMaster", "EliteGear"]
    materials = ["Cotton", "Polyester", "Leather", "Metal", "Plastic", "Glass"]
    colors = ["Black", "White", "Blue", "Red", "Gray", "Green"]
    sizes = ["XS", "S", "M", "L", "XL", "XXL"]
    
    for _ in range(200):
        base_name = random.choice(product_names)
        brand = random.choice(brands)
        sku = f"{brand[:3]}-{base_name[:3]}-{random.randint(1000, 9999)}"
        
        cursor.execute('''
        INSERT INTO products (product_name, product_description, category_id,
                            brand, sku, price, cost_price, stock_quantity,
                            weight, dimensions, color, size, material)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            f"{brand} {base_name}",
            fake.text(max_nb_chars=200),
            random.choice(category_ids),
            brand,
            sku,
            round(random.uniform(10, 1000), 2),
            round(random.uniform(5, 800), 2),
            random.randint(0, 1000),
            round(random.uniform(0.1, 20), 2),
            f"{random.randint(1, 100)}x{random.randint(1, 100)}x{random.randint(1, 100)}",
            random.choice(colors),
            random.choice(sizes),
            random.choice(materials)
        ))
        product_ids.append(cursor.lastrowid)
    
    # 4. Insert Orders (150 orders)
    print("Inserting orders...")
    for _ in range(150):
        user_id = random.choice(user_ids)
        order_date = fake.date_time_between(start_date='-1y')
        
        # Get user's addresses
        cursor.execute('SELECT shipping_address, billing_address FROM users WHERE user_id = ?', (user_id,))
        addresses = cursor.fetchone()
        
        cursor.execute('''
        INSERT INTO orders (user_id, order_number, order_status, order_date,
                          subtotal, tax_amount, shipping_cost, total_amount,
                          payment_method, payment_status, shipping_address,
                          billing_address)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            f"ORD-{uuid.uuid4().hex[:8].upper()}",
            random.choice(['Pending', 'Processing', 'Shipped', 'Delivered']),
            order_date.isoformat(),
            0,  # Will update after adding items
            0,  # Will update after adding items
            random.choice([5.99, 7.99, 10.99, 15.99]),
            0,  # Will update after adding items
            random.choice(['Credit Card', 'PayPal', 'Bank Transfer']),
            random.choice(['Pending', 'Paid']),
            addresses[0],
            addresses[1]
        ))
        order_id = cursor.lastrowid
        order_ids.append(order_id)
        
        # Add 1-5 items to each order
        subtotal = 0
        for _ in range(random.randint(1, 5)):
            product_id = random.choice(product_ids)
            quantity = random.randint(1, 5)
            
            # Get product details
            cursor.execute('SELECT product_name, sku, price FROM products WHERE product_id = ?', (product_id,))
            product = cursor.fetchone()
            unit_price = float(product[2])
            total_price = unit_price * quantity
            subtotal += total_price
            
            cursor.execute('''
            INSERT INTO order_items (order_id, product_id, quantity,
                                   unit_price, total_price, product_name,
                                   product_sku)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                order_id, product_id, quantity,
                unit_price, total_price, product[0],
                product[1]
            ))
        
        # Update order totals
        tax_amount = round(subtotal * 0.1, 2)  # 10% tax
        shipping_cost = random.choice([5.99, 7.99, 10.99, 15.99])
        total_amount = subtotal + tax_amount + shipping_cost
        
        cursor.execute('''
        UPDATE orders
        SET subtotal = ?, tax_amount = ?, total_amount = ?
        WHERE order_id = ?
        ''', (subtotal, tax_amount, total_amount, order_id))
    
    # 5. Insert Reviews (300 reviews)
    print("Inserting reviews...")
    for _ in range(300):
        user_id = random.choice(user_ids)
        product_id = random.choice(product_ids)
        order_id = random.choice(order_ids) if random.random() > 0.2 else None
        
        try:
            cursor.execute('''
            INSERT INTO reviews (product_id, user_id, order_id,
                               rating, review_title, review_text,
                               is_verified_purchase)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                product_id,
                user_id,
                order_id,
                random.randint(1, 5),
                fake.sentence(),
                fake.paragraph(),
                1 if order_id else 0
            ))
        except sqlite3.IntegrityError:
            # Skip if user already reviewed this product
            continue
    
    # Update product ratings
    print("Updating product ratings...")
    cursor.execute('''
    UPDATE products
    SET rating_count = (
        SELECT COUNT(*) FROM reviews WHERE reviews.product_id = products.product_id
    ),
    rating_average = (
        SELECT AVG(rating) FROM reviews WHERE reviews.product_id = products.product_id
    )
    ''')
    
    # Commit and close
    conn.commit()
    conn.close()
    print("Sample data inserted successfully!")

if __name__ == "__main__":
    generate_sample_data()
