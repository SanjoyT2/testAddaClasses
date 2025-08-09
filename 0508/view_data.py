import sqlite3
from tabulate import tabulate

def view_data():
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()

    def print_table_data(table_name, limit=5):
        print(f"\n=== Sample Data from {table_name.upper()} table ===")
        cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        print(tabulate(rows, headers=columns, tablefmt='grid'))
        print(f"Total records in {table_name}: ", cursor.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0])

    # 1. View Categories
    print("\n=== CATEGORIES TREE ===")
    cursor.execute('''
    WITH RECURSIVE category_tree AS (
        SELECT category_id, category_name, parent_category_id, 0 as level
        FROM categories WHERE parent_category_id IS NULL
        UNION ALL
        SELECT c.category_id, c.category_name, c.parent_category_id, ct.level + 1
        FROM categories c
        JOIN category_tree ct ON c.parent_category_id = ct.category_id
    )
    SELECT printf('%s%s', REPLACE(hex(zeroblob(level)), '00', '  '), category_name)
    FROM category_tree
    ORDER BY level, category_name
    ''')
    for row in cursor.fetchall():
        print(row[0])

    # 2. View Users
    print_table_data('users')

    # 3. View Products
    cursor.execute('''
    SELECT p.product_id, p.product_name, c.category_name, p.price, 
           p.stock_quantity, p.rating_average, p.rating_count
    FROM products p
    JOIN categories c ON p.category_id = c.category_id
    ORDER BY p.rating_count DESC
    LIMIT 5
    ''')
    print("\n=== TOP RATED PRODUCTS ===")
    print(tabulate(cursor.fetchall(), 
                  headers=['ID', 'Product', 'Category', 'Price', 'Stock', 'Rating', '# Reviews'],
                  tablefmt='grid'))

    # 4. View Orders
    cursor.execute('''
    SELECT o.order_id, o.order_number, u.username,
           o.total_amount, o.order_status, o.payment_status,
           COUNT(oi.order_item_id) as items
    FROM orders o
    JOIN users u ON o.user_id = u.user_id
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY o.order_id
    ORDER BY o.order_date DESC
    LIMIT 5
    ''')
    print("\n=== RECENT ORDERS ===")
    print(tabulate(cursor.fetchall(),
                  headers=['ID', 'Order #', 'Username', 'Total', 'Status', 'Payment', 'Items'],
                  tablefmt='grid'))

    # 5. View Order Items
    cursor.execute('''
    SELECT oi.order_id, p.product_name, oi.quantity,
           oi.unit_price, oi.total_price
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    LIMIT 5
    ''')
    print("\n=== SAMPLE ORDER ITEMS ===")
    print(tabulate(cursor.fetchall(),
                  headers=['Order ID', 'Product', 'Qty', 'Unit Price', 'Total'],
                  tablefmt='grid'))

    # 6. View Reviews
    cursor.execute('''
    SELECT r.review_id, p.product_name, u.username,
           r.rating, r.review_title, 
           r.helpful_votes, r.review_status
    FROM reviews r
    JOIN products p ON r.product_id = p.product_id
    JOIN users u ON r.user_id = u.user_id
    ORDER BY r.helpful_votes DESC
    LIMIT 5
    ''')
    print("\n=== TOP REVIEWS ===")
    print(tabulate(cursor.fetchall(),
                  headers=['ID', 'Product', 'User', 'Rating', 'Title', 'Helpful Votes', 'Status'],
                  tablefmt='grid'))

    # Some interesting statistics
    print("\n=== STATISTICS ===")
    stats = []
    
    cursor.execute("SELECT COUNT(*), AVG(total_amount) FROM orders")
    orders_stats = cursor.fetchone()
    stats.append(["Total Orders", orders_stats[0]])
    stats.append(["Average Order Value", f"${orders_stats[1]:.2f}"])
    
    cursor.execute("SELECT COUNT(*), AVG(rating) FROM reviews")
    reviews_stats = cursor.fetchone()
    stats.append(["Total Reviews", reviews_stats[0]])
    stats.append(["Average Rating", f"{reviews_stats[1]:.1f}/5.0"])
    
    cursor.execute("SELECT COUNT(*) FROM products WHERE stock_quantity < min_stock_level")
    low_stock = cursor.fetchone()[0]
    stats.append(["Products Low on Stock", low_stock])
    
    print(tabulate(stats, headers=['Metric', 'Value'], tablefmt='grid'))

    conn.close()

if __name__ == "__main__":
    view_data()
