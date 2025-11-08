"""
Test historical sync with all periods
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from funds.gemelnet_sync_v2 import sync_gemelnet_data_with_history
from funds.models import Company, Fund, FundSnapshot

print("="*80)
print("Testing FULL HISTORICAL Sync")
print("="*80)

print("\nBefore sync:")
print(f"  Companies: {Company.objects.count()}")
print(f"  Funds: {Fund.objects.count()}")
print(f"  Snapshots: {FundSnapshot.objects.count()}")

print("\n" + "="*80)
print("Running historical sync with 500 records...")
print("="*80)

try:
    result = sync_gemelnet_data_with_history(limit=500)

    print("\n" + "="*80)
    print("After sync:")
    print("="*80)
    print(f"  Companies: {Company.objects.count()}")
    print(f"  Funds: {Fund.objects.count()}")
    print(f"  Snapshots: {FundSnapshot.objects.count()}")

    # Show example fund with its historical data
    print("\n" + "="*80)
    print("Example: Fund with Historical Data")
    print("="*80)

    fund = Fund.objects.first()
    if fund:
        print(f"\nFund: {fund.name[:60]}")
        print(f"Company: {fund.company.name}")
        print(f"Latest Report Period: {fund.latest_report_period}")
        print(f"Latest Return Rate: {fund.return_rate}%")

        snapshots = fund.snapshots.order_by('report_period')[:5]
        print(f"\nFirst 5 historical snapshots:")
        for snap in snapshots:
            print(f"  {snap.report_period}: Monthly Yield={snap.monthly_yield}%, YTD={snap.ytd_yield}%, Assets=₪{snap.total_assets}M")

        print(f"\nTotal snapshots for this fund: {fund.snapshots.count()}")

except Exception as e:
    print(f"\n[ERROR] Sync failed: {e}")
    import traceback
    traceback.print_exc()
