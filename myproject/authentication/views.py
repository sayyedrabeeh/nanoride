from django.shortcuts import render,get_object_or_404
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
from django.contrib.auth import logout
from django.contrib.auth import password_validation
from django.contrib.auth import authenticate, login
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse
from management.models import Product,Variants
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import TemplateView
from django.contrib import messages
from django.http import JsonResponse
import json
from .models import ProductQuestion,CustomUser,Address,Cart
from authentication.models import CustomUser
from django.contrib.auth.views import LoginView
from management.models import Review 
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth import update_session_auth_hash


def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_superuser:  # Check if the user is a superuser
                login(request, user)
                messages.success(request, 'Login successful!')
                return redirect('users')  # Redirect to your admin dashboard
            else:
                messages.error(request, 'You do not have permission to access this area.')
                return redirect('admin_login')  # Redirect back to login
         

    # Render the login page if GET request or invalid login
    return render(request, 'adminside/login1.html')

# Create your views here.
def generate_otp():
    return str(random.randint(100000, 999999))

def usersignup(request):
    if request.user.is_authenticated:
        return redirect('users')
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
            user = CustomUser(username=username, email=email)
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
# def verify_otp(request):
def verify_otp(request):
    # Check if the user is already authenticated
    if request.user.is_authenticated:
        return redirect('home')

    # Handle POST request to verify OTP
    if request.method == 'POST':
        # Retrieve the OTP inputs and filter out None values
        otp_inputs = [
            request.POST.get('otp_1'),
            request.POST.get('otp_2'),
            request.POST.get('otp_3'),
            request.POST.get('otp_4'),
            request.POST.get('otp_5'),
            request.POST.get('otp_6'),
        ]
        
        # Join the remaining strings to form the entered OTP
        entered_otp = ''.join(filter(None, otp_inputs))
        
        # Retrieve the generated OTP and user data from the session
        generated_otp = request.session.get('otp')
        user_data = request.session.get('user_data')

        # Debug prints
        print('Generated OTP:', generated_otp)
        print('Entered OTP:', entered_otp)
        
        # Check OTP expiration
        otp_generated_time = request.session.get('otp_generated_time')
        otp_expiration_time = request.session.get('otp_expiration_time', 300)  # Default to 5 minutes
        current_time = time.time()

        # Check if the OTP has been generated
        if otp_generated_time is None:
            messages.error(request, 'No OTP generated. Please request a new one.')
            return redirect('request_otp')  # Redirect to where the OTP can be requested

        # Check if the current time exceeds the expiration time
        if current_time - otp_generated_time > otp_expiration_time:
            messages.error(request, 'Your OTP has expired. Please request a new one.')
            return render(request, 'userside/otp.html', context={'otp_form': True})

        # Check if the entered OTP matches the generated OTP
        if entered_otp == generated_otp:
            print('Valid OTP:', entered_otp)

            # Check if user data exists in session
            if user_data:
                # Create a new user instance
                user = CustomUser(username=user_data['username'], email=user_data['email'])
                user.set_password(user_data['password'])

                try:
                    # Validate and save the user
                    user.full_clean()  # Validate user fields
                    user.save()  # Save the user to the database
                    messages.success(request, 'Account created successfully!')

                    # Log the user in
                    login(request, user, backend='allauth.account.auth_backends.AuthenticationBackend')

                    # Clear session data after successful registration
                    del request.session['otp']
                    del request.session['user_data']
                    return redirect('home')  # Redirect to the dashboard or home page
                except ValidationError as e:
                    messages.error(request, f'Error creating account: {str(e)}')
            else:
                messages.error(request, 'User data not found in session.')
        else:
            messages.error(request, 'Invalid OTP or expired OTP. Please try again.')

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
    User = get_user_model() 
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print('username:',username)
        print('password:',password)
        # Check if the user exists
        if not CustomUser.objects.filter(username=username).exists():
            
            messages.error(request, 'User does not exist. Please sign up.')
            return render(request, 'account/login.html', {'username': username})

        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        print('user :',user)
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
    return redirect(reverse( 'login' )) 

def home(request):
    products=Product.objects.all()
    products = Product.objects.prefetch_related('variants__images').all()
    context={
        'products':products
    }
    return render(request,'userside/home.html',context)

@login_required
def userproducts(request):
    
    products = Product.objects.prefetch_related('variants__images').all()
    
    context={
        'products':products
    }
    
    return render(request,'userside/products.html',context)


@csrf_exempt 
def submit_review(request, id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=id)
        name = request.POST.get('name')
        rating = int(request.POST.get('rating'))
        comment = request.POST.get('comment')

        # Create and save the review
        review = Review(product=product, name=name, rating=rating, comment=comment)
        review.save()

        return JsonResponse({'success': True, 'review': {
            'name': review.name,
            'rating': review.rating,
            'comment': review.comment,
            'created_at': review.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }})

    return JsonResponse({'success': False})


