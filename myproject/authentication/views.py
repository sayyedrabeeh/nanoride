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
import logging
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
import time
import uuid
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
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
from .models import ProductQuestion,CustomUser,Address,Cart,CartItem,Order,OrderItem
from authentication.models import CustomUser
from django.contrib.auth.views import LoginView
from management.models import Review 
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash
from django.db.models import Sum,F
# import geocoder

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
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(name__icontains=search_query)

    # Price filter
    price = request.GET.get('price')
    if price:
        products = products.filter(variants__price__lte=price)

    # Color filter
    color = request.GET.getlist('color')
    if color:
        products = products.filter(variants__color__in=color)

    # Costume type filter
    costume_type = request.GET.getlist('costume')
    if costume_type:
        products = products.filter(variants__costume_type__in=costume_type)

    # Sorting
    sort = request.GET.get('sort')
    if sort == 'price_low_to_high':
        products = products.order_by('variants__price')
    elif sort == 'price_high_to_low':
        products = products.order_by('-variants__price')

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
        'variants':variants,
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


 

# @login_required
# def add_to_cart(request, id):
#     print('id:',id)
#     variant = get_object_or_404(Variants, id=id)
#     cart, created = Cart.objects.get_or_create(user=request.user)
#     cart_item, item_created = CartItem.objects.get_or_create(cart=cart, variant=variant)
    
#     if not item_created:
#         cart_item.quantity += 1
#         cart_item.save()
    
#     return redirect('cart')


def add_to_cart(request):
    if request.method == 'POST':
        variant_id = request.POST.get('variant_id')
        quantity = int(request.POST.get('quantity', 1))

        # Fetch the selected variant
        variant = get_object_or_404(Variants, id=variant_id)
        
        # Check stock availability
        if quantity > variant.stock:
            messages.error(request, 'The requested quantity is not available.')
            return redirect('product_detail', product_id=variant.product.id)

        # Get or create the cart for the user
        cart, created = Cart.objects.get_or_create(user=request.user)

        # Add or update the cart item
        cart_item, item_created = CartItem.objects.get_or_create(cart=cart, variant=variant)

        if not item_created:
            cart_item.quantity += quantity
            cart_item.save()
        else:
            cart_item.quantity = quantity
            cart_item.save()

        messages.success(request, 'Item added to cart successfully.')
        return redirect('cart')
    else:
        return redirect('home') 
 
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()  # Get all cart items for this user
    
    cart_total = 0
    cart_data = []

    for item in cart_items:
        variant = item.variant
        item_total = variant.price * item.quantity
        cart_total += item_total
        
        # Get the first image of this variant if it exists
        first_image = variant.images.first().image.url if variant.images.exists() else None
        
        cart_data.append({
            'product_name': variant.product.name,
            'color': variant.colour,
            'size': variant.size,
            'type': variant.type1,
            'price': variant.price,
            'quantity': item.quantity,
            'total_price': item_total,
            'first_image': first_image,
            'cart_item_id': item.id
        })

    return render(request, 'userside/cart.html', {
        'cart_data': cart_data,
        'cart_total': cart_total
    })
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    if request.POST.get('action') == 'increase':
        cart_item.quantity += 1
    elif request.POST.get('action') == 'decrease' and cart_item.quantity > 1:
        cart_item.quantity -= 1
    
    cart_item.save()
    return redirect('cart')

#  

