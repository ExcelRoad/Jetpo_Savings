"""
Test the optimized sync function - run twice to see the optimization in action
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from funds.gemelnet_sync_v2 import sync_gemelnet_data_with_history
from funds.models import Company, Fund, FundSnapshot
import time

print("="*80)
print("Testing OPTIMIZED Sync Function")
print("="*80)

print("\nBefore any sync:")
print(f"  Companies: {Company.objects.count()}")
print(f"  Funds: {Fund.objects.count()}")
print(f"  Snapshots: {FundSnapshot.objects.count()}")

# First run - should create everything
print("\n" + "="*80)
print("FIRST RUN - Creating new data")
print("="*80)
start = time.time()
result1 = sync_gemelnet_data_with_history(limit=500)
time1 = time.time() - start

print(f"\nFirst run took: {time1:.2f} seconds")

print("\nAfter first sync:")
print(f"  Companies: {Company.objects.count()}")
print(f"  Funds: {Fund.objects.count()}")
print(f"  Snapshots: {FundSnapshot.objects.count()}")

# Second run - should skip all existing
print("\n" + "="*80)
print("SECOND RUN - Should skip existing snapshots")
print("="*80)
start = time.time()
result2 = sync_gemelnet_data_with_history(limit=500)
time2 = time.time() - start

print(f"\nSecond run took: {time2:.2f} seconds")
print(f"Speedup: {time1/time2:.2f}x faster!")

print("\nAfter second sync:")
print(f"  Companies: {Company.objects.count()}")
print(f"  Funds: {Fund.objects.count()}")
print(f"  Snapshots: {FundSnapshot.objects.count()}")

# Comparison
print("\n" + "="*80)
print("OPTIMIZATION RESULTS")
print("="*80)
print(f"First run:  {result1['snapshots_created']:,} created, {result1['snapshots_skipped']:,} skipped")
print(f"Second run: {result2['snapshots_created']:,} created, {result2['snapshots_skipped']:,} skipped")
print(f"\nTime saved on second run: {time1 - time2:.2f} seconds ({((time1-time2)/time1)*100:.1f}% faster)")
