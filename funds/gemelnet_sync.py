"""
Gemelnet Data Sync Utility

This module handles fetching and syncing fund data from the Gemelnet API.
The API provides monthly historical reports for Israeli pension/provident funds.

Usage:
    from funds.gemelnet_sync import sync_gemelnet_data
    result = sync_gemelnet_data()
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
    """
    Fetch fund data from the Gemelnet API.

    Args:
        limit (int, optional): Maximum number of records to fetch.
                              If None, fetches all records using pagination.

    Returns:
        list: List of fund records from the API

    Raises:
        requests.exceptions.RequestException: If API request fails
    """
    all_records = []
    offset = 0
    batch_size = 1000  # Fetch 1000 records at a time

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

            # If we have a limit or we've fetched all records, stop
            if limit or len(all_records) >= total:
                break

            offset += batch_size

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch data from Gemelnet API: {e}")

    print(f"Successfully fetched {len(all_records):,} total records")
    return all_records


def organize_records_by_fund(records):
    """
    Organize all records by fund_id, keeping ALL periods for trend analysis.

    The API returns multiple records per fund (one for each month).
    We want ALL periods to show historical trends.

    Args:
        records (list): All records from the API

    Returns:
        dict: Dictionary mapping fund_id to list of all its records
    """
    print("Organizing records by fund (keeping all periods for trends)...")

    fund_records = {}
    period_stats = {}

    for record in records:
        fund_id = str(record.get('FUND_ID'))
        report_period = record.get('REPORT_PERIOD')

        if not fund_id or not report_period:
            continue

        # Track periods
        if report_period not in period_stats:
            period_stats[report_period] = 0
        period_stats[period_stats] += 1

        # Group by fund
        if fund_id not in fund_records:
            fund_records[fund_id] = []
        fund_records[fund_id].append(record)

    print(f"Found {len(fund_records):,} unique funds")
    print(f"Total periods in dataset: {len(period_stats)}")

    return fund_records


def parse_date(date_string):
    """
    Parse date string from API format to Python date.

    Args:
        date_string (str): Date in format "YYYY-MM-DD HH:MM:SS"

    Returns:
        date: Parsed date object or None if parsing fails
    """
    if not date_string:
        return None

    try:
        # Format: "2016-11-28 00:00:00"
        dt = datetime.strptime(date_string.split()[0], "%Y-%m-%d")
        return dt.date()
    except (ValueError, IndexError):
        return None


def safe_decimal(value, default=None):
    """
    Safely convert a value to Decimal, handling None and invalid values.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        Decimal: Converted value or default
    """
    if value is None or value == '':
        return default

    try:
        return Decimal(str(value))
    except (ValueError, TypeError):
        return default


def map_category(fund_classification, specialization):
    """
    Map Gemelnet classification to our simplified category system.

    Args:
        fund_classification (str): Official fund classification
        specialization (str): Fund specialization

    Returns:
        str: Mapped category from Fund.Category choices
    """
    # Convert to lowercase for easier matching
    classification = (fund_classification or '').lower()
    spec = (specialization or '').lower()

    # Map based on keywords (you can expand this mapping)
    if 'מניות' in classification or 'מניות' in spec:
        return Fund.Category.STOCKS
    elif 'אג"ח' in classification or 'אג"ח' in spec or 'אגח' in classification:
        return Fund.Category.BONDS
    elif 'מעורב' in classification or 'מעורב' in spec:
        return Fund.Category.MIXED
    elif 'שוק כסף' in classification or 'כסף' in spec:
        return Fund.Category.MONEY_MARKET
    elif 'חו"ל' in classification or 'חול' in classification:
        return Fund.Category.FOREIGN
    elif 'מדד' in classification or 'מדד' in spec:
        return Fund.Category.INDEX
    elif 'נדל"ן' in classification or 'נדלן' in classification:
        return Fund.Category.REAL_ESTATE

    # Default to mixed if we can't determine
    return ''


@transaction.atomic
def sync_gemelnet_data(limit=None):
    """
    Main function to sync Gemelnet data to the database.

    This function:
    1. Fetches all data from the Gemelnet API
    2. Filters to get the latest period for each fund
    3. Creates or updates Company records in the database
    4. Creates or updates Fund records linked to their companies

    Args:
        limit (int, optional): Limit the number of API records to fetch (for testing)

    Returns:
        dict: Summary of the sync operation with keys:
            - total_fetched: Number of records fetched from API
            - unique_funds: Number of unique funds found
            - companies_created: Number of new companies created
            - companies_updated: Number of existing companies updated
            - funds_created: Number of new funds created
            - funds_updated: Number of existing funds updated
            - errors: Number of records that failed to process
    """
    print("=" * 80)
    print("Starting Gemelnet Data Sync")
    print("=" * 80)

    stats = {
        'total_fetched': 0,
        'unique_funds': 0,
        'companies_created': 0,
        'companies_updated': 0,
        'funds_created': 0,
        'funds_updated': 0,
        'errors': 0
    }

    try:
        # Step 1: Fetch data from API
        records = fetch_gemelnet_data(limit=limit)
        stats['total_fetched'] = len(records)

        if not records:
            print("No records fetched from API")
            return stats

        # Step 2: Get latest period data for each fund
        latest_records = get_latest_period_data(records)
        stats['unique_funds'] = len(latest_records)

        # Step 3: Create or update funds in database
        print(f"\nSyncing {len(latest_records):,} funds to database...")

        for fund_id, record in latest_records.items():
            try:
                # Step 3a: Get or create company first
                company_legal_id = str(record.get('MANAGING_CORPORATION_LEGAL_ID', ''))
                company_name = record.get('MANAGING_CORPORATION', '')

                if not company_legal_id or not company_name:
                    stats['errors'] += 1
                    print(f"  Error: Fund {fund_id} missing company data")
                    continue

                # Create or update company
                company, company_created = Company.objects.update_or_create(
                    legal_id=company_legal_id,
                    defaults={'name': company_name}
                )

                if company_created:
                    stats['companies_created'] += 1
                else:
                    stats['companies_updated'] += 1

                # Step 3b: Extract fund data
                fund_data = {
                    'fund_id': fund_id,
                    'name': record.get('FUND_NAME', ''),
                    'company': company,  # Use the company object instead of string
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

                # Map category
                fund_data['category'] = map_category(
                    fund_data['fund_classification'],
                    fund_data['specialization']
                )

                # Step 3c: Create or update fund
                fund, fund_created = Fund.objects.update_or_create(
                    fund_id=fund_id,
                    defaults=fund_data
                )

                if fund_created:
                    stats['funds_created'] += 1
                else:
                    stats['funds_updated'] += 1

                # Progress indicator
                total_processed = stats['funds_created'] + stats['funds_updated']
                if total_processed % 100 == 0:
                    print(f"  Processed {total_processed:,} funds...")

            except Exception as e:
                stats['errors'] += 1
                print(f"  Error processing fund {fund_id}: {e}")
                continue

        print(f"\nSync completed successfully!")

    except Exception as e:
        print(f"\n[ERROR] Sync failed: {e}")
        raise

    # Print summary
    print("\n" + "=" * 80)
    print("Sync Summary")
    print("=" * 80)
    print(f"Total records fetched:   {stats['total_fetched']:,}")
    print(f"Unique funds found:      {stats['unique_funds']:,}")
    print(f"")
    print(f"Companies created:       {stats['companies_created']:,}")
    print(f"Companies updated:       {stats['companies_updated']:,}")
    print(f"")
    print(f"Funds created:           {stats['funds_created']:,}")
    print(f"Funds updated:           {stats['funds_updated']:,}")
    print(f"")
    print(f"Errors:                  {stats['errors']:,}")
    print("=" * 80)

    return stats
