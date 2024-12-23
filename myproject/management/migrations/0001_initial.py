# Generated by Django 5.1 on 2024-10-27 09:25

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('brand_name', models.CharField(max_length=100)),
                ('active', models.BooleanField(default=True)),
                ('status', models.CharField(default='listed', max_length=10)),
                ('country', models.CharField(max_length=100)),
                ('image', models.ImageField(default='images/default.jpg', upload_to='images/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Edition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('edition_name', models.CharField(max_length=100)),
                ('active', models.BooleanField(default=True)),
                ('status', models.CharField(default='listed', max_length=10)),
                ('image', models.ImageField(default='images/default.jpg', upload_to='images/')),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='SportsCar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('brand', models.CharField(max_length=100)),
                ('year', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('profile_image', models.ImageField(default='images/profile.jpeg', upload_to='profile_images/')),
                ('phone', models.CharField(blank=True, max_length=15, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('wallet', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('groups', models.ManyToManyField(blank=True, related_name='customuser_auth_set', to='auth.group')),
                ('user_permissions', models.ManyToManyField(blank=True, related_name='customuser_auth_set', to='auth.permission')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Categories',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('status', models.CharField(default='listed', max_length=10)),
                ('brand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categories', to='management.brand')),
                ('edition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categories', to='management.edition')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('ratings', models.FloatField(default=0.0)),
                ('comments', models.TextField(blank=True)),
                ('status', models.CharField(default='listed', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('image', models.ImageField(default='products/p.png', upload_to='products/')),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('stock', models.PositiveIntegerField(default=0)),
                ('main_image', models.ImageField(blank=True, null=True, upload_to='product_images/main/')),
                ('brand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='management.brand')),
                ('category', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='management.categories')),
            ],
        ),
        migrations.AddField(
            model_name='edition',
            name='products',
            field=models.ManyToManyField(related_name='editions', to='management.product'),
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='product_images/extra/')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='additional_images', to='management.product')),
            ],
        ),
        migrations.CreateModel(
            name='Type1',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('Quantity', models.IntegerField()),
                ('status', models.CharField(default='listed', max_length=10)),
                ('image', models.ImageField(default='images/default.jpg', upload_to='images/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('products', models.ManyToManyField(related_name='types', to='management.product')),
            ],
        ),
        migrations.AddField(
            model_name='categories',
            name='type1',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categories', to='management.type1'),
        ),
        migrations.CreateModel(
            name='Variants',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('colour', models.CharField(max_length=50)),
                ('type1', models.CharField(max_length=50)),
                ('size', models.CharField(max_length=20)),
                ('stock', models.PositiveIntegerField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(default=24, on_delete=django.db.models.deletion.CASCADE, related_name='variants', to='management.product')),
            ],
        ),
        migrations.CreateModel(
            name='VariantImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='variant_images/')),
                ('variant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='management.variants')),
            ],
        ),
    ]
