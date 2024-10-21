# Generated by Django 5.1.2 on 2024-10-19 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0004_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('brand', models.CharField(max_length=100)),
                ('edition', models.CharField(max_length=100)),
                ('type1', models.CharField(max_length=100)),
                ('status', models.CharField(choices=[('listed', 'Listed'), ('delisted', 'Delisted')], default='listed', max_length=10)),
            ],
        ),
    ]