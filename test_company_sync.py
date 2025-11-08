"""
Test the updated sync function with Company model
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from funds.gemelnet_sync import sync_gemelnet_data
from funds.models import Company, Fund

print("="*80)
print("Testing Updated Sync Function with Company Model")
print("="*80)

print("\nBefore sync:")
print(f"  Companies: {Company.objects.count()}")
print(f"  Funds: {Fund.objects.count()}")

print("\n" + "="*80)
print("Running sync with 100 records (test mode)...")
print("="*80)

try:
    result = sync_gemelnet_data(limit=100)

    print("\n" + "="*80)
    print("After sync:")
    print("="*80)
    print(f"  Companies: {Company.objects.count()}")
    print(f"  Funds: {Fund.objects.count()}")

    print("\n" + "="*80)
    print("Sample Companies:")
    print("="*80)
    for company in Company.objects.all()[:5]:
        print(f"  {company.name} (Legal ID: {company.legal_id})")
        print(f"    Funds managed: {company.get_funds_count()}")

    print("\n" + "="*80)
    print("Sample Funds:")
    print("="*80)
    for fund in Fund.objects.all()[:3]:
        print(f"  {fund.name[:60]}")
        print(f"    Company: {fund.company.name}")
        print(f"    Return Rate: {fund.return_rate}%")
        print(f"    Report Period: {fund.report_period}")
        print()

except Exception as e:
    print(f"\n[ERROR] Sync failed: {e}")
    import traceback
    traceback.print_exc()
