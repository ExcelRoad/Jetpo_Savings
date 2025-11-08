"""
Clear all fund-related data before running full sync
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from funds.models import Company, Fund, FundSnapshot, FundLike
from portfolios.models import PortfolioHolding

print("="*80)
print("Clearing All Fund Data")
print("="*80)

print("\nCurrent counts:")
print(f"  Portfolio Holdings: {PortfolioHolding.objects.count()}")
print(f"  Fund Likes: {FundLike.objects.count()}")
print(f"  Fund Snapshots: {FundSnapshot.objects.count()}")
print(f"  Funds: {Fund.objects.count()}")
print(f"  Companies: {Company.objects.count()}")

print("\nDeleting data...")

# Delete in correct order (respecting foreign keys)
holdings_deleted = PortfolioHolding.objects.all().delete()[0]
print(f"  [OK] Deleted {holdings_deleted} portfolio holdings")

likes_deleted = FundLike.objects.all().delete()[0]
print(f"  [OK] Deleted {likes_deleted} fund likes")

snapshots_deleted = FundSnapshot.objects.all().delete()[0]
print(f"  [OK] Deleted {snapshots_deleted} fund snapshots")

funds_deleted = Fund.objects.all().delete()[0]
print(f"  [OK] Deleted {funds_deleted} funds")

companies_deleted = Company.objects.all().delete()[0]
print(f"  [OK] Deleted {companies_deleted} companies")

print("\nFinal counts:")
print(f"  Portfolio Holdings: {PortfolioHolding.objects.count()}")
print(f"  Fund Likes: {FundLike.objects.count()}")
print(f"  Fund Snapshots: {FundSnapshot.objects.count()}")
print(f"  Funds: {Fund.objects.count()}")
print(f"  Companies: {Company.objects.count()}")

print("\n" + "="*80)
print("All fund data cleared successfully!")
print("="*80)
