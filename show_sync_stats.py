"""
Show statistics after full sync
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db.models import Count, Avg, Max, Min
from funds.models import Company, Fund, FundSnapshot

print("="*80)
print("DATABASE STATISTICS AFTER FULL SYNC")
print("="*80)

print(f"\nTotal Counts:")
print(f"  Companies: {Company.objects.count()}")
print(f"  Funds: {Fund.objects.count()}")
print(f"  Snapshots: {FundSnapshot.objects.count()}")

# Companies
print("\n" + "="*80)
print("Top 10 Companies by Number of Funds:")
print("="*80)
companies_with_most_funds = Company.objects.annotate(
    fund_count=Count('funds')
).order_by('-fund_count')[:10]

for i, company in enumerate(companies_with_most_funds, 1):
    print(f"{i:2}. {company.name[:60]:<60} {company.fund_count:3} funds")

# Funds with most historical data
print("\n" + "="*80)
print("Funds with Most Historical Periods:")
print("="*80)
funds_with_most_snapshots = Fund.objects.annotate(
    snapshot_count=Count('snapshots')
).order_by('-snapshot_count')[:10]

for i, fund in enumerate(funds_with_most_snapshots, 1):
    print(f"{i:2}. {fund.name[:60]:<60} {fund.snapshots.count():2} periods")

# Period distribution
print("\n" + "="*80)
print("Period Distribution (Latest 20 Months):")
print("="*80)
period_distribution = FundSnapshot.objects.values('report_period').annotate(
    count=Count('id')
).order_by('-report_period')[:20]

for period in period_distribution:
    year = str(period['report_period'])[:4]
    month = str(period['report_period'])[4:6]
    print(f"  {month}/{year}: {period['count']:4} snapshots")

# Average statistics
print("\n" + "="*80)
print("Average Statistics:")
print("="*80)
avg_stats = FundSnapshot.objects.aggregate(
    avg_return_5yr=Avg('avg_annual_return_5yr'),
    max_return_5yr=Max('avg_annual_return_5yr'),
    min_return_5yr=Min('avg_annual_return_5yr'),
    avg_assets=Avg('total_assets'),
)

print(f"  Average 5-year return: {avg_stats['avg_return_5yr']:.2f}%")
print(f"  Best 5-year return: {avg_stats['max_return_5yr']:.2f}%")
print(f"  Worst 5-year return: {avg_stats['min_return_5yr']:.2f}%")
print(f"  Average assets: {avg_stats['avg_assets']:.2f}M ILS")

# Sample fund with full history
print("\n" + "="*80)
print("Sample Fund with Full Historical Data:")
print("="*80)
sample_fund = Fund.objects.annotate(
    snapshot_count=Count('snapshots')
).filter(snapshot_count__gt=15).first()

if sample_fund:
    print(f"\nFund: {sample_fund.name}")
    print(f"Company: {sample_fund.company.name}")
    print(f"Latest Return Rate: {sample_fund.return_rate}%")
    print(f"Total Historical Periods: {sample_fund.snapshots.count()}")

    print(f"\nLast 6 months of data:")
    recent_snapshots = sample_fund.snapshots.order_by('-report_period')[:6]
    for snap in recent_snapshots:
        year = str(snap.report_period)[:4]
        month = str(snap.report_period)[4:6]
        print(f"  {month}/{year}: Monthly={snap.monthly_yield:6.2f}%, YTD={snap.ytd_yield:6.2f}%, Assets={snap.total_assets:8.2f}M")

print("\n" + "="*80)
print("FULL SYNC COMPLETE!")
print("="*80)
