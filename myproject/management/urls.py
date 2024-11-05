from django.urls import path
from . import views
# from .views import block_user
from .views import  edit_catogery, delete_catogery ,toggle_category_status,get_suggestions,products1,Brand,edtion,add_brand,toggle_status,edit_brand,list_brand,type1,add_type,edit_type,list_type,Edition1,add_Edition,list_Edition,add_category_view,list_catogery,add_products,list_products,edit_products,product_variants_view,add_variant_view,toggle_listing

from .views import index
urlpatterns = [
    path('edit_catogery/<int:pk>/', views.edit_catogery, name='edit_catogery'),  
    path('users/', views.users, name='users'),
    path('admin/block_user/<int:user_id>/', views.block_user, name='block_user'),
    # path('catogery/', views.catogery, name='catogery'), 
    # path('add_catogery/', add_catogery, name='add_catogery'),
    path('products/', views.products1, name='products'),
    path('add_products/', add_products, name='add_products'),
    
    path('edit_products/<int:product_id>/', edit_products, name='edit_products'),
    path('delete/<int:pk>/', delete_catogery, name='delete_catogery'),  
    path('management/list/<int:pk>/', views.list_catogery, name='list_catogery'),
    path('management/delist/<int:pk>/', views.delist_catogery, name='delist_catogery'),
    path('toggle-category-status/<int:pk>/', toggle_category_status, name='toggle_category_status'),
    path('delete-category/<int:pk>/', delete_catogery, name='delete_category'),
    path('api/suggestions/', get_suggestions, name='get_suggestions'),   
    # path('catogery/', views.catogery, name='catogery'), 
    path('brand/', views.brand, name='brand'), 
    path('add_brand/', add_brand, name='add_brand'),
    # path('edit-brand/', views.edit_brand, name='edit_brand'),
    path('edtion/', views.edtion, name='edtion'), 
    path('varients/<int:product_id>/', views.varients, name='varients'),
    # path('viewvarients/<int:id>/', views.viewvarients, name='viewvarients'), 
    path('toggle-status/', toggle_status, name='toggle_status'),
    path('edit-brand/<int:id>/', edit_brand, name='edit_brand'),
    path('type1/', type1, name='type1'),
    path('add_type/', add_type, name='add_type'),
    path('edit_type/<int:id>/', views.edit_type, name='edit_type'),
    path('list_brand/',list_brand , name='list_brand'),
    path('list_type/',list_type , name='list_type'),
    path('Edition/', Edition1, name='Edition'),
    path('add_Edition/', add_Edition, name='add_Edition'),
    path('list_Edition/',list_Edition , name='list_Edition'),
    path('edit_Edition/<int:id>/', views.edit_Edition, name='edit_Edition'),
    path('add_category_view/', add_category_view, name='add_category_view'),
    path('list_catogery/',list_catogery , name='list_catogery'),
    path('list_products/',list_products , name='list_products'),
    path('', index, name='index'),
    path('variants/edit/<int:id>/', views.edit_variant, name='edit_variant'),
    path('products/<int:product_id>/variants/', product_variants_view, name='variants'),
    path('<int:product_id>/variants/add/', views.add_variant_view, name='add_variant'),
    # path('products/<int:product_id>/variants/edit/<int:variant_id>/', edit_variant_view, name='edit_variant'),
    path('<int:product_id>/variants/<int:variant_id>/edit/', views.edit_variant, name='edit_variant'),
    path('management/variants/<int:variant_id>/toggle/', toggle_listing, name='toggle_listing'),
    path('question/',views.question,name='question'),
    # path('submit_question/', views.submit_question, name='submit_question'),
    path('submit_question/', views.submit_question, name='submit_question'),
    path('update-status/', views.update_order_item_status, name='update_order_item_status'),
    path('update-status/<int:orderitem_id>/', views.update_status, name='update_status'),




 

 ]