from django.urls import path
from . import views
from .views import custom_logout,custom_logoutadmin

urlpatterns = [
    path('signup/', views.usersignup, name='usersignup'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('login/', views.userlogin, name='userlogin'),
    path('resend_otp/', views.resend_otp, name='resend_otp'),
    path('home/', views.home, name='home'),
    path('logout/', custom_logout, name='custom_logout'),
    path('userproducts/', views.userproducts, name='userproducts'),
    path('singleproduct/<int:id>/', views.singleproduct, name='singleproduct'),
    path('logout/', custom_logout, name='logout'),
    path('restricted/', views.restricted_view, name='restricted'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-home/', views.AdminHomeView.as_view(), name='admin_home'),
    path('custom_logout1/', custom_logoutadmin, name='custom_logout1'),
    path('submit_review/<int:id>/', views.submit_review, name='submit_review'),
    path('profile/',views.profile,name='profile'),
    path('profile_view/',views.profile_view,name='profile_view'),
    path('restpassword/',views.restpassword,name='restpassword'),
    path('add_address/', views.add_address, name='add_address'),
    path('edit_address/<int:address_id>/', views.edit_address, name='edit_address'),
    path('set-default-address/', views.set_default_address, name='default_address'),
    path('unlist-address/<int:address_id>/', views.unlist_address, name='unlist_address'),
    path('restore-all-addresses/', views.restore_all_addresses, name='restore_all_addresses'),
    path('add-to-cart/<int:variant_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='cart'),

 ]