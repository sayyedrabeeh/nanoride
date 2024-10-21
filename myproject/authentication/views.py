from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_protect
import random
from django.views.decorators.csrf import csrf_exempt
import time
from django.contrib.auth import password_validation
from django.contrib.auth import authenticate, login
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse
# from .views import custom_logout
# Create your views here.
def generate_otp():
    return str(random.randint(100000, 999999))

def usersignup(request):
    # if request.user.is_authenticated:
    #     return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Check for existing username or email
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
        elif password1 != password2:
            messages.error(request, 'Passwords do not match.')
        elif len(password1)<6:
            messages.error(request, 'Passwords must be six charecter.')
        else:
            # Create a new user but don't save yet
            user = User(username=username, email=email)
            user.set_password(password1)

            # Generate and send OTP
            otp = generate_otp()
            print("generated otp",otp)
            subject = 'Your OTP Code'
            message = f'Your OTP code is {otp}'
            from_email = settings.EMAIL_HOST_USER
            
            try:
                send_mail(subject, message, from_email, [email])
                # Store OTP and user data in session for verification
                request.session['otp'] = otp
                request.session['otp_generated_time'] = time.time()  # Store the current time
                request.session['otp_expiration_time'] = 300
                request.session['resend_otp_time'] = 30   
                request.session['user_data'] = {'username': username, 'email': email, 'password': password1}
                return redirect('verify_otp')  # Redirect to OTP verification page
            except Exception as e:
                messages.error(request, f'Error sending email: {str(e)}')
                return render(request, 'userside/otp.html',{'error': str(e)})  # Render the signup form again

    return render(request, 'userside/usersignup.html')  



@csrf_protect
def verify_otp(request):
    # if request.user.is_authenticated:
    #     return redirect('home')
    if request.method == 'POST':
        # Retrieve the OTP inputs and handle None values
        otp_inputs = [
            request.POST.get('otp_1'),
            request.POST.get('otp_2'),
            request.POST.get('otp_3'),
            request.POST.get('otp_4'),
            request.POST.get('otp_5'),
            request.POST.get('otp_6'),
        ]
        
        # Filter out None values and join the remaining strings
        entered_otp = ''.join(filter(None, otp_inputs))
        
        generated_otp = request.session.get('otp') 
        user_data = request.session.get('user_data')
        print('genereted otp :',generated_otp)
        print('entered_otp :',entered_otp)
        
         # Check OTP expiration
         
           # Check OTP expiration
        otp_generated_time = request.session.get('otp_generated_time')
        otp_expiration_time = request.session.get('otp_expiration_time', 0)
        current_time = time.time()

        if current_time - otp_generated_time > otp_expiration_time:
            messages.error(request, 'Your OTP has expired. Please request a new one.')
            return render(request, 'userside/otp.html', context={'otp_form': True})

        
        # Check if the entered OTP matches the generated OTP
        if entered_otp == generated_otp:
            print('genereted otp :',generated_otp)
            print('entered_otp :',entered_otp)
            if user_data:
                # Create a new user instance
                user = User(username=user_data['username'], email=user_data['email'])
                user.set_password(user_data['password'])

                try:
                    # Validate and save the user
                    user.full_clean()
                    user.save()
                    messages.success(request, 'Account created successfully!')
                    
                    # Log the user in
                    login(request, user)
                    
                    # Clear session data after successful registration
                    del request.session['otp']
                    del request.session['user_data']
                    return redirect('userlogin') # Redirect to the dashboard or home page
                except ValidationError as e:
                    messages.error(request, f'Error creating account: {str(e)}')
            else:
                messages.error(request, 'User data not found in session.')
        else:
            messages.error(request, 'Invalid OTP or expired OTP Please try again.')
        
        # Render the same template with an error message
        return render(request, 'userside/otp.html', context={'otp_form': True})

    # Handle GET requests
    return render(request, 'userside/otp.html', context={'otp_form': True})

@csrf_exempt  # Use with caution; better to handle CSRF properly
def resend_otp(request):
    if request.method == 'POST':
        last_resend_time = request.session.get('otp_generated_time', 0) + request.session.get('resend_otp_time', 0)
        # Retrieve the user's email from the session
        email = request.session.get('user_data', {}).get('email')  # Assuming user_data is stored in session
         
        if time.time() < last_resend_time:
            return JsonResponse({'status': 'error', 'message': 'Please wait before requesting a new OTP.'})
        email = request.session.get('user_data', {}).get('email')
        
        if not email:
            return JsonResponse({'status': 'error', 'message': 'User not found in session.'})

        # Generate a new OTP
        otp = generate_otp()  # Replace this with your OTP generation logic

        # Prepare email details
        subject = 'Your OTP Code'
        message = f'Your new OTP code is {otp}'
        from_email = settings.EMAIL_HOST_USER

        try:
            # Send the OTP email
            send_mail(subject, message, from_email, [email])
            # Update the session with the new OTP and expiration time
            request.session['otp'] = otp
            request.session['otp_generated_time'] = time.time()  # Record the current time
            request.session['otp_expiration_time'] = 300  # Set expiration time to 30 seconds

            return JsonResponse({'status': 'success', 'message': 'OTP has been resent.'})  # Return success response
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})  # Handle any errors during email sending

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}) 



def userlogin(request):
    # if request.user.is_authenticated:
    #     return redirect('app1:home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check if the user exists
        if not User.objects.filter(username=username).exists():
            print('ffffffffffffff',username)
            messages.error(request, 'User does not exist. Please sign up.')
            return render(request, 'account/login.html', {'username': username})

        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        print('ffffffffvv',user)
        if user is not None:
              if not user.is_active:
                    messages.error(request, "You are not allowed to log in.")
                    return render(request, 'login.html')
              auth_login(request, user)
              return redirect('home')
        else:
            messages.error(request, 'Username or Password is wrong.')
            return render(request, 'account/login.html', {'username': username})

    return render(request, 'account/login.html')

class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()
        try:
            user = User.objects.get(username=username)
            if not user.is_active:  # Check if user is blocked
                return None
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

   
def custom_logout(request):
    logout(request)  # Log out the user
    # Optionally, add any additional logic here (e.g., logging, notifications)
    return redirect(reverse( 'custom_login' )) 

def home(request):
    return render(request,'userside/home.html')