"""
Dry run test script for Gemelnet sync - prints results without saving to database.
This allows you to see what would happen without actually modifying the database.
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import requests
from datetime import datetime
from decimal import Decimal


# Gemelnet API Configuration
GEMELNET_API_URL = "https://data.gov.il/api/3/action/datastore_search"
GEMELNET_RESOURCE_ID = "a30dcbea-a1d2-482c-ae29-8f781f5025fb"


def fetch_gemelnet_data(limit=None):
    """Fetch fund data from the Gemelnet API."""
    all_records = []
    offset = 0
    batch_size = 1000

    print(f"\n{'='*80}")
    print("STEP 1: FETCHING DATA FROM API")
    print(f"{'='*80}")
    print(f"API URL: {GEMELNET_API_URL}")
    print(f"Resource ID: {GEMELNET_RESOURCE_ID}")
    print(f"Fetch limit: {limit if limit else 'All records'}")

    while True:
        params = {
            'resource_id': GEMELNET_RESOURCE_ID,
            'limit': limit if limit else batch_size,
            'offset': offset
        }

        try:
            print(f"\nFetching batch starting at offset {offset}...")
            response = requests.get(GEMELNET_API_URL, params=params, timeout=60)
            response.raise_for_status()

            data = response.json()

            if not data.get('success'):
                raise Exception(f"API returned unsuccessful response: {data}")

            result = data.get('result', {})
            records = result.get('records', [])
            total = result.get('total', 0)

            if not records:
                break

            all_records.extend(records)

            print(f"  -> Fetched {len(records)} records (Total so far: {len(all_records):,} / {total:,})")

            # If we have a limit or we've fetched all records, stop
            if limit or len(all_records) >= total:
                break

            offset += batch_size

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to fetch data: {e}")
            raise

    print(f"\n[SUCCESS] Fetched {len(all_records):,} total records from API")
    return all_records


def get_latest_period_data(records):
    """Filter records to get only the latest report period for each fund."""
    print(f"\n{'='*80}")
    print("STEP 2: FILTERING TO LATEST PERIOD PER FUND")
    print(f"{'='*80}")

    latest_records = {}
    period_stats = {}

    for record in records:
        fund_id = str(record.get('FUND_ID'))
        report_period = record.get('REPORT_PERIOD')

        if not fund_id or not report_period:
            continue

        # Track periods
        if report_period not in period_stats:
            period_stats[report_period] = 0
        period_stats[report_period] += 1

        # Keep latest
        if (fund_id not in latest_records or
            report_period > latest_records[fund_id].get('REPORT_PERIOD')):
            latest_records[fund_id] = record

    # Show period distribution
    print(f"\nReport periods found in data:")
    for period in sorted(period_stats.keys()):
        print(f"  Period {period}: {period_stats[period]:,} records")

    print(f"\n[SUCCESS] Found {len(latest_records):,} unique funds")

    return latest_records


def parse_date(date_string):
    """Parse date string from API format."""
    if not date_string:
        return None
    try:
        dt = datetime.strptime(date_string.split()[0], "%Y-%m-%d")
        return dt.date()
    except (ValueError, IndexError):
        return None


def safe_decimal(value, default=None):
    """Safely convert a value to Decimal."""
    if value is None or value == '':
        return default
    try:
        return Decimal(str(value))
    except (ValueError, TypeError):
        return default


def dry_run_sync(records_dict, show_sample=5):
    """
    Simulate the sync process without saving to database.
    Shows what would be created/updated.
    """
    print(f"\n{'='*80}")
    print("STEP 3: PROCESSING FUNDS (DRY RUN - NO DATABASE CHANGES)")
    print(f"{'='*80}")

    stats = {
        'total_processed': 0,
        'would_create': 0,
        'would_update': 0,
        'errors': 0,
        'samples': []
    }

    # Check which funds already exist in database
    from funds.models import Fund
    existing_fund_ids = set(
        Fund.objects.filter(fund_id__isnull=False)
        .values_list('fund_id', flat=True)
    )
    print(f"\nCurrently in database: {len(existing_fund_ids)} funds with Gemelnet fund_id")

    print(f"\nProcessing {len(records_dict):,} funds...")

    for fund_id, record in records_dict.items():
        try:
            # Extract data
            fund_data = {
                'fund_id': fund_id,
                'name': record.get('FUND_NAME', ''),
                'company': record.get('MANAGING_CORPORATION', ''),
                'fund_classification': record.get('FUND_CLASSIFICATION', ''),
                'specialization': record.get('SPECIALIZATION', ''),
                'sub_specialization': record.get('SUB_SPECIALIZATION', ''),
                'return_rate': safe_decimal(record.get('AVG_ANNUAL_YIELD_TRAILING_5YRS'), Decimal('0')),
                'monthly_yield': safe_decimal(record.get('MONTHLY_YIELD')),
                'ytd_yield': safe_decimal(record.get('YEAR_TO_DATE_YIELD')),
                'total_assets': safe_decimal(record.get('TOTAL_ASSETS')),
                'inception_date': parse_date(record.get('INCEPTION_DATE')),
                'management_fee': safe_decimal(record.get('AVG_ANNUAL_MANAGEMENT_FEE')),
                'report_period': record.get('REPORT_PERIOD'),
            }

            # Determine if would create or update
            would_create = fund_id not in existing_fund_ids

            if would_create:
                stats['would_create'] += 1
            else:
                stats['would_update'] += 1

            stats['total_processed'] += 1

            # Store samples
            if len(stats['samples']) < show_sample:
                stats['samples'].append({
                    'action': 'CREATE' if would_create else 'UPDATE',
                    'data': fund_data
                })

            # Progress indicator
            if stats['total_processed'] % 500 == 0:
                print(f"  Processed {stats['total_processed']:,} funds...")

        except Exception as e:
            stats['errors'] += 1
            if stats['errors'] <= 3:  # Show first 3 errors
                print(f"  [ERROR] Fund {fund_id}: {e}")

    return stats


def main():
    """Main dry run function."""
    print("\n" + "="*80)
    print("GEMELNET SYNC - DRY RUN MODE")
    print("="*80)
    print("\nThis will fetch data and show what would happen WITHOUT saving to database.")
    print("\nFetch options:")
    print("1. Small sample (100 records)")
    print("2. Medium sample (1000 records)")
    print("3. All data (~19,000 records)")

    choice = input("\nEnter choice (1-3) or press Enter for small sample: ").strip()

    if choice == '3':
        limit = None
        print("\n[INFO] Fetching ALL data - this will take 1-2 minutes...")
    elif choice == '2':
        limit = 1000
        print("\n[INFO] Fetching 1000 records...")
    else:
        limit = 100
        print("\n[INFO] Fetching 100 records...")

    try:
        # Step 1: Fetch data
        records = fetch_gemelnet_data(limit=limit)

        if not records:
            print("\n[ERROR] No records fetched")
            return

        # Step 2: Get latest period per fund
        latest_records = get_latest_period_data(records)

        # Step 3: Dry run sync
        stats = dry_run_sync(latest_records, show_sample=5)

        # Print summary
        print(f"\n{'='*80}")
        print("DRY RUN SUMMARY")
        print(f"{'='*80}")
        print(f"Total records fetched:     {len(records):,}")
        print(f"Unique funds found:        {len(latest_records):,}")
        print(f"Would CREATE new funds:    {stats['would_create']:,}")
        print(f"Would UPDATE existing:     {stats['would_update']:,}")
        print(f"Errors encountered:        {stats['errors']:,}")
        print(f"{'='*80}")

        # Show samples
        if stats['samples']:
            print(f"\n{'='*80}")
            print(f"SAMPLE FUNDS (First {len(stats['samples'])} funds)")
            print(f"{'='*80}")

            for i, sample in enumerate(stats['samples'], 1):
                action = sample['action']
                data = sample['data']

                print(f"\n--- Sample #{i} - Would {action} ---")
                print(f"  Fund ID:          {data['fund_id']}")
                print(f"  Name:             {data['name'][:70]}")
                print(f"  Company:          {data['company']}")
                print(f"  Classification:   {data['fund_classification']}")
                print(f"  Return Rate:      {data['return_rate']}%")
                print(f"  Monthly Yield:    {data['monthly_yield']}%")
                print(f"  YTD Yield:        {data['ytd_yield']}%")
                print(f"  Total Assets:     ₪{data['total_assets']} million")
                print(f"  Management Fee:   {data['management_fee']}%")
                print(f"  Inception Date:   {data['inception_date']}")
                print(f"  Report Period:    {data['report_period']}")
                print(f"  Specialization:   {data['specialization']}")

        print(f"\n{'='*80}")
        print("[INFO] DRY RUN COMPLETE - No database changes were made")
        print("{'='*80}")

    except Exception as e:
        print(f"\n[ERROR] Dry run failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
