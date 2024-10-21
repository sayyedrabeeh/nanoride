from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class CustomUser(AbstractUser):
    profile_image = models.ImageField(upload_to='profile_images/', default='images/profile.jpeg')
    phone = models.CharField(max_length=15, blank=True, null=True)  # Add phone field
    address = models.TextField(blank=True, null=True)  # Add address field
    wallet = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Add wallet field

    groups = models.ManyToManyField(
        Group,
        related_name='customuser_auth_set',  # Change related_name to be unique
        blank=True,
    )
    
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_auth_set',  # Change related_name to be unique
        blank=True,
    )


  
    
class Brand(models.Model):
    brand_name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    status = models.CharField(max_length=10) 
    country = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/', default='images/default.jpg')
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.brand_name

class Type1(models.Model):
    name = models.CharField(max_length=100)
    count_of_type = models.IntegerField()
    status = models.CharField(max_length=10) 
    image = models.ImageField(upload_to='images/', default='images/default.jpg')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Many-to-many relationship with Product
    products = models.ManyToManyField('Product', related_name='types')

    def __str__(self):
        return self.name

class Edition(models.Model):
    edition_name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    status = models.CharField(max_length=10 ) 
    image = models.ImageField(upload_to='images/', default='images/default.jpg')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Many-to-many relationship with Product
    products = models.ManyToManyField('Product', related_name='editions')

    def __str__(self):
        return self.edition_name


class Variants(models.Model):
    colour = models.JSONField()  # Store an array of colors
    type1 = models.JSONField()    # Store an array of types
    image = models.JSONField()   # Store an array of images
    size = models.JSONField()     # Store an array of sizes
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Many-to-many relationship with Product
    products = models.ManyToManyField('Product', related_name='variants')

    def __str__(self):
        return f'Variants for Product'


class Categories(models.Model):
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE, related_name='categories')
    type1 = models.ForeignKey('Type1', on_delete=models.CASCADE, related_name='categories')
    edition = models.ForeignKey('Edition', on_delete=models.CASCADE, related_name='categories')
    status = models.CharField(max_length=10 )   


    def __str__(self):
        return f'Category: {self.brand.brand_name} - {self.type1.name} - {self.edition.edition_name}'


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    stock = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    ratings = models.FloatField(default=0.0)
    comments = models.TextField(blank=True)
    status = models.CharField(max_length=10) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Foreign Key relationship
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE, related_name='products')
    
    # Optional: Many-to-many relationships already defined in Type1, Edition, and Variants

    def __str__(self):
        return self.name