@method_decorator(csrf_exempt, name='dispatch')  # Only if you're not using CSRF tokens
def update_cart_item(request, item_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            quantity = data.get('quantity')
            
            # Here you would update the quantity in your database
            # Assuming you have a CartItem model
            cart_item = CartItem.objects.get(id=item_id)
            cart_item.quantity = quantity
            cart_item.save()

            return JsonResponse({'message': 'Quantity updated successfully!'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)



def delete_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, 'Item removed from cart successfully.')
    return redirect('cart')

# def checkout(request):
#     # Ensure the user is authenticated
#     if not request.user.is_authenticated:
#         return redirect('login')  # Redirect to login if the user is not authenticated

#     # Get the cart items based on the user's cart
#     cart_items = CartItem.objects.filter(cart__user=request.user)
#     print('cart_items:', cart_items)
    
#     # Fetch user addresses
#     user_addresses = Address.objects.filter(user=request.user, status="listed")

#     # Initialize item_details list
#     item_details = []
#     first_image = variants.images.first().image.url if variants.images.exists() else None

#     # Gather item details directly from cart_items
#     for item in cart_items:
#         item_total_price = item.variant.price * item.quantity  # Calculate total price for each item
        
#         # Append item details for rendering, including variant properties
#         item_details.append({
#             'image':  item.variant.product.image.url if item.variant.product.image else '',  # Adjust to point to the correct image field
#             'name': item.variant.product.name,
#             'quantity': item.quantity,
#             'price_per_unit': item.variant.price,
#             'total_price': item_total_price,
#             'color': item.variant.colour,  # Access color
#             'size': item.variant.size,    # Access size
#             'type': item.variant.type1,
#             'first_image': first_image,
# # Access type
#         })

#     # Calculate the total price for all items in the cart
#     total_price = sum(detail['total_price'] for detail in item_details)
#     print('item_details:', item_details)

#     # Prepare the context to pass to the template
#     context = {
#         'user_addresses': user_addresses,
#         'item_details': item_details,  # Pass item_details to the template
#         'cart_total': total_price,     # Total price for checkout
#     }

#     return render(request, 'userside/checkout.html', context)


@never_cache
# def checkout(request):
#     # Ensure the user is authenticated
#     if not request.user.is_authenticated:
#         return redirect('login')  # Redirect to login if the user is not authenticated

#     # Get the cart items based on the user's cart
#     cart_items = CartItem.objects.filter(cart__user=request.user)  # Filter cart items for the logged-in user
#     print('cart_items:', cart_items)
    
#     # Fetch user addresses
#     user_addresses = Address.objects.filter(user=request.user, status="listed")

#     # Initialize item_details list
#     item_details = []  
#     cart_total = 0  # Initialize cart total

#     # Gather item details directly from cart_items
#     for item in cart_items:
#         variant = item.variant  # Get the variant for the cart item
#         item_total_price = variant.price * item.quantity  # Calculate total price for each item
#         cart_total += item_total_price  # Update the cart total
        
#         # Get the first image of this variant if it exists
#         first_image = variant.images.first().image.url if variant.images.exists() else None
        
#         # Append item details for rendering, including variant properties
#         item_details.append({
#             'image': first_image,  # First image of the variant
#             'name': variant.product.name,
#             'quantity': item.quantity,
#             'price_per_unit': variant.price,
#             'total_price': item_total_price,
#             'color': variant.colour,  # Access color
#             'size': variant.size,    # Access size
#             'type': variant.type1,   # Access type
#         })

#     # Prepare the context to pass to the template
#     context = {
#         'user_addresses': user_addresses,
#         'item_details': item_details,  # Pass item_details to the template
#         'cart_total': cart_total,
#         'warning_message': request.GET.get('warning_message'),  # Check for warning message
# # Total price for checkout
#     }

#     return render(request, 'userside/checkout.html', context)




def checkout(request):
    # Ensure the user is authenticated
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to login if the user is not authenticated

    # Initialize variables
    item_details = []
    cart_total = 0  # Initialize cart total

    # Check if the request is a single checkout or cart checkout
    variant_id = request.POST.get('variant_id')  # Check for a variant ID in the POST request

    if variant_id:  # User is checking out a single item
        # Fetch the variant or return a 404 error if it doesn't exist
        variant = get_object_or_404(Variants, id=variant_id)
        
        # Prepare item details for the single checkout
        item_total_price = variant.price  # Total price for the single item
        first_image = variant.images.first().image.url if variant.images.exists() else None
        
        # Append item details for rendering, including variant properties
        item_details.append({
            'image': first_image,  # First image of the variant
            'name': variant.product.name,
            'quantity': 1,  # Since this is a single checkout, quantity is 1
            'price_per_unit': variant.price,
            'total_price': item_total_price,
            'color': variant.colour,  # Access color
            'size': variant.size,    # Access size
            'type': variant.type1,   # Access type
        })

        cart_total = item_total_price  # Total for the single item checkout

    else:  # User is checking out from the cart
        # Get the cart items based on the user's cart
        cart_items = CartItem.objects.filter(cart__user=request.user)  # Filter cart items for the logged-in user
        
        # Fetch user addresses
        user_addresses = Address.objects.filter(user=request.user, status="listed")

        # Gather item details directly from cart_items
        for item in cart_items:
            variant = item.variant  # Get the variant for the cart item
            item_total_price = variant.price * item.quantity  # Calculate total price for each item
            cart_total += item_total_price  # Update the cart total
            
            # Get the first image of this variant if it exists
            first_image = variant.images.first().image.url if variant.images.exists() else None
            
            # Append item details for rendering, including variant properties
            item_details.append({
                'image': first_image,  # First image of the variant
                'name': variant.product.name,
                'quantity': item.quantity,
                'price_per_unit': variant.price,
                'total_price': item_total_price,
                'color': variant.colour,  # Access color
                'size': variant.size,    # Access size
                'type': variant.type1,   # Access type
            })

    # Get user addresses for the checkout
    user_addresses = Address.objects.filter(user=request.user, status="listed")

    # Prepare the context to pass to the template
    context = {
        'user_addresses': user_addresses,
        'item_details': item_details,  # Pass item_details to the template
        'cart_total': cart_total,
        'warning_message': request.GET.get('warning_message'),  # Check for warning message
    }

    return render(request, 'userside/checkout.html', context)














@never_cache
def single_checkout(request):
    # Ensure the user is authenticated
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to login if the user is not authenticated

    # Get the variant ID from the POST request
    variant_id = request.POST.get('variant_id')
    
    # Fetch the variant or return a 404 error if it doesn't exist
    variant = get_object_or_404(Variants, id=variant_id)

    # Initialize item_details list and other variables
    item_details = []
    item_total_price = variant.price  # Total price for the single item
    first_image = variant.images.first().image.url if variant.images.exists() else None

    # Append item details for rendering, including variant properties
    item_details.append({
        'image': first_image,  # First image of the variant
        'name': variant.product.name,
        'quantity': 1,  # Since this is a single checkout, quantity is 1
        'price_per_unit': variant.price,
        'total_price': item_total_price,
        'color': variant.colour,  # Access color
        'size': variant.size,    # Access size
        'type': variant.type1,   # Access type
    })

    # Get user addresses for the checkout
    user_addresses = Address.objects.filter(user=request.user, status="listed")

    # Prepare the context to pass to the template
    context = {
        'user_addresses': user_addresses,
        'item_details': item_details,  # Pass item_details to the template
        'cart_total': item_total_price,
        'warning_message': request.GET.get('warning_message'),  # Check for warning message
# Total price for checkout
    }

    return render(request, 'userside/checkout.html', context)


logger = logging.getLogger(__name__)
 

def get_address_by_postal_code(request):
    postal_code = request.GET.get('postal_code')
    logger.debug('Received postal code: %s', postal_code)

    if postal_code:
        # Nominatim URL for geocoding
        url = 'https://nominatim.openstreetmap.org/search'
        params = {
            'q': postal_code,
            'format': 'json',
            'addressdetails': 1,
            'limit': 1,
            'accept-language': 'en'
        }
        
        headers = {
            'User-Agent': 'nanoride/1.0 (sayyedrabeeh240@gmail.com)'  # Update this with your app name and contact
        }

        try:
            # Make the API request with headers
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()  # Raise an error for bad responses

            # Parse the JSON response
            data = response.json()
            logger.debug('Nominatim API response: %s', data)

            if data:
                # Extract address details with fallbacks
                address = data[0].get('address', {})
                return JsonResponse({
                    'address_line1': address.get('road', ''),
                    'address_line2': address.get('suburb', ''),
                    'city': address.get('city', address.get('town', '')),  # Fallback to town
                    'state': address.get('state', ''),
                    'country': address.get('country', ''),
                    'postal_code': postal_code
                })

            # Log if no address was found
            logger.warning('No address found for postal code: %s', postal_code)
            return JsonResponse({'error': 'Address not found'}, status=404)

        except requests.exceptions.RequestException as e:
            logger.error('Error fetching address: %s', e)
            return JsonResponse({'error': 'Network error: ' + str(e)}, status=500)

    logger.warning('Postal code not provided or invalid: %s', postal_code)
    return JsonResponse({'error': 'Postal code not provided'}, status=400)


def save_address(request):
    if request.method == 'POST':
        postal_code = request.POST.get('postal_code')
        print('postal_code:',postal_code)
        address_line2 = request.POST.get('address_line1', '')
        print('address_line2:',address_line2)
        city = request.POST.get('city', '')
        print('city:',city)
        state = request.POST.get('state', '')
        country = request.POST.get('country', '')

        # Ensure the user is authenticated
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'User not authenticated'}, status=403)

        try:
            # Create the address entry without address_line1 and phone_number
            address = Address.objects.create(
                user=request.user,
                address_line2=address_line2,
                city=city,
                state=state,
                country=country,
                postal_code=postal_code,
                is_default=False  # Adjust logic for default address if needed
            )
            logger.info('Address saved successfully for user: %s', request.user.username)
            return JsonResponse({'success': 'Address saved successfully!'})
        
        except Exception as e:
            logger.error('Error saving address: %s', e)  # Log the error
            return JsonResponse({'error': 'Error saving address. Please try again.'}, status=500)

    logger.warning('Invalid request method: %s', request.method)
    return JsonResponse({'error': 'Invalid request'}, status=400)


