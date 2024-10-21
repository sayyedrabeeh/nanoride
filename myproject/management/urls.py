from django.urls import path
from . import views
# from .views import block_user
from .views import catogery, add_category, edit_category, delete_category ,toggle_category_status,delete_category,get_suggestions,products,brand,edtion,add_Brand,toggle_status
urlpatterns = [
    path('update_category/<int:pk>/', views.edit_category, name='edit_category'),  # Changed URL
    path('users/', views.users, name='users'),
    path('admin/block_user/<int:user_id>/', views.block_user, name='block_user'),
    path('catogery/', views.catogery, name='catogery'), 
    path('add/', add_category, name='add_category'),
    path('products/', views.products, name='products'),
    path('delete/<int:pk>/', delete_category, name='delete_category'),  
    path('management/list/<int:pk>/', views.list_category, name='list_category'),
    path('management/delist/<int:pk>/', views.delist_category, name='delist_category'),
    path('toggle-category-status/<int:pk>/', toggle_category_status, name='toggle_category_status'),
    path('delete-category/<int:pk>/', delete_category, name='delete_category'),
    path('api/suggestions/', get_suggestions, name='get_suggestions'),   
    path('catogery/', views.catogery, name='catogery'), 
    path('brand/', views.brand, name='brand'), 
    path('add-brand/', add_Brand, name='add_brand'),
    path('update-brand/', views.update_brand, name='update_brand'),
    path('edtion/', views.edtion, name='edtion'), 
    path('type1/', views.type1, name='type1'), 
    path('varients/', views.varients, name='varients'), 
    path('toggle-status/', toggle_status, name='toggle_status'),
]