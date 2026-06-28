from django.core.management.base import BaseCommand
from apps.products.management.commands.importers.category import CategoryImporter
from apps.products.management.commands.importers.product import ProductImporter


class Command(BaseCommand):


    help = 'Import data from CSV files'

    def add_arguments(self, parser):
        """Define command line arguments."""
        parser.add_argument(
            '--file',
            type=str,
            required=True,
            help='Path to CSV file'
        )
        parser.add_argument(
            '--model',
            type=str,
            required=True,
            choices=['categories', 'products'],
            help='Type of data to import'
        )

        parser.add_argument(
            '--user',
            type=str,
            required=False,
            help='Email of the user performing the import (for permission checks)'
        )
        parser.add_argument(
            '--skip-invalid',
            action='store_true',
            help='Skip invalid rows and continue importing'
        )
        parser.add_argument(
            '--update-existing',
            action='store_true',
            help='Update existing records instead of skipping'
        )

    def handle(self, *args, **options):
        """Execute the command."""

        file_path = options['file']
        model_name = options['model']
        user_email = options['user']           # ← NEW: Get user from --user flag
        skip_invalid = options['skip_invalid']
        update_existing = options['update_existing']

        # Map model names to importer classes
        importers = {
            'categories': CategoryImporter,
            'products': ProductImporter,
        }

        if model_name not in importers:
            self.stdout.write(self.style.ERROR(f'Unknown model: {model_name}'))
            return

        importer_class = importers[model_name]

        importer = importer_class(
            stdout=self.stdout,
            style=self.style,
            user=user_email  # ← Pass email string (importer will look it up)
        )

        # Run the import (reads file from disk)
        importer.run(file_path, skip_invalid, update_existing)