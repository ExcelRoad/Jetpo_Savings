"""
Gemelnet Data Sync Utility V2 - WITH HISTORICAL DATA

This version saves ALL periods for trend analysis, not just the latest.
"""
import requests
from datetime import datetime
from decimal import Decimal
from django.db import transaction
from .models import Company, Fund, FundSnapshot

# Gemelnet API Configuration
GEMELNET_API_URL = "https://data.gov.il/api/3/action/datastore_search"
GEMELNET_RESOURCE_ID = "a30dcbea-a1d2-482c-ae29-8f781f5025fb"


def fetch_gemelnet_data(limit=None):
    """Fetch fund data from the Gemelnet API."""
    all_records = []
    offset = 0
    batch_size = 1000

    print(f"Fetching data from Gemelnet API...")

    while True:
        params = {
            'resource_id': GEMELNET_RESOURCE_ID,
            'limit': limit if limit else batch_size,
            'offset': offset
        }

        try:
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
            print(f"  Fetched {len(all_records):,} / {total:,} records...")

            if limit or len(all_records) >= total:
                break

            offset += batch_size

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch data from Gemelnet API: {e}")

    print(f"Successfully fetched {len(all_records):,} total records")
    return all_records


def organize_by_fund(records):
    """Organize ALL records by fund_id for historical tracking."""
    print("Organizing records by fund (keeping ALL periods)...")

    fund_records = {}

    for record in records:
        fund_id = str(record.get('FUND_ID'))
        if not fund_id:
            continue

        if fund_id not in fund_records:
            fund_records[fund_id] = []
        fund_records[fund_id].append(record)

    print(f"Found {len(fund_records):,} unique funds")
    print(f"Total records to process: {len(records):,}")

    return fund_records


def safe_decimal(value, default=None):
    """Safely convert a value to Decimal."""
    if value is None or value == '':
        return default
    try:
        return Decimal(str(value))
    except (ValueError, TypeError):
        return default


def parse_date(date_string):
    """Parse date string from API format."""
    if not date_string:
        return None
    try:
        dt = datetime.strptime(date_string.split()[0], "%Y-%m-%d")
        return dt.date()
    except (ValueError, IndexError):
        return None


