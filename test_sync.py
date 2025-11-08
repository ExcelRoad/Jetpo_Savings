"""
Test script to test the Gemelnet sync function with a small sample.
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from funds.gemelnet_sync import sync_gemelnet_data
from funds.models import Fund

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("Testing Gemelnet Sync Function")
    print("=" * 80)
    print("\nThis will fetch a small sample (100 records) to test the sync function.")
    print("Press Ctrl+C to cancel, or Enter to continue...")
    input()

    # Show current fund count
    initial_count = Fund.objects.count()
    print(f"\nCurrent number of funds in database: {initial_count}")

    # Run sync with limit of 100 records (will result in fewer unique funds)
    print("\nStarting sync with limit=100...")
    try:
        result = sync_gemelnet_data(limit=100)

        # Show results
        print("\n" + "=" * 80)
        print("Test Results")
        print("=" * 80)
        print(f"Initial fund count:  {initial_count}")
        print(f"Final fund count:    {Fund.objects.count()}")
        print(f"New funds created:   {result['created']}")
        print(f"Funds updated:       {result['updated']}")
        print(f"Errors:              {result['errors']}")
        print("=" * 80)

        # Show sample of synced funds
        print("\nSample of funds with Gemelnet data:")
        synced_funds = Fund.objects.filter(fund_id__isnull=False)[:5]
        for fund in synced_funds:
            print(f"\n  Fund: {fund.name[:60]}...")
            print(f"    Company: {fund.company}")
            print(f"    Return Rate: {fund.return_rate}%")
            print(f"    Total Assets: {fund.total_assets} million")
            print(f"    Report Period: {fund.report_period}")

    except Exception as e:
        print(f"\n[ERROR] Sync failed: {e}")
        import traceback
        traceback.print_exc()
