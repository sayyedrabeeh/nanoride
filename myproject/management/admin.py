from .models import CustomUser,Product,Variants,Edition,Type1,Brand

# Register your models here.
from django.contrib import admin
# from .models import CustomUser

admin.site.register(CustomUser)
admin.site.register(Product)
admin.site.register(Variants)
admin.site.register(Edition)
admin.site.register(Type1)
admin.site.register(Brand)
 
