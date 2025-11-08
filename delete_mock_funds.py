"""
Delete all existing mock funds before migration
"""
import sqlite3

# Connect to the database
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Delete all funds
cursor.execute("DELETE FROM funds_fund")
cursor.execute("DELETE FROM funds_fundlike")
cursor.execute("DELETE FROM portfolios_portfolioholding")

conn.commit()

# Check counts
cursor.execute("SELECT COUNT(*) FROM funds_fund")
fund_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM funds_fundlike")
like_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM portfolios_portfolioholding")
holding_count = cursor.fetchone()[0]

print(f"Funds remaining: {fund_count}")
print(f"Likes remaining: {like_count}")
print(f"Holdings remaining: {holding_count}")

conn.close()
print("\nAll mock data deleted successfully!")
