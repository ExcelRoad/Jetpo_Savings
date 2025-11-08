"""
Django management command to sync Gemelnet fund data.

Usage:
    python manage.py sync_gemelnet              # Sync all historical data (default)
    python manage.py sync_gemelnet --limit 100  # Limit API records for testing
"""
from django.core.management.base import BaseCommand
from funds.gemelnet_sync_v2 import sync_gemelnet_data_with_history


class Command(BaseCommand):
    help = 'Sync fund data from Gemelnet API (includes all historical data)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit number of records to fetch from API (for testing)'
        )

    def handle(self, *args, **options):
        limit = options.get('limit')

        if limit:
            self.stdout.write(
                self.style.WARNING(f'Syncing with limit of {limit} records (testing mode)...')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Syncing ALL historical data (this may take several minutes)...')
            )

        result = sync_gemelnet_data_with_history(limit=limit)

        # Display results
        self.stdout.write(self.style.SUCCESS('\n' + '='*80))
        self.stdout.write(self.style.SUCCESS('Sync completed successfully!'))
        self.stdout.write(self.style.SUCCESS('='*80))
