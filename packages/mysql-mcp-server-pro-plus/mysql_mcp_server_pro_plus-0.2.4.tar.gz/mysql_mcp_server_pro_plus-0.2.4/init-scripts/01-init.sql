-- MySQL MCP Server Pro Plus - Complex E-commerce Database Simulation
-- This script creates a realistic but problematic database structure for testing MCP capabilities

-- BAD PRACTICE 1: No proper database creation with character set
CREATE DATABASE IF NOT EXISTS ecommerce_db;

-- BAD PRACTICE 2: Using root user instead of dedicated user
USE ecommerce_db;

-- BAD PRACTICE 3: Inconsistent naming conventions and no proper constraints
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL, -- BAD: Plain text passwords
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    phone VARCHAR(20),
    address TEXT,
    credit_card VARCHAR(16), -- BAD: Storing credit card numbers in plain text
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL
);

-- BAD PRACTICE 4: No foreign key constraints, inconsistent data types
CREATE TABLE IF NOT EXISTS categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    parent_category_id INT, -- BAD: No foreign key constraint
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- BAD PRACTICE 5: Poor table design, missing indexes on frequently queried columns
CREATE TABLE IF NOT EXISTS products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description LONGTEXT,
    price DECIMAL(10,2) NOT NULL,
    cost_price DECIMAL(10,2),
    category_id INT, -- BAD: No foreign key constraint
    sku VARCHAR(50),
    weight DECIMAL(8,2),
    dimensions VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- BAD PRACTICE 6: Denormalized table with redundant data
CREATE TABLE IF NOT EXISTS inventory (
    inventory_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT, -- BAD: No foreign key constraint
    warehouse_id INT,
    quantity INT DEFAULT 0,
    min_quantity INT DEFAULT 0,
    max_quantity INT DEFAULT 1000,
    product_name VARCHAR(200), -- BAD: Redundant data
    product_price DECIMAL(10,2), -- BAD: Redundant data
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- BAD PRACTICE 7: No proper order status management
CREATE TABLE IF NOT EXISTS orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT, -- BAD: No foreign key constraint
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(12,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- BAD: No enum constraint
    shipping_address TEXT,
    billing_address TEXT,
    payment_method VARCHAR(50),
    tracking_number VARCHAR(100),
    notes TEXT
);

-- BAD PRACTICE 8: Missing important constraints and indexes
CREATE TABLE IF NOT EXISTS order_items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT, -- BAD: No foreign key constraint
    product_id INT, -- BAD: No foreign key constraint
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    product_name VARCHAR(200), -- BAD: Redundant data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- BAD PRACTICE 9: No proper review validation
CREATE TABLE IF NOT EXISTS reviews (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT, -- BAD: No foreign key constraint
    user_id INT, -- BAD: No foreign key constraint
    rating INT CHECK (rating >= 1 AND rating <= 5), -- BAD: Check constraint but no foreign keys
    title VARCHAR(200),
    comment TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    helpful_votes INT DEFAULT 0
);

-- BAD PRACTICE 10: Sensitive payment information in plain text
CREATE TABLE IF NOT EXISTS payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT, -- BAD: No foreign key constraint
    amount DECIMAL(12,2) NOT NULL,
    payment_method VARCHAR(50),
    card_number VARCHAR(16), -- BAD: Plain text credit card numbers
    card_expiry VARCHAR(5),
    cvv VARCHAR(4), -- BAD: Storing CVV
    transaction_id VARCHAR(100),
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- BAD PRACTICE 11: Overly permissive permissions
GRANT ALL PRIVILEGES ON ecommerce_db.* TO 'mcp_user'@'%';
GRANT ALL PRIVILEGES ON *.* TO 'mcp_user'@'%'; -- BAD: Global privileges
FLUSH PRIVILEGES;

-- BAD PRACTICE 12: No proper indexes on frequently queried columns
-- Missing indexes on: users.email, products.category_id, orders.user_id, order_items.order_id

-- BAD PRACTICE 13: Inserting test data with SQL injection patterns
INSERT INTO users (username, email, password, first_name, last_name, phone, credit_card) VALUES
('admin', 'admin@test.com', 'admin123', 'Admin', 'User', '1234567890', '1234567890123456'),
('user1', 'user1@test.com', 'password123', 'John', 'Doe', '1234567891', '1234567890123457'),
('user2', 'user2@test.com', 'password456', 'Jane', 'Smith', '1234567892', '1234567890123458'),
('test_user', 'test@test.com', 'test123', 'Test', 'User', '1234567893', '1234567890123459'),
('demo_user', 'demo@test.com', 'demo123', 'Demo', 'User', '1234567894', '1234567890123460');

-- BAD PRACTICE 14: Inserting data with potential SQL injection patterns
INSERT INTO categories (name, description, parent_category_id) VALUES
('Electronics', 'Electronic devices and gadgets', NULL),
('Clothing', 'Apparel and fashion items', NULL),
('Books', 'Books and publications', NULL),
('Home & Garden', 'Home improvement and garden items', NULL),
('Sports', 'Sports equipment and accessories', NULL),
('Electronics > Computers', 'Computers and laptops', 1),
('Electronics > Phones', 'Mobile phones and accessories', 1),
('Clothing > Men', 'Men''s clothing', 2),
('Clothing > Women', 'Women''s clothing', 2),
('Books > Fiction', 'Fiction books', 3);

-- BAD PRACTICE 15: Inserting products with inconsistent data
INSERT INTO products (name, description, price, cost_price, category_id, sku, weight) VALUES
('Laptop Pro', 'High-performance laptop for professionals', 1299.99, 800.00, 6, 'LAP001', 2.5),
('Smartphone X', 'Latest smartphone with advanced features', 899.99, 600.00, 7, 'PHN001', 0.3),
('T-Shirt Classic', 'Comfortable cotton t-shirt', 19.99, 8.00, 8, 'TSH001', 0.2),
('Novel Adventure', 'Exciting adventure novel', 12.99, 5.00, 10, 'BOK001', 0.5),
('Garden Tool Set', 'Complete garden maintenance kit', 89.99, 45.00, 4, 'GRD001', 3.0),
('Basketball', 'Professional basketball', 29.99, 15.00, 5, 'SPT001', 0.6),
('Wireless Headphones', 'Noise-cancelling wireless headphones', 199.99, 120.00, 1, 'AUD001', 0.4),
('Running Shoes', 'Comfortable running shoes', 79.99, 35.00, 5, 'SHO001', 0.8),
('Coffee Maker', 'Automatic coffee maker', 149.99, 80.00, 4, 'KIT001', 2.2),
('Desk Lamp', 'LED desk lamp with adjustable brightness', 39.99, 20.00, 4, 'LIT001', 1.1);

-- Show created tables
SHOW TABLES;

-- BAD PRACTICE 16: No proper error handling or transaction management
-- The following will be used for generating 10M rows and 1M transactions
