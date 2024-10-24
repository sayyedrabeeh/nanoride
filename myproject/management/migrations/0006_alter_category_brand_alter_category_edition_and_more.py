# Generated by Django 5.1.2 on 2024-10-19 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0005_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='brand',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='category',
            name='edition',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='category',
            name='status',
            field=models.CharField(default='listed', max_length=10),
        ),
        migrations.AlterField(
            model_name='category',
            name='type1',
            field=models.CharField(max_length=255),
        ),
    ]
