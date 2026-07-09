from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_orderitem_fulfillment_warehouse'),
        ('carts', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel(name='CartItem'),
                migrations.DeleteModel(name='Cart'),
            ],
            database_operations=[],
        ),
    ]