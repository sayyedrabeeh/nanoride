# Generated by Django 5.1.2 on 2024-11-01 11:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='profile_image',
            field=models.ImageField(default='images/profile.png', upload_to='profile_images/'),
        ),
    ]
