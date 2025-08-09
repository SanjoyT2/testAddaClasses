import sqlite3
from datetime import datetime

def create_database():
    # Connect to SQLite database (it will be created if it doesn't exist)
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()

    # 1. Users Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        phone TEXT,
        date_of_birth DATE,
        gender TEXT CHECK(gender IN ('M', 'F', 'Other')),
        registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP,
        account_status TEXT DEFAULT 'Active' CHECK(account_status IN ('Active', 'Inactive', 'Suspended')),
        loyalty_points INTEGER DEFAULT 0,
        total_spent REAL DEFAULT 0.00,
        shipping_address TEXT,
        billing_address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 2. Categories Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_name TEXT NOT NULL,
        parent_category_id INTEGER,
        category_description TEXT,
        category_image_url TEXT,
        is_active INTEGER DEFAULT 1,
        sort_order INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (parent_category_id) REFERENCES categories(category_id)
    )
    ''')

    # 3. Products Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        product_description TEXT,
        category_id INTEGER NOT NULL,
        brand TEXT,
        sku TEXT UNIQUE NOT NULL,
        price REAL NOT NULL,
        cost_price REAL,
        discount_percentage REAL DEFAULT 0.00,
        stock_quantity INTEGER NOT NULL DEFAULT 0,
        min_stock_level INTEGER DEFAULT 10,
        weight REAL,
        dimensions TEXT,
        color TEXT,
        size TEXT,
        material TEXT,
        product_status TEXT DEFAULT 'Active' CHECK(product_status IN ('Active', 'Inactive', 'Discontinued')),
        featured INTEGER DEFAULT 0,
        rating_average REAL DEFAULT 0.00,
        rating_count INTEGER DEFAULT 0,
        view_count INTEGER DEFAULT 0,
        sales_count INTEGER DEFAULT 0,
        image_urls TEXT,
        tags TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES categories(category_id)
    )
    ''')

    # 4. Orders Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        order_number TEXT UNIQUE NOT NULL,
        order_status TEXT DEFAULT 'Pending' CHECK(order_status IN ('Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled', 'Refunded')),
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        shipping_date TIMESTAMP,
        delivery_date TIMESTAMP,
        subtotal REAL NOT NULL,
        tax_amount REAL DEFAULT 0.00,
        shipping_cost REAL DEFAULT 0.00,
        discount_amount REAL DEFAULT 0.00,
        total_amount REAL NOT NULL,
        payment_method TEXT NOT NULL CHECK(payment_method IN ('Credit Card', 'Debit Card', 'PayPal', 'Bank Transfer', 'Cash on Delivery')),
        payment_status TEXT DEFAULT 'Pending' CHECK(payment_status IN ('Pending', 'Paid', 'Failed', 'Refunded')),
        shipping_address TEXT NOT NULL,
        billing_address TEXT NOT NULL,
        tracking_number TEXT,
        notes TEXT,
        coupon_code TEXT,
        loyalty_points_used INTEGER DEFAULT 0,
        loyalty_points_earned INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    ''')

    # 5. Order Items Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS order_items (
        order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        discount_amount REAL DEFAULT 0.00,
        total_price REAL NOT NULL,
        product_name TEXT NOT NULL,
        product_sku TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (order_id) REFERENCES orders(order_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    )
    ''')

    # 6. Reviews Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reviews (
        review_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        order_id INTEGER,
        rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
        review_title TEXT,
        review_text TEXT,
        is_verified_purchase INTEGER DEFAULT 0,
        helpful_votes INTEGER DEFAULT 0,
        total_votes INTEGER DEFAULT 0,
        review_status TEXT DEFAULT 'Pending' CHECK(review_status IN ('Pending', 'Approved', 'Rejected')),
        review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(product_id),
        FOREIGN KEY (user_id) REFERENCES users(user_id),
        FOREIGN KEY (order_id) REFERENCES orders(order_id),
        UNIQUE (user_id, product_id, order_id)
    )
    ''')

    # Create indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_registration_date ON users(registration_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_name ON products(product_name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_total ON orders(total_amount)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_reviews_date ON reviews(review_date)')

    # Insert sample categories
    cursor.execute('''
    INSERT OR IGNORE INTO categories (category_name, category_description) 
    VALUES ('Electronics', 'Electronic devices and accessories')
    ''')
    
    electronics_id = cursor.lastrowid
    
    cursor.execute('''
    INSERT OR IGNORE INTO categories (category_name, parent_category_id, category_description) 
    VALUES ('Smartphones', ?, 'Mobile phones and accessories')
    ''', (electronics_id,))
    
    cursor.execute('''
    INSERT OR IGNORE INTO categories (category_name, parent_category_id, category_description) 
    VALUES ('Laptops', ?, 'Portable computers')
    ''', (electronics_id,))
    
    cursor.execute('''
    INSERT OR IGNORE INTO categories (category_name, category_description) 
    VALUES ('Clothing', 'Apparel and fashion')
    ''')
    
    clothing_id = cursor.lastrowid
    
    cursor.execute('''
    INSERT OR IGNORE INTO categories (category_name, parent_category_id, category_description) 
    VALUES ('Men''s Clothing', ?, 'Clothing for men')
    ''', (clothing_id,))
    
    cursor.execute('''
    INSERT OR IGNORE INTO categories (category_name, parent_category_id, category_description) 
    VALUES ('Women''s Clothing', ?, 'Clothing for women')
    ''', (clothing_id,))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    print("Database created successfully with all tables and sample categories!")

if __name__ == "__main__":
    create_database()
