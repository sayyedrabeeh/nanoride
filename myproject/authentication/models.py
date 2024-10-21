from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class CustomUser(AbstractUser):
    profile_image = models.ImageField(upload_to='profile_images/', default='images/profile.jpeg')

    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',  # Change related_name
        blank=True,
    )
    
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',  # Change related_name
        blank=True,
    )
