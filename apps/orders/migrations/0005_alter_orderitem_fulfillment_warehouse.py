import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_move_cart_models_state_only'),
        ('warehouses', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='fulfillment_warehouse',
            field=models.ForeignKey(blank=True, help_text='Warehouse that stock was deducted from for this item', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='fulfilled_order_items', to='warehouses.warehouse'),
        ),
    ]