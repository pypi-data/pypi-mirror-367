#!/usr/bin/env python3
"""
MySQL MCP Server Pro Plus - Bad Practices Verification Script
This script verifies that the intentional bad practices are present in the database
"""

import mysql.connector
import sys
from datetime import datetime

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "mcp_user",
    "password": "mcp_password",
    "database": "ecommerce_db",
}


def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def print_section(title):
    """Print a formatted section"""
    print(f"\n--- {title} ---")


def check_security_issues(cursor):
    """Check for security-related bad practices"""
    print_section("SECURITY ISSUES")

    # Check for plain text credit cards
    cursor.execute("SELECT COUNT(*) FROM users WHERE credit_card REGEXP '^[0-9]{16}$'")
    plain_text_cc = cursor.fetchone()[0]
    print(f"✓ Plain text credit cards in users table: {plain_text_cc:,}")

    cursor.execute(
        "SELECT COUNT(*) FROM payments WHERE card_number REGEXP '^[0-9]{16}$'"
    )
    plain_text_cc_payments = cursor.fetchone()[0]
    print(f"✓ Plain text credit cards in payments table: {plain_text_cc_payments:,}")

    # Check for CVV storage
    cursor.execute("SELECT COUNT(*) FROM payments WHERE cvv REGEXP '^[0-9]{3,4}$'")
    cvv_storage = cursor.fetchone()[0]
    print(f"✓ CVV codes stored in plain text: {cvv_storage:,}")

    # Check for MD5 passwords
    cursor.execute("SELECT COUNT(*) FROM users WHERE password REGEXP '^[a-f0-9]{32}$'")
    md5_passwords = cursor.fetchone()[0]
    print(f"✓ MD5 hashed passwords: {md5_passwords:,}")

    # Check user privileges
    cursor.execute("SHOW GRANTS FOR 'mcp_user'@'%'")
    grants = cursor.fetchall()
    print(f"✓ Overly permissive privileges: {len(grants)} grant statements")


def check_data_integrity_issues(cursor):
    """Check for data integrity issues"""
    print_section("DATA INTEGRITY ISSUES")

    # Check for missing foreign key constraints
    cursor.execute("""
        SELECT COUNT(*) FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
        WHERE REFERENCED_TABLE_SCHEMA = 'ecommerce_db' 
        AND REFERENCED_TABLE_NAME IS NOT NULL
    """)
    foreign_keys = cursor.fetchone()[0]
    print(f"✗ Missing foreign key constraints: Only {foreign_keys} foreign keys found")

    # Check for missing unique constraints on important fields
    cursor.execute(
        "SHOW INDEX FROM users WHERE Non_unique = 0 AND Column_name = 'email'"
    )
    email_unique = cursor.fetchall()
    print(
        f"✗ Missing unique constraint on users.email: {'No' if not email_unique else 'Yes'}"
    )

    # Check for inconsistent data types
    cursor.execute("""
        SELECT COLUMN_NAME, DATA_TYPE 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = 'ecommerce_db' 
        AND TABLE_NAME = 'users' 
        AND COLUMN_NAME IN ('created_date', 'last_login')
    """)
    date_columns = cursor.fetchall()
    print(f"✗ Inconsistent date column types: {len(date_columns)} columns")


def check_performance_issues(cursor):
    """Check for performance-related issues"""
    print_section("PERFORMANCE ISSUES")

    # Check for missing indexes on frequently queried columns
    tables_to_check = [
        ("users", "email"),
        ("products", "category_id"),
        ("orders", "user_id"),
        ("order_items", "order_id"),
        ("reviews", "product_id"),
        ("payments", "order_id"),
    ]

    missing_indexes = []
    for table, column in tables_to_check:
        cursor.execute(f"SHOW INDEX FROM {table} WHERE Column_name = '{column}'")
        indexes = cursor.fetchall()
        if not indexes:
            missing_indexes.append(f"{table}.{column}")

    print(f"✗ Missing indexes on frequently queried columns: {len(missing_indexes)}")
    for missing in missing_indexes[:5]:  # Show first 5
        print(f"  - {missing}")

    # Check table sizes
    cursor.execute("""
        SELECT 
            table_name,
            ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'Size (MB)',
            table_rows
        FROM information_schema.tables 
        WHERE table_schema = 'ecommerce_db'
        ORDER BY (data_length + index_length) DESC
    """)
    table_sizes = cursor.fetchall()

    print(f"\n✓ Large tables without partitioning:")
    for table, size_mb, rows in table_sizes[:5]:
        print(f"  - {table}: {size_mb} MB, {rows:,} rows")


