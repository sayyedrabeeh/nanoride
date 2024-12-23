# Generated by Django 5.1.2 on 2024-11-02 10:54

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_alter_customuser_profile_image'),
        ('management', '0003_review'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('order_id', models.AutoField(primary_key=True, serialize=False)),
                ('tracking_number', models.CharField(editable=False, max_length=20, unique=True)),
                ('total_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('payment_type', models.CharField(choices=[('COD', 'Cash on Delivery'), ('RazorPay', 'Razor Pay'), ('Wallet', 'Wallet')], max_length=20)),
                ('payment_status', models.CharField(choices=[('Pending', 'Pending'), ('Success', 'Success'), ('Failure', 'Failure')], default='Pending', max_length=10)),
                ('estimated_delivery_date', models.DateField(blank=True, null=True)),
                ('coupon_code', models.CharField(blank=True, max_length=50, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('shipping_address', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentication.address')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('orderitem_id', models.AutoField(primary_key=True, serialize=False)),
                ('quantity', models.FloatField(default=0)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(choices=[('Order Pending', 'Order Pending'), ('Order Confirmed', 'Order Confirmed'), ('Shipped', 'Shipped'), ('Out For Delivery', 'Out For Delivery'), ('Delivered', 'Delivered'), ('Cancelled', 'Cancelled'), ('Requested Return', 'Requested Return'), ('Approve Returned', 'Approve Returned'), ('Reject Returned', 'Reject Returned')], default='Order Pending', max_length=20)),
                ('subtotal_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('return_reason', models.TextField(blank=True, null=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='authentication.order')),
                ('variants', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='management.variants')),
            ],
        ),
    ]