# def place_order(request):
#     if request.method == 'POST':
#         # Create a new Order
#         order = Order(
#             user=request.user,
#             total_price=0,  # This will be calculated later
#             payment_type=request.POST.get('payment_type', 'COD'),  # Replace with your payment logic
#             created_at=timezone.now(),
#         )
#         order.save()  # Save order first to get the order ID
        
#         total_price = 0  # Initialize total price
        
#         # Handle each item
#         for i in range(len(request.POST.getlist('item_id'))):
#             item_id = request.POST.getlist('item_id')[i]
#             item_name = request.POST.getlist('item_name')[i]
#             item_quantity = int(request.POST.getlist('item_quantity')[i])
#             item_color = request.POST.getlist('item_color')[i]
#             item_size = request.POST.getlist('item_size')[i]
#             item_type = request.POST.getlist('item_type')[i]
#             item_price = float(request.POST.getlist('item_price')[i])
#             item_total = float(request.POST.getlist('item_total')[i])
            
#             # Create OrderItem
#             order_item = OrderItem(
#                 order=order,
#                 variants=Variants.objects.get(id=item_id),  # Assuming you have a Variants model
#                 quantity=item_quantity,
#                 price=item_price,
#                 subtotal_price=item_total,
#             )
#             order_item.save()  # Save each OrderItem
            
