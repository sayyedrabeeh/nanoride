from django.urls import path
from . import views
from .views import custom_logout

urlpatterns = [
    path('signup/', views.usersignup, name='usersignup'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('login/', views.userlogin, name='userlogin'),
    path('resend_otp/', views.resend_otp, name='resend_otp'),
    path('home/', views.home, name='home'),
    path('logout/', custom_logout, name='custom_logout'),
]