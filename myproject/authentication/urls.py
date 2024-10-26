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
]