"""
Check fund categories after update
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from funds.models import Fund

print("=" * 80)
print("FUND CATEGORIES FROM API")
print("=" * 80)

categories = Fund.objects.exclude(category='').values_list('category', flat=True).distinct().order_by('category')

print(f"\nTotal distinct categories: {len(categories)}")
print("\nCategories:")
for cat in categories:
    count = Fund.objects.filter(category=cat).count()
    print(f"  {cat}: {count} funds")

print("\n" + "=" * 80)
print("Sample funds with categories:")
print("=" * 80)

sample_funds = Fund.objects.exclude(category='').select_related('company')[:10]
for fund in sample_funds:
    print(f"\n{fund.name}")
    print(f"  Company: {fund.company.name}")
    print(f"  Category: {fund.category}")
    print(f"  Classification: {fund.fund_classification}")
