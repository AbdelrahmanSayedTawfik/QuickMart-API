from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0009_warehouse_city_warehousemovement_dest_after_and_more'),
        ('warehouses', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel(name='WarehouseMovement'),
                migrations.DeleteModel(name='WarehouseStock'),
                migrations.DeleteModel(name='Warehouse'),
            ],
            database_operations=[],
        ),
    ]