#             total_price += item_total  # Accumulate total price
            
#         # Update order total price
#         order.total_price = total_price
#         order.save()

#         messages.success(request, 'Order placed successfully!')
#         return redirect('place_order')  # Redirect to a confirmation page
    

#     return render(request,'userside/placeorder.html')


# def place_order(request):
#     print("Starting place_order function")  # Debug print to confirm function call
    
#     if request.method == 'POST':
#         shipping_address_id = request.POST.get('address')  # Get the selected address ID
#         payment_method = request.POST.get('payment')
        
#         print("shipping_address_id:", shipping_address_id)
#         print("payment_method:", payment_method)
#         total_price = request.POST.get('total_price')
#         order_id = new_order.id 
#         # Print the total price to the console
#         print("Total Price:", total_price)
#         if not shipping_address_id or not payment_method:
#             messages.error(request, "Please select a shipping address and payment method.")
#             return redirect('place_order')  # Reload the page if either field is missing
        
#         try:
#             # Fetch the shipping address for the logged-in user
#             shipping_address = Address.objects.get(id=shipping_address_id, user=request.user)
#         except Address.DoesNotExist:
#             messages.error(request, "Selected address does not exist.")
#             return redirect('userproducts')  # Redirect back to the order page

#         # Create the order with a generated tracking number
#         order = Order.objects.create(
#             user=request.user,
#             shipping_address=shipping_address,
#             total_price=total_price,
#             payment_type=payment_method,
#             tracking_number=str(uuid.uuid4().hex[:8])  # Generate tracking number
#         )
#         print()

#         print("Order created:", order)  # Debugging output to verify order creation
        
#         # Fetch items from the user's cart
#         try:
#             cart = Cart.objects.get(user=request.user)
#             cart_items = CartItem.objects.filter(cart=cart)
#         except Cart.DoesNotExist:
#             messages.error(request, "No items in the cart.")
#             return redirect('userproducts')

#         # Add each item in the cart to the OrderItem model
#         for cart_item in cart_items:
#             OrderItem.objects.create(
#                 order=order,
#                 variants=cart_item.variant,
#                 quantity=cart_item.quantity,
#                 price=cart_item.variant.price,
#                 subtotal_price=cart_item.item_total()  # This assumes you have the method defined
#             )
#             print("Order item created for variant:", cart_item.variant)  # Debug output for each item added

#         # Clear the user's cart after placing the order
#         cart.items.all().delete()  # Assuming `items` is the related name for cart items

#         messages.success(request, "Your order has been placed successfully.")
#         return redirect('place_order')  # Redirect to a success page
    
#     else:
#         # Fetch the user's addresses to display in the template
#         shipping_addresses = Address.objects.filter(user=request.user)
#         return render(request, 'userside/placeorder.html', {'shipping_addresses': shipping_addresses})  
    
