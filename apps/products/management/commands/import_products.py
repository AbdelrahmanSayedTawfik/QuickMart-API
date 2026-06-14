import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from django.core.exceptions import ValidationError

from apps.accounts.models.user import CustomUser
from apps.products.models.category import Category
from apps.products.models.product import Product
from apps.products.validators.product import ProductValidator


class Command(BaseCommand):

    # Text shown when you run: python manage.py help import_products
    help = 'Import products from Excel file (.xlsx or .csv)'
    
    def add_arguments(self, parser):


        parser.add_argument(
            'file_path',                          
            type=str,                             
            help='Path to Excel file (.xlsx)'     
        )

        parser.add_argument(
            '--skip-invalid',
            action='store_true',                 
            help='Skip invalid rows instead of stopping on first error'
        )
        

        parser.add_argument(
            '--update-existing',
            action='store_true',
            help='Update existing products instead of skipping them'
        )
    
    def handle(self, *args, **options):
 
        # Get arguments from options dict
        file_path = options['file_path']
        skip_invalid = options['skip_invalid']
        update_existing = options['update_existing']
        
        
        self.stdout.write(self.style.NOTICE(f'📖 Reading {file_path}...'))
        
        # ── STEP 1: READ EXCEL FILE ──
        try:
            
            df = pd.read_excel(file_path)
        except Exception as e:
            
            self.stdout.write(self.style.ERROR(f'❌ Failed to read file: {e}'))
            return  
        
        # Show how many rows we found
        self.stdout.write(f'📊 Found {len(df)} rows to process')
        
        # ── STEP 2: TRACK RESULTS ──
        created_count = 0      
        updated_count = 0      
        skipped_count = 0      
        error_count = 0        
        errors = []            
        
        # ── STEP 3: PROCESS EACH ROW ──

        for index, row in df.iterrows():
            # Excel row number = index + 2 (row 1 is header, DataFrame is 0-indexed)
            row_num = index + 2
            
            try:

                with transaction.atomic():
                    result = self._process_row(row, row_num, update_existing)
                
                # Count results
                if result == 'created':
                    created_count += 1
                elif result == 'updated':
                    updated_count += 1
                elif result == 'skipped':
                    skipped_count += 1
                    
            except Exception as e:
                # Something went wrong with this row
                error_count += 1
                errors.append(f'Row {row_num}: {str(e)}')
                
                # Print error immediately so admin sees progress
                self.stdout.write(self.style.ERROR(f'  ❌ Row {row_num}: {e}'))
                
                # If --skip-invalid is NOT set, STOP everything
                if not skip_invalid:
                    self.stdout.write(self.style.ERROR(
                        f'\n🛑 Stopping due to error at row {row_num}. '
                        f'Use --skip-invalid to skip bad rows.'
                    ))
                    break  # Exit the loop
        
        # ── STEP 4: PRINT SUMMARY ──
        self.stdout.write(self.style.SUCCESS(
            f'\n{"="*50}\n'
            f'📦 IMPORT SUMMARY\n'
            f'{"="*50}\n'
            f'✅ Created:  {created_count}\n'
            f'🔄 Updated:  {updated_count}\n'
            f'⏭️  Skipped: {skipped_count}\n'
            f'❌ Errors:   {error_count}\n'
            f'📋 Total:    {created_count + updated_count + skipped_count + error_count}/{len(df)}\n'
            f'{"="*50}'
        ))
        
        # Print all errors at the end for review
        if errors:
            self.stdout.write(self.style.WARNING('\n⚠️  Error Details:'))
            for error in errors:
                self.stdout.write(self.style.WARNING(f'  • {error}'))
    
    def _process_row(self, row, row_num, update_existing):

        # ── EXTRACT DATA FROM EXCEL ROW ──
        # .get() with default value prevents crashes if column is missing
        # str() converts everything to string, then .strip() removes spaces
        
        name = str(row.get('name', '')).strip()
        description = str(row.get('description', '')).strip() or None  # Empty → None
        sku = str(row.get('sku', '')).strip()
        original_price = self._parse_decimal(row.get('original_price', 0))
        price = self._parse_decimal(row.get('price', 0))
        stock_quantity = int(row.get('stock_quantity', 0))
        category_name = str(row.get('category_name', '')).strip()
        seller_email = str(row.get('seller_email', '')).strip()
        status = str(row.get('status', 'draft')).strip().lower()
        is_active = self._parse_bool(row.get('is_active', True))
        
        # ── VALIDATE REQUIRED FIELDS ──
        if not name:
            raise ValidationError('Name is required')
        if not sku:
            raise ValidationError('SKU is required')
        
        # ── VALIDATE BUSINESS RULES (using our validator!) ──
        ProductValidator.validate_price(price)
        if original_price > 0:
            ProductValidator.validate_price(original_price)
        
        # ── GET OR CREATE CATEGORY ──
        category = None
        if category_name:

            category, _ = Category.objects.get_or_create(
                name=category_name,
                defaults={
                    'slug': category_name.lower().replace(' ', '-'),
                    'is_active': True
                }
            )
        
        # ── GET SELLER ──
        seller = None
        if seller_email:
            try:
                # Must be a seller or admin
                seller = CustomUser.objects.get(
                    email=seller_email,
                    role__in=['seller', 'admin']
                )
            except CustomUser.DoesNotExist:
                raise ValidationError(
                    f'Seller with email "{seller_email}" not found '
                    f'(must have role=seller or admin)'
                )
        else:
            # No seller specified — use first admin as default
            seller = CustomUser.objects.filter(role='admin').first()
            if not seller:
                raise ValidationError('No seller or admin found in database')
        
        # ── CHECK IF PRODUCT EXISTS (by SKU) ──
        try:
            product = Product.objects.get(sku=sku)
            
            # Product exists — update or skip?
            if update_existing:
                # UPDATE EXISTING PRODUCT
                product.name = name
                product.description = description
                product.original_price = original_price
                product.price = price
                product.stock_quantity = stock_quantity
                product.category = category
                product.status = status
                product.is_active = is_active
                product.seller = seller  # Can transfer ownership
                
                # Save triggers auto-slug and stock_status update
                product.save()
                
                self.stdout.write(f'  🔄 Row {row_num}: Updated "{name}" (SKU: {sku})')
                return 'updated'
            else:
                # Skip — don't update existing
                self.stdout.write(f'  ⏭️  Row {row_num}: Skipped "{name}" (SKU exists)')
                return 'skipped'
                
        except Product.DoesNotExist:
            # CREATE NEW PRODUCT
            product = Product.objects.create(
                name=name,
                description=description,
                sku=sku,
                original_price=original_price,
                price=price,
                stock_quantity=stock_quantity,
                category=category,
                status=status,
                is_active=is_active,
                seller=seller
                # slug auto-generated by model's save() method
            )
            
            self.stdout.write(f'  ✅ Row {row_num}: Created "{name}" (SKU: {sku})')
            return 'created'
    
    def _parse_decimal(self, value):

        if value is None or value == '':
            return 0
        try:
            from decimal import Decimal
            return Decimal(str(value))
        except:
            return 0
    
    def _parse_bool(self, value):

        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', 'yes', '1', 't', 'y')
        return bool(value)