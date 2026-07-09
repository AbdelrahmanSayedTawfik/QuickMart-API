import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('products', '0009_warehouse_city_warehousemovement_dest_after_and_more'),
        ('accounts', '0009_remove_customuser_managed_warehouses_and_more'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='Warehouse',
                    fields=[
                        ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('name', models.CharField(help_text='Name of the warehouse', max_length=100, unique=True)),
                        ('code', models.CharField(help_text='Unique code for the warehouse', max_length=10, unique=True)),
                        ('address', models.TextField(help_text='Address of the warehouse')),
                        ('city', models.CharField(blank=True, help_text='City this warehouse serves for shipping', max_length=100, null=True)),
                        ('is_active', models.BooleanField(default=True, help_text='Indicates whether the warehouse is active or not')),
                        ('is_default', models.BooleanField(default=False, help_text=' Default Warehouse for new stock and orders ')),
                        ('manager_name', models.CharField(blank=True, help_text='Person responsible for this warehouse', max_length=50)),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('updated_at', models.DateTimeField(auto_now=True)),
                    ],
                    options={
                        'verbose_name': 'Warehouse',
                        'verbose_name_plural': 'Warehouses',
                        'db_table': 'products_warehouse',
                        'ordering': ['name'],
                    },
                ),
                migrations.CreateModel(
                    name='WarehouseStock',
                    fields=[
                        ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('quantity', models.PositiveIntegerField(default=0, help_text='Quantity of the product in the warehouse', validators=[django.core.validators.MinValueValidator(0)])),
                        ('low_stock_threshold', models.PositiveIntegerField(default=5, help_text='Threshold for low stock alert', validators=[django.core.validators.MinValueValidator(0)])),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('updated_at', models.DateTimeField(auto_now=True)),
                        ('Warehouse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='warehouse_stocks', to='warehouses.warehouse')),
                        ('Product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='warehouse_stocks', to='products.product')),
                    ],
                    options={
                        'verbose_name': 'Warehouse Stock',
                        'verbose_name_plural': 'Warehouse Stocks',
                        'db_table': 'products_warehousestock',
                        'ordering': ['Warehouse', 'Product'],
                        'unique_together': {('Warehouse', 'Product')},
                        'indexes': [
                                    models.Index(fields=['Warehouse', 'quantity'], name='products_wa_Warehou_0ab9bc_idx'),
                                    models.Index(fields=['Warehouse', 'Product'], name='products_wa_Warehou_37ceb6_idx'),
                                ],
                    },
                ),
                migrations.CreateModel(
                    name='WarehouseMovement',
                    fields=[
                        ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('movement_type', models.CharField(choices=[('in', 'Stock In'), ('out', 'Stock Out'), ('transfer_in', 'Transfer In'), ('transfer_out', 'Transfer Out'), ('adjustment', 'Adjustment')], help_text='Why did this movement happen', max_length=20)),
                        ('quantity', models.PositiveIntegerField(help_text='How many units moved')),
                        ('source_stock_before', models.PositiveIntegerField(blank=True, help_text='Stock at source warehouse BEFORE this movement', null=True)),
                        ('destination_stock_before', models.PositiveIntegerField(blank=True, help_text='Stock at destination warehouse BEFORE this movement', null=True)),
                        ('source_after', models.PositiveIntegerField(blank=True, help_text='Source warehouse stock AFTER this move', null=True)),
                        ('dest_after', models.PositiveIntegerField(blank=True, help_text='Destination warehouse stock AFTER this move', null=True)),
                        ('reference_id', models.CharField(blank=True, help_text='Order number, transfer ID, or adjustment reference', max_length=100)),
                        ('notes', models.TextField(blank=True, help_text='Human-readable reason')),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('source_warehouse', models.ForeignKey(blank=True, help_text='Warehouse stock LEFT from. NULL for supplier.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='outgoing_movements', to='warehouses.warehouse')),
                        ('destination_warehouse', models.ForeignKey(blank=True, help_text='Warehouse stock ARRIVED at. NULL for customer.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='incoming_movements', to='warehouses.warehouse')),
                        ('product', models.ForeignKey(blank=True, help_text='Which product moved', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='warehouse_movements', to='products.product')),
                        ('created_by', models.ForeignKey(blank=True, help_text='User who initiated this movement', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='warehouse_movements', to='accounts.customuser')),
                    ],
                    options={
                        'verbose_name': 'Warehouse Movement',
                        'verbose_name_plural': 'Warehouse Movements',
                        'db_table': 'products_warehousemovement',
                        'ordering': ['-created_at'],
                        'indexes': [
                                    models.Index(fields=['product', '-created_at'], name='products_wa_product_9f6c45_idx'),
                                    models.Index(fields=['source_warehouse', '-created_at'], name='products_wa_source__ab1412_idx'),
                                    models.Index(fields=['destination_warehouse', '-created_at'], name='products_wa_destina_261040_idx'),
                                    models.Index(fields=['movement_type', '-created_at'], name='products_wa_movemen_9fe1f3_idx'),
                                ],
                    },
                ),
            ],
            database_operations=[],
        ),
    ]