@login_required
def singleproduct(request, id):
    # cart = get_object_or_404(Cart, user=request.user)
    # variant = get_object_or_404(Variants, product=product)  # Use this line only if you want the first variant

    cart, created = Cart.objects.get_or_create(user=request.user)



    product = get_object_or_404(Product, id=id)
    additional_images = product.additional_images.all()
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]



    variants = product.variants.all()
    if not variants:  # Check if variants exist
        # Handle the case where the product has no variants
        return render(request, 'userside/singleproduct.html', {
            'product': product,
            'error_message': "This product has no available variants."
        })






    # Prepare variants data for the current product
    variants_data = []
    for variant in product.variants.all():
        images = [{'image': img.image.url} for img in variant.images.all()]
        variants_data.append({
            'id': variant.id,
            'colour': variant.colour,
            'size': variant.size,
            'type1': variant.type1,
            'price': variant.price,
            'description': product.description,
            'stock': variant.stock,
            'images': images,
        })

    # Set the default variant
    default_variant = variants_data[0] if variants_data else {'images': [], 'price': 0, 'description': '', 'stock': 0}
    
    # Get the latest five reviews
    reviews = Review.objects.filter(product=product).order_by('-created_at')[:5]
    answered_questions = ProductQuestion.objects.filter(product=product, status='answered').exclude(answered_privately=True).order_by('-answered_at')[:5]
    print('answered_questions :',answered_questions)

    for question in answered_questions:
        question.username = question.email.split('@')[0] 
        
        
    unique_colors = set(variant['colour'] for variant in variants_data)
    unique_sizes = set(variant['size'] for variant in variants_data)
    unique_types = set(variant['type1'] for variant in variants_data)
    materials = set(variant['type1'] for variant in variants_data)

    # Retrieve the first image for each related product's default variant
    related_products_with_images = []
    for related_product in related_products:
        first_image = None
        if related_product.variants.exists():
            first_variant = related_product.variants.first()
            if first_variant.images.exists():
                first_image = first_variant.images.first().image.url
        related_products_with_images.append({
            'product': related_product,
            'first_image': first_image
        })
        print('answered_questions :',answered_questions)
    # Add star range for star ratings in template
    star_range = range(1, 6)

    context = {
        'product': product,
        'additional_images': additional_images,
        'variants_data': variants_data,
        'default_variant': default_variant,
        'unique_colors': unique_colors,
        'unique_sizes': unique_sizes,
        'unique_types': unique_types,
        'materials': materials,
        'reviews': reviews,  # Limit to first five reviews
        'related_products_with_images': related_products_with_images,
        'star_range': star_range, 
        'answered_questions': answered_questions,# Pass star range to template
        'cart':cart,
        'variant':variant
    }

    return render(request, 'userside/singleproduct.html', context)

def custom_logout(request):
    logout(request)  # Log the user out
    request.session.flush()  # Clear the session data
    return redirect('userlogin')

