from django.db import migrations, models
import json

def convert_price_to_json(apps, schema_editor):
    Variants = apps.get_model('management', 'Variants')
    for variant in Variants.objects.all():
        variant.price = json.dumps([float(variant.price)])  # Store it as a list in JSON
        variant.save()

def convert_stock_to_json(apps, schema_editor):
    Variants = apps.get_model('management', 'Variants')
    for variant in Variants.objects.all():
        variant.stock = json.dumps([int(variant.stock)])  # Store it as a list in JSON
        variant.save()

class Migration(migrations.Migration):

    dependencies = [
        ('management', '0031_merge_20241024_1253'),
    ]

    operations = [
        # Add temporary fields
        migrations.AddField(
            model_name='variants',
            name='price_temp',
            field=models.JSONField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='variants',
            name='stock_temp',
            field=models.JSONField(null=True, blank=True),
        ),
        # Convert existing data to JSON
        migrations.RunPython(convert_price_to_json),
        migrations.RunPython(convert_stock_to_json),
        # Remove old fields
        migrations.RemoveField(
            model_name='variants',
            name='price',
        ),
        migrations.RemoveField(
            model_name='variants',
            name='stock',
        ),
        # Rename temporary fields to original names
        migrations.RenameField(
            model_name='variants',
            old_name='price_temp',
            new_name='price',
        ),
        migrations.RenameField(
            model_name='variants',
            old_name='stock_temp',
            new_name='stock',
        ),
        # Now add the new image fields and remove the old image field
        migrations.RemoveField(
            model_name='variants',
            name='image',
        ),
        migrations.AddField(
            model_name='variants',
            name='image1',
            field=models.ImageField(blank=True, null=True, upload_to='variant_images/'),
        ),
        migrations.AddField(
            model_name='variants',
            name='image2',
            field=models.ImageField(blank=True, null=True, upload_to='variant_images/'),
        ),
        migrations.AddField(
            model_name='variants',
            name='image3',
            field=models.ImageField(blank=True, null=True, upload_to='variant_images/'),
        ),
        migrations.AddField(
            model_name='variants',
            name='image4',
            field=models.ImageField(blank=True, null=True, upload_to='variant_images/'),
        ),
    ]
