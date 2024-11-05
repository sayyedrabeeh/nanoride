from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.conf import settings
# from image_cropping import ImageRatioField

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
    status = models.CharField(max_length=10, default='listed')
    country = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/', default='images/default.jpg')
    # cropping = ImageRatioField('image', '300x300')
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.brand_name

class Type1(models.Model):
    name = models.CharField(max_length=100)
    Quantity = models.IntegerField()
    status = models.CharField(max_length=10, default='listed')
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
    status = models.CharField(max_length=10, default='listed')
    image = models.ImageField(upload_to='images/', default='images/default.jpg')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Many-to-many relationship with Product
    products = models.ManyToManyField('Product', related_name='editions')

    def __str__(self):
        return self.edition_name



class Categories(models.Model):
    name = models.CharField(max_length=255)
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE, related_name='categories')
    type1 = models.ForeignKey('Type1', on_delete=models.CASCADE, related_name='categories')
    edition = models.ForeignKey('Edition', on_delete=models.CASCADE, related_name='categories')
    status = models.CharField(max_length=10, default='listed')


    def __str__(self):
        return f'Category: {self.brand.brand_name} - {self.type1.name} - {self.edition.edition_name}'


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    ratings = models.FloatField(default=0.0)
    comments = models.TextField(blank=True)
    status = models.CharField(max_length=10, default='listed') 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='products/',default='products/p.png')  # Directory for storing images
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0)  # Adjust max_digits and decimal_places as needed
    stock = models.PositiveIntegerField(default=0) 
    main_image = models.ImageField(upload_to='product_images/main/', blank=True, null=True)
    video = models.FileField(upload_to='variant_videos/', blank=True, null=True)

    # Foreign Key relationship
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE, related_name='products')
    # Variant = models.ForeignKey('Variants', on_delete=models.CASCADE )
    category = models.ForeignKey('Categories', on_delete=models.CASCADE,default=0 )     # Optional: Many-to-many relationships already defined in Type1, Edition, and Variants
    
     
    def __str__(self):
        return self.name
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='additional_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/extra/')



class Variants(models.Model):
    colour = models.CharField(max_length=50)  # Store a single color
    type1 = models.CharField(max_length=50)   # Store a single type
    size = models.CharField(max_length=20)     # Store a single size
    stock = models.PositiveIntegerField()       # Store stock quantity as a positive integer
    price = models.DecimalField(max_digits=10, decimal_places=2)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status  =models.CharField(default='listed')

    # Many-to-many relationship with Product
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE,default=24)
     # products = models.ManyToManyField('Product', related_name='variants')

    def __str__(self):
        return f'Variants for Product: {self.type1} in {self.colour}'

class VariantImage(models.Model):
    variant = models.ForeignKey(Variants, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='variant_images/')

    def __str__(self):
        return f'Image for Variant: {self.variant.type1} in {self.variant.colour}'
    
    
    
    
class ProductVideo(models.Model):
    product = models.ForeignKey(Product, related_name='videos', on_delete=models.CASCADE)
    video = models.FileField(upload_to='product_videos/',blank=True, null=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f'Video for {self.product.name}'
    
    
    
    
    
class Review(models.Model):
    product = models.ForeignKey('Product', related_name='reviews', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    rating = models.PositiveIntegerField()  # Rating out of 5
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set the date when created

    class Meta:
        ordering = ['-created_at']  # Show newest reviews first

    def __str__(self):
        return f'Review by {self.name} - {self.rating} stars'



 


class SportsCar(models.Model):
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    year = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.brand} {self.name} ({self.year})"