def place_order(request):
    print("Starting place_order function")  # Debug print to confirm function call
    
    if request.method == 'POST':
        shipping_address_id = request.POST.get('address')  # Get the selected address ID
        payment_method = request.POST.get('payment')
        total_price = request.POST.get('total_price')

        print("shipping_address_id:", shipping_address_id)
        print("payment_method:", payment_method)
        print("Total Price:", total_price)

        if not shipping_address_id or not payment_method:
            messages.error(request, "Please select a shipping address and payment method.")
            return redirect('place_order')  # Reload the page if either field is missing
        
        try:
            # Fetch the shipping address for the logged-in user
            shipping_address = Address.objects.get(id=shipping_address_id, user=request.user)
        except Address.DoesNotExist:
            messages.error(request, "Selected address does not exist.")
            return redirect('place_order')  # Redirect back to the order page

        # Create the order with a generated tracking number
        order = Order.objects.create(
            user=request.user,
            shipping_address=shipping_address,
            total_price=total_price,
            payment_type=payment_method,
            tracking_number=str(uuid.uuid4().hex[:8])  # Generate tracking number
        )
        print("Order created:", order)  # Debugging output to verify order creation
        
        # Fetch items from the user's cart
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items = CartItem.objects.filter(cart=cart)
        except Cart.DoesNotExist:
            messages.error(request, "No items in the cart.")
            return redirect('userproducts')

         
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                variants=cart_item.variant,
                quantity=cart_item.quantity,
                price=cart_item.variant.price,
                subtotal_price=cart_item.item_total()  # This assumes you have the method defined
            )
            print("Order item created for variant:", cart_item.variant)  # Debug output for each item added

        # Clear the user's cart after placing the order
        cart.items.all().delete()  # Assuming `items` is the related name for cart items

        messages.success(request, "Your order has been placed successfully.")
        return redirect('place_order')  # Redirect to the order detail page with the new order ID
    
    else:
        # Fetch the user's addresses to display in the template
        shipping_addresses = Address.objects.filter(user=request.user)
        return render(request, 'userside/placeorder.html', {'shipping_addresses': shipping_addresses})
    


def order_summary(request):
    # Assume item_details and cart_total are calculated from the session or database
    item_details = request.session.get('cart_items', [])  # Placeholder for cart items
    cart_total = sum(item['total_price'] for item in item_details)  # Assuming item_details is a list of dicts
    
    if request.method == 'POST':
        # Create Order
        order = Order(
            user=request.user,
            total_price=cart_total,
            payment_type=request.POST.get('payment_type', 'COD'),  # You may want to provide a way to select this
        )
        order.save()
        
        # Create OrderItems
        for item in item_details:
            variant = Variants.objects.get(id=item['variant_id'])  # Adjust based on your data structure
            order_item = OrderItem(
                order=order,
                variants=variant,
                quantity=item['quantity'],
                price=item['price_per_unit'],
                subtotal_price=item['total_price'],
            )
            order_item.save()

        messages.success(request, 'Order placed successfully!')
        return redirect('order_confirmation')  # Redirect to a confirmation page

    context = {
        'item_details': item_details,
        'cart_total': cart_total,
    }
    return render(request, 'order_summary.html', context)

def order_confirmation(request):
    return render(request, 'order_confirmation.html')

def order_detail(request):
    # Fetch the order using the given order_id
    # order = get_object_or_404(Order, order_id=order_id)

    order_items = OrderItem.objects.all()
    for item in order_items:
        item.can_return = item.status == "Order Confirmed"
        item.is_return_approved_or_cancelled = item.status in ["Return Approved", "Cancelled"]

    # print('Order:', order)
    print('Order Items:', order_items)
    for item in order_items:
        print(f'Order Item ID: {item.orderitem_id}, Variant ID: {item.variants.id}, Quantity: {item.quantity}, Price: {item.price}')

    context = {
        # 'order': order,
        'order_items': order_items,  # This will contain items for the specific order
    }
    
    return render(request, 'userside/uder_order.html', context)


def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        # Update the status of all order items to 'Cancelled'
        order_items = order.items.all()
        for item in order_items:
            item.status = 'Cancelled'
            item.save()

        # Optionally, update the order status
        order.status = 'Cancelled'
        order.save()

        messages.success(request, 'Your order has been cancelled successfully.')
        return redirect('order_detail', order_id=order.id)  # Redirect to order detail page

    context = {
        'order': order,
    }
    
    return render(request, 'cancel_order.html', context)
 