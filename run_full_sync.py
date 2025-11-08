"""
Run FULL sync with ALL data from Gemelnet API
"""
import os
import django
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from funds.gemelnet_sync_v2 import sync_gemelnet_data_with_history
from funds.models import Company, Fund, FundSnapshot

print("="*80)
print("FULL HISTORICAL SYNC - ALL DATA FROM API")
print("="*80)

print("\nBefore sync:")
print(f"  Companies: {Company.objects.count()}")
print(f"  Funds: {Fund.objects.count()}")
print(f"  Snapshots: {FundSnapshot.objects.count()}")

print("\n" + "="*80)
print("Starting FULL sync (this will take a few minutes)...")
print("="*80)

start_time = time.time()

try:
    # Run with NO LIMIT to get all data
    result = sync_gemelnet_data_with_history(limit=None)

    elapsed = time.time() - start_time

    print("\n" + "="*80)
    print("SYNC COMPLETED SUCCESSFULLY!")
    print("="*80)
    print(f"Total time: {elapsed/60:.2f} minutes ({elapsed:.1f} seconds)")

    print("\nAfter sync:")
    print(f"  Companies: {Company.objects.count()}")
    print(f"  Funds: {Fund.objects.count()}")
    print(f"  Snapshots: {FundSnapshot.objects.count()}")

    # Show some statistics
    print("\n" + "="*80)
    print("DATABASE STATISTICS")
    print("="*80)

    # Companies
    companies_with_most_funds = Company.objects.annotate(
        fund_count=models.Count('funds')
    ).order_by('-fund_count')[:5]

    from django.db.models import Count

    print("\nTop 5 Companies by Number of Funds:")
    for company in companies_with_most_funds:
        print(f"  {company.name[:50]}: {company.funds.count()} funds")

    # Funds with most historical data
    from django.db.models import Count as ModelCount
    funds_with_most_snapshots = Fund.objects.annotate(
        snapshot_count=ModelCount('snapshots')
    ).order_by('-snapshot_count')[:5]

    print("\nFunds with Most Historical Data:")
    for fund in funds_with_most_snapshots:
        print(f"  {fund.name[:50]}: {fund.snapshots.count()} periods")

    # Period distribution
    from django.db.models import Count as ModelCount2
    period_distribution = FundSnapshot.objects.values('report_period').annotate(
        count=ModelCount2('id')
    ).order_by('-report_period')[:12]

    print("\nLatest 12 Periods:")
    for period in period_distribution:
        year = str(period['report_period'])[:4]
        month = str(period['report_period'])[4:6]
        print(f"  {month}/{year}: {period['count']} snapshots")

except Exception as e:
    print(f"\n[ERROR] Sync failed: {e}")
    import traceback
    traceback.print_exc()