def restricted_view(request):
    # Check if the user is authenticated
    if not request.user.is_authenticated:
        messages.info(request, "Please log in to access this page.")
        return redirect('custom_login')  # Redirect to login if not authenticated
    return render(request, 'restricted.html') 


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin to restrict access to admin users."""
    def test_func(self):
        if self.request.user.is_superuser:
            return True
        else:
            messages.error(self.request, "You do not have permission to access this area.")
            return False

class AdminHomeView(AdminRequiredMixin, TemplateView):
    template_name = 'adminside/users.html'

    def handle_no_permission(self):
        return redirect('admin_login')  # Redirect to admin login if not permitted
    
def custom_logoutadmin(request):
    logout(request)  # Log the user out
    messages.success(request, "You have been logged out successfully.")  # Optional: Add a success message
    return redirect('admin_login') 

# def color_to_rgb(color):
#     # Example mapping, you can expand this
#     color_dict = {
#         'red': (255, 0, 0),
#         'blue': (0, 0, 255),
#         'green': (0, 255, 0),
#         'yellow': (255, 255, 0),
#         # Add more colors as needed
#     }
#     return color_dict.get(color.lower(), (255, 255, 255))


def profile(request):
    user = request.user  # Get the logged-in user
    addresses = Address.objects.filter(user=user, status='listed')   
    default_address = addresses.filter(is_default=True).first()  # Get the default address
    print("Default Address:", default_address)  

    if request.method == 'POST':
        # Update user details
        username = request.POST.get('username', user.username)
        if username:  # Ensure username is not empty or null
           user.username = username
           user.phone = request.POST.get('phone', user.phone)
           user.dob = request.POST.get('dob', user.dob)
           user.gender = request.POST.get('gender', user.gender)
           user.city = request.POST.get('city', user.city)
           user.country = request.POST.get('country', user.country)

        if 'profile_image' in request.FILES:
            user.profile_image = request.FILES['profile_image']
        
        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('profile')

    context = {
        'user': user,
        'addresses': addresses,
        'default_address': default_address
    }
    return render(request, 'userside/profile.html', context)
# @never_cache
def profile_view(request):
    user = request.user  # Assuming the user is logged in
    default_address = Address.objects.filter(user=request.user, is_default=True).first()# Get default address


    if request.method == 'POST':
       
        # Check if the profile_image is part of the POST request
        if 'profile_image' in request.FILES:
            # Update the user's profile image
            user.profile_image = request.FILES['profile_image']
            user.save()
            messages.success(request, "Profile image updated successfully!")
            return redirect('profile')  # Redirect to the profile page after updating

    context = {
        'user': user,
        'default_address': default_address

    }
    return render(request, 'userside/profile.html', context)


def restpassword(request):
    old = ''
    new = ''
    comform = ''
    if request.method=='POST':
        old=request.POST.get('oldPassword')
        new=request.POST.get('newPassword')
        comform=request.POST.get('confirmNewPassword')
        
        print('oldpass:',old)
        print('newpass:',new)
        print('compass:',comform)
        
        if new!= comform:
            print('not equl')
            messages.error(request,'password deos not match')
            return render(request, 'userside/profile.html', {
                'oldPassword': old,
                'newPassword': new,
                'confirmNewPassword': comform,
            })
        
        if len(new) < 6:
            messages.error(request, 'New password must be at least 6 characters long.')
            return render(request, 'userside/profile.html', {
                'oldPassword': old,
                'newPassword': new,
                'confirmNewPassword': comform,
            })
        
        user = authenticate(username=request.user.username, password=old)
        
        if user is not None:
            user.set_password(new)
            user.save()
            update_session_auth_hash(request, user)   
              
             
            return redirect('profile')
        else:
             messages.error(request, 'Old password is incorrect.')
             return render(request, 'userside/profile.html', {
                'oldPassword': old,
                'newPassword': new,
                'confirmNewPassword': comform,
            })
    return render(request, 'userside/profile.html')  # Render your template as needed

 

def add_address(request):
    address = Address.objects.filter(user=request.user)

    if request.method=='POST':
        address_line1 = request.POST.get('addressLine1')
        
        city = request.POST.get('city')
        state = request.POST.get('state')
        postalCode = request.POST.get('postalCode')
        country = request.POST.get('country')
        phoneNumber = request.POST.get('phoneNumber')
        
        Address.objects.create(
            user=request.user,
            address_line1=address_line1,
            
            city=city,
            state=state,
            postal_code=postalCode,
            country=country,
            phone_number=phoneNumber,
          
        )
        messages.success(request, 'Address added successfully!')
        return redirect('profile') 
        context={
             'address': address
        }

    return render(request,'userside/profile.html')

def set_default_address(request):
    if request.method == 'POST':
        address_id = request.POST.get('default_address')
        print("Address ID:", address_id)  # Debugging statement to see what was received
        
        if address_id:
            # Set all addresses to is_default=False for the current user
            Address.objects.filter(user=request.user).update(is_default=False)
            
            # Set the selected address to is_default=True
            Address.objects.filter(id=address_id, user=request.user).update(is_default=True)
            print(f"Address with ID {address_id} set to default.")
        else:
            print("No address selected")  # Optional debugging for the case when nothing is submitted

    return redirect('profile')
def edit_address(request , address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    # address = get_object_or_404(Address, id=address_id)
    print('hi',address_id)
    if request.method =='POST':
        print('hi')
        address.address_line1 = request.POST.get('addressLine1', address.address_line1)
        print(f"Updating address_line1 to: {address.address_line1}") 
        address.city = request.POST.get('city', address.city)
        address.state = request.POST.get('state', address.state)
        address.postal_code = request.POST.get('postalCode', address.postal_code)
        address.country = request.POST.get('country', address.country)
        address.phone_number = request.POST.get('phoneNumber', address.phone_number)

        address.save()
        print( 'new',address)
        messages.success(request, "Address updated successfully!")
        show_messages = True
        return redirect('profile')  # Redirect to the profile page or another appropriate page

    context={
      'address':address ,
      
    }
    return render(request,'userside/profile.html',context)

def unlist_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.status = 'unlisted'
    address.save()
    return redirect('profile') 

def restore_all_addresses(request):
    Address.objects.filter(user=request.user).update(status='listed')
    return redirect('profile') 


def add_to_cart(request, variant_id):
    print('iiii',variant_id)
    variant = get_object_or_404(Variant, id=variant_id)
    
    # Get or create the cart for the user
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Get or create the cart item
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, variant=variant)
    
    if not item_created:
        # If the item already exists, increment the quantity
        cart_item.quantity += 1
        cart_item.save()
    
    return redirect('cart')

def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()  # Fetch related CartItems for this cart
    
    return render(request, 'userside/cart.html', {'cart': cart, 'cart_items': cart_items})