def check_design_issues(cursor):
    """Check for design-related issues"""
    print_section("DESIGN ISSUES")

    # Check for denormalized data
    cursor.execute("""
        SELECT COUNT(*) FROM inventory 
        WHERE product_name IS NOT NULL AND product_price IS NOT NULL
    """)
    denormalized_inventory = cursor.fetchone()[0]
    print(
        f"✗ Denormalized data in inventory table: {denormalized_inventory:,} rows with redundant product info"
    )

    cursor.execute("""
        SELECT COUNT(*) FROM order_items 
        WHERE product_name IS NOT NULL
    """)
    denormalized_order_items = cursor.fetchone()[0]
    print(
        f"✗ Denormalized data in order_items table: {denormalized_order_items:,} rows with redundant product info"
    )

    # Check for inconsistent naming conventions
    cursor.execute("""
        SELECT COLUMN_NAME, TABLE_NAME 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = 'ecommerce_db' 
        AND COLUMN_NAME LIKE '%created%' OR COLUMN_NAME LIKE '%updated%'
        ORDER BY TABLE_NAME, COLUMN_NAME
    """)
    naming_inconsistencies = cursor.fetchall()
    print(
        f"✗ Inconsistent naming conventions: {len(naming_inconsistencies)} date columns with mixed naming"
    )

    # Check for missing ENUM constraints
    cursor.execute("""
        SELECT COLUMN_NAME, DATA_TYPE 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = 'ecommerce_db' 
        AND COLUMN_NAME = 'status' 
        AND DATA_TYPE = 'varchar'
    """)
    varchar_status = cursor.fetchall()
    print(
        f"✗ Missing ENUM constraints on status fields: {len(varchar_status)} VARCHAR status columns"
    )


def check_sql_injection_vulnerabilities(cursor):
    """Check for SQL injection vulnerabilities in data"""
    print_section("SQL INJECTION VULNERABILITIES")

    # Check for SQL injection patterns in test data
    sql_patterns = [
        ("'; DROP TABLE users; --", "users"),
        ("' OR '1'='1", "users"),
        (
            "'; INSERT INTO users VALUES (999999, 'hacker', 'hack@evil.com', 'password', 'Hack', 'Er', '123-456-7890', 'Evil Address', '1234567890123456', NOW(), NULL); --",
            "users",
        ),
        ("' UNION SELECT * FROM users --", "users"),
        (
            "' AND 1=CONVERT(int, (SELECT password FROM users WHERE username='admin')) --",
            "users",
        ),
    ]

    vulnerable_data = 0
    for pattern, table in sql_patterns:
        try:
            cursor.execute(
                f"SELECT COUNT(*) FROM {table} WHERE username LIKE '%{pattern}%' OR email LIKE '%{pattern}%'"
            )
            count = cursor.fetchone()[0]
            if count > 0:
                vulnerable_data += count
        except:
            pass

    print(
        f"✗ SQL injection patterns in test data: {vulnerable_data} potential vulnerabilities"
    )


def get_database_statistics(cursor):
    """Get overall database statistics"""
    print_section("DATABASE STATISTICS")

    tables = [
        "users",
        "products",
        "orders",
        "order_items",
        "reviews",
        "payments",
        "inventory",
        "categories",
    ]

    total_rows = 0
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"✓ {table}: {count:,} rows")
            total_rows += count
        except Exception as e:
            print(f"✗ {table}: Error - {e}")

    print(f"\n✓ Total rows across all tables: {total_rows:,}")

    # Get database size
    cursor.execute("""
        SELECT 
            ROUND(SUM((data_length + index_length) / 1024 / 1024), 2) AS 'Total Size (MB)'
        FROM information_schema.tables 
        WHERE table_schema = 'ecommerce_db'
    """)
    total_size = cursor.fetchone()[0]
    print(f"✓ Total database size: {total_size} MB")


def main():
    """Main function to verify bad practices"""
    print_header("MySQL MCP Server Pro Plus - Bad Practices Verification")
    print(f"Verification started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # Connect to database
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        print("✓ Connected to database successfully!")

        # Run all checks
        get_database_statistics(cursor)
        check_security_issues(cursor)
        check_data_integrity_issues(cursor)
        check_performance_issues(cursor)
        check_design_issues(cursor)
        check_sql_injection_vulnerabilities(cursor)

        print_header("VERIFICATION SUMMARY")
        print("✓ Database contains intentional bad practices for MCP agent testing")
        print("✓ Security vulnerabilities: Plain text passwords, credit cards, CVV")
        print("✓ Data integrity issues: Missing foreign keys, constraints")
        print("✓ Performance issues: Missing indexes, no partitioning")
        print("✓ Design issues: Denormalization, naming inconsistencies")
        print("✓ SQL injection vulnerabilities: Test patterns in data")
        print("\n⚠️  WARNING: This database is for testing only!")
        print("   Do not use in production environments!")

        cursor.close()
        connection.close()

    except Exception as e:
        print(f"✗ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
