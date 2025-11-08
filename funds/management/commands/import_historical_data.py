"""
Management command to import historical fund data from data.gov.il API.
Downloads historical performance data and stores it in FundSnapshot model.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from funds.models import Fund, Company, FundSnapshot
from decimal import Decimal, InvalidOperation
from datetime import datetime
import requests


class Command(BaseCommand):
    help = 'Import historical fund data from data.gov.il Gemelnet API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit number of records to import (for testing)'
        )
        parser.add_argument(
            '--offset',
            type=int,
            default=0,
            help='Offset for pagination'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing snapshots before importing'
        )
        parser.add_argument(
            '--source',
            type=str,
            choices=['recent', 'historical', 'both'],
            default='both',
            help='Data source to import: recent (2016+), historical (1999+), or both'
        )

    def handle(self, *args, **options):
        limit = options['limit']
        offset = options['offset']
        clear = options['clear']
        source = options['source']

        if clear:
            self.stdout.write(self.style.WARNING('Clearing existing snapshots...'))
            FundSnapshot.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Cleared all snapshots'))

        # API endpoints
        RECENT_RESOURCE_ID = '2016d770-f094-4a2e-983e-797c26479720'  # Recent data (2016+)
        HISTORICAL_RESOURCE_ID = '91c849ed-ddc4-472b-bd09-0f5486cea35c'  # Historical data (1999+)
        base_url = 'https://data.gov.il/api/3/action/datastore_search'

        # Determine which sources to import
        sources_to_import = []
        if source in ['recent', 'both']:
            sources_to_import.append(('Recent (2016+)', RECENT_RESOURCE_ID))
        if source in ['historical', 'both']:
            sources_to_import.append(('Historical (1999+)', HISTORICAL_RESOURCE_ID))

        # Statistics
        stats = {
            'total_records': 0,
            'companies_created': 0,
            'companies_updated': 0,
            'funds_created': 0,
            'funds_updated': 0,
            'snapshots_created': 0,
            'snapshots_updated': 0,
            'errors': 0,
        }

        self.stdout.write(self.style.NOTICE(f'Starting data import from data.gov.il...'))
        self.stdout.write(f'Importing from {len(sources_to_import)} source(s)')

        # Process each source
        for source_name, resource_id in sources_to_import:
            self.stdout.write('\n' + '='*50)
            self.stdout.write(self.style.NOTICE(f'Importing from: {source_name}'))
            self.stdout.write(f'Resource ID: {resource_id}')
            self.stdout.write('='*50)

            # Fetch data with pagination
            has_more = True
            current_offset = offset
            batch_size = 1000 if not limit else min(limit, 1000)

            while has_more:
                params = {
                    'resource_id': resource_id,
                    'limit': batch_size,
                    'offset': current_offset
                }

                try:
                    self.stdout.write(f'\nFetching records {current_offset} to {current_offset + batch_size}...')
                    response = requests.get(base_url, params=params, timeout=30)
                    response.raise_for_status()
                    data = response.json()

                    if not data.get('success'):
                        self.stdout.write(self.style.ERROR(f'API returned error: {data}'))
                        break

                    records = data['result']['records']
                    total_available = data['result']['total']

                    if not records:
                        self.stdout.write('No more records to fetch')
                        break

                    self.stdout.write(f'Processing {len(records)} records...')

                    # Process each record
                    for record in records:
                        try:
                            self._process_record(record, stats)
                        except Exception as e:
                            stats['errors'] += 1
                            self.stdout.write(self.style.ERROR(f'Error processing record: {str(e)}'))
                            continue

                    stats['total_records'] += len(records)

                    # Update offset
                    current_offset += batch_size

                    # Check if we should continue
                    if limit and stats['total_records'] >= limit:
                        self.stdout.write(f'Reached limit of {limit} records')
                        has_more = False
                    elif current_offset >= total_available:
                        self.stdout.write(f'Fetched all {total_available} available records')
                        has_more = False

                    # Show progress
                    self.stdout.write(self.style.SUCCESS(
                        f'Progress: {current_offset}/{total_available} '
                        f'({(current_offset/total_available*100):.1f}%)'
                    ))

                except requests.exceptions.RequestException as e:
                    self.stdout.write(self.style.ERROR(f'Request failed: {str(e)}'))
                    break
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Unexpected error: {str(e)}'))
                    break

        # Print summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('Import completed!'))
        self.stdout.write(f'Total records processed: {stats["total_records"]}')
        self.stdout.write(f'Companies created: {stats["companies_created"]}')
        self.stdout.write(f'Companies updated: {stats["companies_updated"]}')
        self.stdout.write(f'Funds created: {stats["funds_created"]}')
        self.stdout.write(f'Funds updated: {stats["funds_updated"]}')
        self.stdout.write(f'Snapshots created: {stats["snapshots_created"]}')
        self.stdout.write(f'Snapshots updated: {stats["snapshots_updated"]}')
        if stats['errors'] > 0:
            self.stdout.write(self.style.WARNING(f'Errors encountered: {stats["errors"]}'))
        self.stdout.write('='*50)

    @transaction.atomic
    def _process_record(self, record, stats):
        """Process a single API record and create/update database objects."""

        # Extract company information
        company_legal_id = record.get('MANAGING_CORPORATION_LEGAL_ID')
        company_name = record.get('MANAGING_CORPORATION')

        if not company_legal_id or not company_name:
            return

        # Get or create company
        company, created = Company.objects.get_or_create(
            legal_id=company_legal_id,
            defaults={'name': company_name}
        )

        if created:
            stats['companies_created'] += 1
        elif company.name != company_name:
            company.name = company_name
            company.save()
            stats['companies_updated'] += 1

        # Extract fund information
        fund_id = record.get('FUND_ID')
        fund_name = record.get('FUND_NAME')

        if not fund_id or not fund_name:
            return

        # Parse inception date
        inception_date = None
        if record.get('INCEPTION_DATE'):
            try:
                inception_date = datetime.strptime(record['INCEPTION_DATE'], '%Y-%m-%dT%H:%M:%S').date()
            except (ValueError, TypeError):
                pass

        # Get or create fund
        fund, created = Fund.objects.get_or_create(
            fund_id=fund_id,
            defaults={
                'name': fund_name,
                'company': company,
                'category': record.get('FUND_CLASSIFICATION', ''),
                'fund_classification': record.get('FUND_CLASSIFICATION', ''),
                'specialization': record.get('SPECIALIZATION', ''),
                'sub_specialization': record.get('SUB_SPECIALIZATION', ''),
                'inception_date': inception_date,
            }
        )

        if created:
            stats['funds_created'] += 1
        else:
            # Update fund fields if they've changed
            updated = False
            if fund.name != fund_name:
                fund.name = fund_name
                updated = True
            if record.get('FUND_CLASSIFICATION') and fund.category != record['FUND_CLASSIFICATION']:
                fund.category = record['FUND_CLASSIFICATION']
                fund.fund_classification = record['FUND_CLASSIFICATION']
                updated = True
            if updated:
                fund.save()
                stats['funds_updated'] += 1

        # Extract snapshot data
        report_period = record.get('REPORT_PERIOD')
        if not report_period:
            return

        # Helper function to convert to Decimal
        def to_decimal(value, default=None):
            if value is None or value == '':
                return default
            try:
                return Decimal(str(value))
            except (InvalidOperation, ValueError):
                return default

        # Create or update snapshot
        snapshot, created = FundSnapshot.objects.update_or_create(
            fund=fund,
            report_period=report_period,
            defaults={
                'monthly_yield': to_decimal(record.get('MONTHLY_YIELD')),
                'ytd_yield': to_decimal(record.get('YEAR_TO_DATE_YIELD')),
                'return_3yr': to_decimal(record.get('YIELD_TRAILING_3_YRS')),
                'return_5yr': to_decimal(record.get('YIELD_TRAILING_5_YRS')),
                'avg_annual_return_3yr': to_decimal(record.get('AVG_ANNUAL_YIELD_TRAILING_3YRS')),
                'avg_annual_return_5yr': to_decimal(record.get('AVG_ANNUAL_YIELD_TRAILING_5YRS')),
                'total_assets': to_decimal(record.get('TOTAL_ASSETS')),
                'deposits': to_decimal(record.get('DEPOSITS')),
                'withdrawals': to_decimal(record.get('WITHDRAWLS')),  # Note: API has typo
                'net_deposits': to_decimal(record.get('NET_MONTHLY_DEPOSITS')),
                'internal_transfers': to_decimal(record.get('INTERNAL_TRANSFERS')),
                'net_monthly_deposits': to_decimal(record.get('NET_MONTHLY_DEPOSITS')),
                'standard_deviation': to_decimal(record.get('STANDARD_DEVIATION')),
                'alpha': to_decimal(record.get('ALPHA')),
                'sharpe_ratio': to_decimal(record.get('SHARPE_RATIO')),
                'liquid_assets_percent': to_decimal(record.get('LIQUID_ASSETS_PERCENT')),
                'stock_market_exposure': to_decimal(record.get('STOCK_MARKET_EXPOSURE')),
                'foreign_exposure': to_decimal(record.get('FOREIGN_EXPOSURE')),
                'foreign_currency_exposure': to_decimal(record.get('FOREIGN_CURRENCY_EXPOSURE')),
                'avg_annual_management_fee': to_decimal(record.get('AVG_ANNUAL_MANAGEMENT_FEE')),
                'avg_deposit_fee': to_decimal(record.get('AVG_DEPOSIT_FEE')),
            }
        )

        if created:
            stats['snapshots_created'] += 1
        else:
            stats['snapshots_updated'] += 1

        # Update fund's cached latest data if this is the most recent period
        if not fund.latest_report_period or report_period > fund.latest_report_period:
            fund.latest_report_period = report_period
            fund.return_rate = snapshot.avg_annual_return_5yr or snapshot.avg_annual_return_3yr
            fund.total_assets = snapshot.total_assets
            fund.management_fee = snapshot.avg_annual_management_fee
            fund.save(update_fields=['latest_report_period', 'return_rate', 'total_assets', 'management_fee'])