@transaction.atomic
def sync_gemelnet_data_with_history(limit=None):
    """
    Sync ALL historical data from Gemelnet API.

    This creates:
    - Company records (one per company)
    - Fund records (one per fund with static data)
    - FundSnapshot records (one per fund per period for trends)

    Optimization: Pre-checks existing snapshots to skip already-synced periods.
    """
    print("=" * 80)
    print("Starting Gemelnet FULL HISTORICAL Sync")
    print("=" * 80)

    stats = {
        'total_fetched': 0,
        'unique_funds': 0,
        'companies_created': 0,
        'funds_created': 0,
        'snapshots_created': 0,
        'snapshots_skipped': 0,
        'errors': 0
    }

    try:
        # Step 1: Fetch ALL records
        all_records = fetch_gemelnet_data(limit=limit)
        stats['total_fetched'] = len(all_records)

        if not all_records:
            print("No records fetched")
            return stats

        # Step 2: Organize by fund
        fund_records_map = organize_by_fund(all_records)
        stats['unique_funds'] = len(fund_records_map)

        # Step 3: Pre-load existing snapshots for optimization
        print("\nPre-loading existing snapshots for optimization...")
        existing_snapshots = set(
            FundSnapshot.objects.values_list('fund__fund_id', 'report_period')
        )
        print(f"Found {len(existing_snapshots):,} existing snapshots in database")

        # Step 4: Process each fund and ALL its periods
        print(f"\nProcessing {len(fund_records_map):,} funds with historical data...")

        for fund_id, fund_periods in fund_records_map.items():
            try:
                # Get the latest record for company/fund info
                latest_record = max(fund_periods, key=lambda x: x.get('REPORT_PERIOD', 0))

                # Step 3a: Create/update Company
                company_legal_id = str(latest_record.get('MANAGING_CORPORATION_LEGAL_ID', ''))
                company_name = latest_record.get('MANAGING_CORPORATION', '')

                if not company_legal_id or not company_name:
                    stats['errors'] += 1
                    continue

                company, company_created = Company.objects.get_or_create(
                    legal_id=company_legal_id,
                    defaults={'name': company_name}
                )

                if company_created:
                    stats['companies_created'] += 1

                # Step 3b: Create/update Fund (with static data from latest record)
                fund_classification = latest_record.get('FUND_CLASSIFICATION', '')
                fund_data = {
                    'name': latest_record.get('FUND_NAME', ''),
                    'company': company,
                    'category': fund_classification,  # Use FUND_CLASSIFICATION directly
                    'fund_classification': fund_classification,
                    'specialization': latest_record.get('SPECIALIZATION', ''),
                    'sub_specialization': latest_record.get('SUB_SPECIALIZATION', ''),
                    'inception_date': parse_date(latest_record.get('INCEPTION_DATE')),
                    'management_fee': safe_decimal(latest_record.get('AVG_ANNUAL_MANAGEMENT_FEE')),
                    # Cached latest values
                    'return_rate': safe_decimal(latest_record.get('AVG_ANNUAL_YIELD_TRAILING_5YRS')),
                    'total_assets': safe_decimal(latest_record.get('TOTAL_ASSETS')),
                    'latest_report_period': latest_record.get('REPORT_PERIOD'),
                }

                fund, fund_created = Fund.objects.update_or_create(
                    fund_id=fund_id,
                    defaults=fund_data
                )

                if fund_created:
                    stats['funds_created'] += 1

                # Step 3c: Create snapshots ONLY for periods we don't have yet
                for period_record in fund_periods:
                    report_period = period_record.get('REPORT_PERIOD')
                    if not report_period:
                        continue

                    # OPTIMIZATION: Skip if we already have this snapshot
                    if (fund_id, report_period) in existing_snapshots:
                        stats['snapshots_skipped'] += 1
                        continue

                    # Only create/update if we don't have it
                    snapshot_data = {
                        'monthly_yield': safe_decimal(period_record.get('MONTHLY_YIELD')),
                        'ytd_yield': safe_decimal(period_record.get('YEAR_TO_DATE_YIELD')),
                        'return_3yr': safe_decimal(period_record.get('YIELD_TRAILING_3_YRS')),
                        'return_5yr': safe_decimal(period_record.get('YIELD_TRAILING_5_YRS')),
                        'avg_annual_return_3yr': safe_decimal(period_record.get('AVG_ANNUAL_YIELD_TRAILING_3YRS')),
                        'avg_annual_return_5yr': safe_decimal(period_record.get('AVG_ANNUAL_YIELD_TRAILING_5YRS')),
                        'total_assets': safe_decimal(period_record.get('TOTAL_ASSETS')),
                        'deposits': safe_decimal(period_record.get('DEPOSITS')),
                        'withdrawals': safe_decimal(period_record.get('WITHDRAWLS')),  # Note: API has typo
                        'net_deposits': safe_decimal(period_record.get('NET_MONTHLY_DEPOSITS')),
                        'standard_deviation': safe_decimal(period_record.get('STANDARD_DEVIATION')),
                        'alpha': safe_decimal(period_record.get('ALPHA')),
                        'sharpe_ratio': safe_decimal(period_record.get('SHARPE_RATIO')),
                    }

                    FundSnapshot.objects.create(
                        fund=fund,
                        report_period=report_period,
                        **snapshot_data
                    )
                    stats['snapshots_created'] += 1

                    # Add to existing set to avoid duplicates in this run
                    existing_snapshots.add((fund_id, report_period))

                # Progress
                if stats['funds_created'] % 50 == 0:
                    print(f"  Processed {stats['funds_created']} funds, {stats['snapshots_created']:,} snapshots...")

            except Exception as e:
                stats['errors'] += 1
                print(f"  Error processing fund {fund_id}: {e}")
                continue

        print(f"\nSync completed!")

    except Exception as e:
        print(f"\n[ERROR] Sync failed: {e}")
        raise

    # Summary
    print("\n" + "=" * 80)
    print("FULL HISTORICAL Sync Summary")
    print("=" * 80)
    print(f"Total records fetched:        {stats['total_fetched']:,}")
    print(f"Unique funds:                 {stats['unique_funds']:,}")
    print(f"")
    print(f"Companies created:            {stats['companies_created']:,}")
    print(f"Funds created:                {stats['funds_created']:,}")
    print(f"")
    print(f"Snapshots created:            {stats['snapshots_created']:,}")
    print(f"Snapshots skipped:            {stats['snapshots_skipped']:,} (already exist)")
    print(f"")
    print(f"Errors:                       {stats['errors']:,}")
    print("=" * 80)

    return stats
