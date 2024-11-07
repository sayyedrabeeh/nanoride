from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from .models import Categories,Brand,Type1,Edition,Product,Variants,VariantImage,ProductImage
from django.shortcuts import render, redirect, get_object_or_404
import logging
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import SportsCar
from authentication.models import ProductQuestion
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.db.models import Sum
from authentication.models import OrderItem
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db.models import Prefetch


STATUS_TRANSITIONS = {
    "Order Pending": ["Order Pending", "Order Confirmed", "Cancelled"],
    "Order Confirmed": ["Order Confirmed", "Shipped", "Cancelled"],
    "Shipped": ["Shipped", "Out For Delivery", "Cancelled"],
    "Out For Delivery": ["Out For Delivery", "Delivered", "Requested Return"],
    "Delivered": ["Delivered", "Requested Return"],
    "Cancelled": ["Cancelled"],
    "Requested Return": ["Requested Return", "Approve Returned", "Reject Returned"],
    "Approve Returned": ["Approve Returned"],
    "Reject Returned": ["Reject Returned"],
}



User = get_user_model()

@never_cache
@login_required(login_url='admin_login')
def users(request):
    all_users = User.objects.order_by('-is_active', 'last_login')
    print(all_users,'lkkjjjjn') 
    return render(request, 'adminside/users.html', {'all_users': all_users})
@never_cache
@login_required(login_url='admin_login')

def block_user(request, user_id):
    User = get_user_model()


    if request.method == 'POST':
        
        user = get_object_or_404(User, id=user_id)
        user.is_active = not user.is_active
        user.save()
        return JsonResponse({'is_active': user.is_active})
    return JsonResponse({'error': 'Invalid request'}, status=400)
@never_cache
@login_required(login_url='admin_login')
def user_details(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        data = {
            "name": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "phone": user.profile.phone,  # Adjust according to your user model
            "address": user.profile.address,  # Adjust accordingly
            "wallet": user.profile.wallet,  # Adjust accordingly
        }
        return JsonResponse(data)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)
    
# def catogery(request):
#     # categories = Categories.objects.all().order_by('-status')
#     brands = Brand.objects.all().order_by('status')
#     print('hiiiiiii',brands)
#     types = Type1.objects.all().order_by('status')
#     editions = Edition.objects.all().order_by('status')
    

#     return render(request, 'adminside/catogery.html', {
       
#         'brands': brands,
#         'types': types,
#         'editions': editions,
#     })
# def add_catogery(request):
#     categories = Categories.objects.all().order_by('-status')
#     if request.method == 'POST':
#         name = request.POST.get('name')
#         brand_id = request.POST.get('brand')  # Get the brand ID as a string
#         edition_id = request.POST.get('edition')  # Get the edition ID as a string
#         type_id = request.POST.get('type1') # Get the edition ID as a string

#         # Retrieve the actual Brand and Edition instances
#         brand = get_object_or_404(Brand, id=brand_id)  # Get Brand instance or 404
#         edition = get_object_or_404(Edition, id=edition_id)  # Get Edition instance or 404
#         type_instance = get_object_or_404(Type1, id=type_id)  # Get Edition instance or 404

#         print(f"Received: name={name}, brand={brand}, edition={edition}")  # Debugging

#         # Create and save the category with the actual Brand and Edition instances
#         category = Categories(name=name, brand=brand, edition=edition,type1=type_instance)
#         category.save()
#         print('saved', category)
        
#         return redirect('catogery')  # Redirect back to the category view after saving

#     return render(request,'adminside/catogery.html',{'categories': categories})
@never_cache
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
                return redirect('admin_login')  # Redirect to your admin dashboard
            else:
                messages.error(request, 'You do not have permission to access this area.')
                return redirect('admin_login')  # Redirect back to login
        else:
            messages.error(request, 'Invalid credentials. Please try again.')
    
    return render(request, 'adminside/login.html')
@never_cache
@login_required(login_url='admin_login')
def edit_catogery(request, pk):
    if request.user.is_authenticated:
        return redirect('home')
    category = get_object_or_404(Categories, pk=pk)

    if request.method == 'POST':
        try:
            # Update the category with the new data from the request
            category.name = request.POST.get('name')
            category.brand = get_object_or_404(Brand, pk=request.POST.get('brand'))
            category.edition = get_object_or_404(Edition, pk=request.POST.get('edition'))
            category.type1 = get_object_or_404(Type1, pk=request.POST.get('type1'))

            # Save the updated category
            category.save()

            # Redirect to the category management page after saving
            return redirect('add_category_view')  # Change this to your actual view name for categories

        except Exception as e:
            # Handle the error (optional)
            print(f"Error updating category: {e}")

    # If the request method is not POST, render the edit form with existing data
    return render(request, 'adminside/edit_category.html', {
        'category': category,
        'brands': Brand.objects.all(),
        'editions': Edition.objects.all(),
        'types': Type1.objects.all(),
    })
@never_cache
@login_required(login_url='admin_login') 
@csrf_exempt  # Use this if you're handling CSRF tokens manually
def delete_catogery(request, pk):
    if request.method == 'POST':
        category = get_object_or_404(Categories, pk=pk)
        category.delete()
        return JsonResponse({'status': 'deleted'})
    return JsonResponse({'error': 'Invalid request'}, status=400)
@never_cache
@login_required(login_url='admin_login')
def list_catogery(request, pk):
    category = get_object_or_404(Categories, pk=pk)
    category.status = 'listed'  # Set to 'listed'
    category.save()
    return JsonResponse({'status': 'listed'})
@never_cache
@login_required(login_url='admin_login')
def delist_catogery(request, pk):
    category = get_object_or_404(Categories, pk=pk)
    category.status = 'delisted'  # Set to 'delisted'
    category.save()
    return JsonResponse({'status': 'delisted'})
@never_cache
@login_required(login_url='admin_login')
def toggle_category_status(request, pk):
    category = get_object_or_404(Categories, pk=pk)
    category.status = 'delisted' if Categories.status == 'listed' else 'listed'
    category.save()
    return JsonResponse({'status': Categories.status})
@never_cache
@login_required(login_url='admin_login')
def get_suggestions(request):
    query = request.GET.get('query', '')
    field = request.GET.get('field', '')

    if field not in ['name', 'brand', 'edition' ]:
        return JsonResponse([], safe=False)

    suggestions = Categories.objects.filter(**{f"{field}__icontains": query}).values_list(field, flat=True).distinct()
    return JsonResponse(list(suggestions), safe=False)




@never_cache
@login_required(login_url='admin_login')
def products1(request):
    products = Product.objects.annotate(total_stock=Sum('variants__stock')).prefetch_related(
        'variants__images'
    )
    # products = Product.objects.all()
    categories = Categories.objects.all() # Fetch all products
    brands = Brand.objects.all()  # Fetch all brands
    return render(request, 'adminside/product.html', {'products': products , 'brands': brands,'categories': categories})




@never_cache
@login_required(login_url='admin_login')
def add_products(request):
    categories = Categories.objects.filter(status='listed')
    brands = Brand.objects.filter(status='listed')
    product = Product.objects.all()

    if request.method == 'POST':
        # Retrieve product details from the form
        name = request.POST.get('name')
        description = request.POST.get('description')
        category_id = request.POST.get('category')
        brand_id = request.POST.get('brand')
       
        stock = request.POST.get('stock')
        video = request.FILES.get('video')  # Get the uploaded video file


        # Get category and brand objects
        category = get_object_or_404(Categories, id=category_id)
        brand = get_object_or_404(Brand, id=brand_id)

        # Create a new product instance
        new_item = Product(
            name=name,
            description=description,
            category=category,
            brand=brand,
            video=video,  # Assign the video to the product

            stock=stock,
        )
        new_item.save()

        # Loop through each additional cropped image
        for key in request.FILES:
            if key.startswith('additional_image_'):
                cropped_image = request.FILES[key]
                ProductImage.objects.create(product=new_item, image=cropped_image)
                print(f'Saved cropped image: {cropped_image.name}')

        return redirect('products')

    return render(request, 'adminside/product.html', {
        'categories': categories,
        'brands': brands,
        'product': product,
    })
    
@never_cache
@login_required(login_url='admin_login')
def edit_products(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    categories = Categories.objects.filter(status='listed')
    brands = Brand.objects.filter(status='listed')

    if request.method == 'POST':
        # Update product with the data from the form
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        category_id = request.POST.get('category')
        brand_id = request.POST.get('brand')
       
        stock = request.POST.get('stock')

        if category_id and brand_id:
            category = get_object_or_404(Categories, id=category_id)
            brand = get_object_or_404(Brand, id=brand_id)

            product.category = category
            product.brand = brand
         # Update the price
            product.stock = stock  # Update the stock
            # Update the product's video field

            video = request.FILES.get('video')  # Get the uploaded video file
            if video:
               product.video = video 
            # Handle multiple image uploads
            if request.FILES.getlist('edited_images[]'):
                for img in request.FILES.getlist('edited_images[]'):
                    ProductImage.objects.create(product=product, image=img)  # Create a new image instance

            product.save()
            return redirect('products')  # Redirect to the products list

    return render(request, 'adminside/edit_product.html', {
        'product': product,
        'categories': categories,
        'brands': brands,
    })
    
    
    
    
@never_cache   
@login_required(login_url='admin_login')   
def list_products(request):
    if request.method == 'POST':
        product_id = request.POST.get('id')  # Changed from brand_id to product_id
        new_status = request.POST.get('status')

        # Fetch the product using product_id
        product = get_object_or_404(Product, id=product_id)

        # Update the product's status
        product.status = new_status
        product.save()

        return redirect('products')  # Redirect to the products page

    # Handle GET request if needed
    products = Product.objects.all()  # Fetch all products to display in the template
    return render(request, 'adminside/list_products.html', {'products': products})

@never_cache
@login_required(login_url='admin_login')
def brand(request):
    # if request.user.is_authenticated:
    #   return redirect('brand')
    brand=Brand.objects.all().order_by('status')
    return render(request,'adminside/brand.html',{'brand':brand})
@never_cache
@login_required(login_url='admin_login')
@csrf_exempt
def add_brand(request):
    brand=Brand.objects.all().order_by('status')
    if request.method == 'POST':
        brand_name = request.POST.get('brand_name')
        country = request.POST.get('country')
        image = request.FILES.get('image')

        # Check if the brand already exists
        if Brand.objects.filter(brand_name=brand_name).exists():
            messages.error(request, 'Brand name already exists.')
            # Render the same template with the error
            return render(request, 'adminside/brand.html', {
                'brand':brand,
                'errors': {'brand_name''Brand name already exists.'},
                'brand_name': brand_name,
                'country': country,
                'modal_open': True,  # Flag to indicate the modal should be open
            })

        # Save the new brand
        brand = Brand(brand_name=brand_name, country=country, image=image)
        brand.save()

        messages.success(request, 'Brand added successfully.')
        return redirect('brand')  # Redirect to the brand list or desired page

    return render(request, 'adminside/brand.html', {'modal_open': False}) 

@never_cache
@login_required(login_url='admin_login')
# View to handle editing and cropping
def edit_brand(request, id):
    brand = get_object_or_404(Brand,id=id)
    
    
    if request.method == 'POST':
        brand.brand_name = request.POST['brand_name']
        brand.country = request.POST['country']
        print('fffffffff')
        if 'image' in request.FILES:
            image = request.FILES['image']
            brand.image = image
 
        brand.save()
        return redirect('brand')
     
    return render(request, 'adminside/brand.html', {'brand': brand})
@never_cache
@login_required(login_url='admin_login')
def list_brand(request):
      if request.method == 'POST':
        brand_id = request.POST.get('id')
        new_status = request.POST.get('status')

        try:
            brand = Brand.objects.get(id=brand_id)
            brand.status = new_status
            brand.save()
        except Brand.DoesNotExist:
            # Handle the error if the brand does not exist
            pass
        
        return redirect('brand')
      else:
        # Handle GET request if needed
        return redirect('brand')
@never_cache
@login_required(login_url='admin_login')
def toggle_status(request): 
    if request.method == 'POST':
        brand_id = request.POST.get('id')
        new_status = request.POST.get('status')

        try:
            brand = Brand.objects.get(id=brand_id)
            brand.status = new_status
            brand.save()

            return JsonResponse({'status': 'success'}, status=200)
        except Brand.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Brand not found.'}, status=404)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)
@never_cache
@login_required(login_url='admin_login')
def edtion(request):
    return render(request,'adminside/edition.html')
@never_cache
@login_required
def type1(request):
    type1 = Type1.objects.all().order_by('status')
    return render(request,'adminside/type1.html',{'type1':type1})
@never_cache
@login_required(login_url='admin_login')
def add_type(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        quantity = request.POST.get('Quantity')  # Use lowercase if needed
        image = request.FILES.get('image')
        
        print(f"Received - Name: {name}, Quantity: {quantity}, Image: {image}")
        
        # Save the new brand
        type1 = Type1(name=name, Quantity=quantity, image=image)
        type1.save()
        
        return redirect('type1')
@never_cache
@login_required(login_url='admin_login')
def edit_type(request, id):
    type1 = get_object_or_404(Type1, id=id)  # Retrieve the Type1 instance by ID
    
    if request.method == 'POST':
        # Update fields with data from the form
        type1.name = request.POST.get('name')
        type1.Quantity = request.POST.get('Quantity')  # Adjust as needed
        
        # Check if an image file is uploaded
        if 'image' in request.FILES:
            type1.image = request.FILES['image']  # Update the image field
        
        # Save the updated instance
        type1.save()
        
        return redirect('type1')  # Adjust this to your desired redirect view
    
    # If the method is not POST, render the edit form with the current instance data
    return render(request, 'adminside/type1.html', {'type1': type1})
@never_cache
@login_required(login_url='admin_login')  
def list_type(request):
    print('kkkkkk')
    if request.method == 'POST':
        type_id = request.POST.get('id')
        print(id,'llllllll')
        new_status = request.POST.get('status')
        print(f"Updating Type1 ID: {type_id} to status: {new_status}") 
        try:
            type1 = Type1.objects.get(id=type_id)
            type1.status = new_status
            type1.save()
            print(f"Type1 with ID {type_id} does not exist.")
        except Type1.DoesNotExist:
            # Handle the error if the type does not exist
            pass
        
        return redirect('type1')  # Adjust this to your actual redirect target
    else:
        # Handle GET request if needed
        return redirect('type1')
@never_cache
@login_required(login_url='admin_login')  
def Edition1(request):
    edition=Edition.objects.all().order_by('status')
    return render(request,'adminside/edition.html',{'edition':edition})
@never_cache
@login_required(login_url='admin_login')
def add_Edition(request):
    print('jjjj')
    if request.method == 'POST':
        edition_name = request.POST.get('name')
        description = request.POST.get('description')  # Use lowercase if needed
        image = request.FILES.get('image')
        print('hhhhhh')
        
        print(f"Received - Name: {edition_name}, Quantity: {description}, Image: {image}")
        
        # Save the new brand
        edition = Edition(edition_name=edition_name, description=description, image=image)
        edition.save()
        
        return redirect('Edition')
    
@never_cache
@login_required(login_url='admin_login')    
def edit_Edition(request, id):
    edition1 = get_object_or_404(Edition, id=id)  # Retrieve the Type1 instance by ID
    
    if request.method == 'POST':
        # Update fields with data from the form
        Edition.edition_name = request.POST.get('edition_name')
        Edition.description = request.POST.get('description')  # Adjust as needed
        
        # Check if an image file is uploaded
        if 'image' in request.FILES:
            Edition.image = request.FILES['image']  # Update the image field
        
        # Save the updated instance
        Edition.save()
        
        return redirect('Edition')  # Adjust this to your desired redirect view
    
    # If the method is not POST, render the edit form with the current instance data
    return render(request, 'adminside/edition.html', {'edition1': edition1})

@never_cache
@login_required(login_url='admin_login')    
def list_Edition(request):
    print('kkkkkk')
    if request.method == 'POST':
        Edition_id = request.POST.get('id')
        print(id,'llllllll')
        new_status = request.POST.get('status')
        print(f"Updating Type1 ID: {Edition_id} to status: {new_status}") 
        try:
            Edition1 = Edition.objects.get(id=Edition_id)
            Edition1.status = new_status
            Edition1.save()
            print(f"Type1 with ID {Edition_id} does not exist.")
        except Edition.DoesNotExist:
            # Handle the error if the type does not exist
            pass
        
        return redirect('Edition')  # Adjust this to your actual redirect target
    else:
        # Handle GET request if needed
        return redirect('Edition')
    
@never_cache
@login_required(login_url='admin_login')    
def add_category_view(request):
    brands = Brand.objects.filter(status='listed')
    types = Type1.objects.filter(status='listed')
    editions = Edition.objects.filter(status='listed')
    categories = Categories.objects.filter(status='listed')

    if request.method == 'POST':
        name = request.POST.get('name')
        brand_id = request.POST.get('brand')  # Get the brand ID as a string
        edition_id = request.POST.get('edition')  # Get the edition ID as a string
        type_id = request.POST.get('type1')  # Get the type ID as a string

        # Retrieve the actual Brand, Edition, and Type instances
        brand = get_object_or_404(Brand, id=brand_id)
        edition = get_object_or_404(Edition, id=edition_id)
        type_instance = get_object_or_404(Type1, id=type_id)

        # Create and save the category
        category = Categories(name=name, brand=brand, edition=edition, type1=type_instance)
        category.save()
        print('Saved:', category)

        return redirect('add_category_view') 
    
    return render(request, 'adminside/catogery.html', {
        'brands': brands,
        'types': types,
        'editions': editions,
        'categories': categories,  # Ensure categories are passed to the template
    })
    # Redirect to the category view after saving
    # Redirect to the category view after saving
# def list_catogery(request, pk):
#     category = get_object_or_404(Categories, pk=pk)
    
#     # Toggle the status
#     category.status = 'listed' if category.status == 'unlisted' else 'unlisted'
#     category.save()
    
#     # Redirect back to the same category's detail view
#     return redirect('list_catogery', pk=category.pk)


@never_cache
@login_required(login_url='admin_login')
def list_catogery(request):
    print('kkkkkk')
    if request.method == 'POST':
        Edition_id = request.POST.get('id')
         
        new_status = request.POST.get('status')
        print(f"Updating Type1 ID: {Edition_id} to status: {new_status}") 
        try:
            Edition1 = Categories.objects.get(id=Edition_id)
            Edition1.status = new_status
            Edition1.save()
            print(f"Type1 with ID {Edition_id} does not exist.")
        except Edition.DoesNotExist:
            # Handle the error if the type does not exist
            pass
        
        return redirect('add_category_view')  # Adjust this to your actual redirect target
    else:
        # Handle GET request if needed
        return redirect('add_category_view')

# def varients(request):
#     return render(request,'adminside/varients.html')
@never_cache
@login_required(login_url='admin_login')

def varients(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    variants = Variants.objects.filter(product=product)
    print('varient:',variants)

    if request.method == 'POST':
        try:
            # Prepare to collect variant data
            colour = request.POST.get('colour')
            size = request.POST.get('size')
            type1 = request.POST.get('type1')
            stock = int(request.POST.get('stock'))
            price = float(request.POST.get('price'))

            # Check for duplicates
            if Variants.objects.filter(
                colour=colour,
                size=size,
                type1=type1,
                product=product
            ).exists():
                return HttpResponseBadRequest("Variant with the same attributes already exists.")

            # Create the variant
            variant = Variants.objects.create(
                product=product,
                colour=colour,
                size=size,
                type1=type1,
                stock=stock,
                price=price,
             )

            # Save each of the images associated with the variant
            for i in range(1, 5):  # Assuming you want to support 4 images
                image = request.FILES.get(f'image{i}')
                if image:  # Check if the image exists
                    VariantImage.objects.create(variant=variant, image=image)

            return redirect('varients', product_id=product_id)

        except Exception as e:
            return HttpResponseBadRequest(f"An error occurred: {str(e)}")

    context = {
        'product': product,
        'variants': variants
    }
    return render(request, 'adminside/varients.html', context)

@never_cache
@login_required(login_url='admin_login')
def index(request):
    cars = SportsCar.objects.all()
    if request.method == 'POST':
        car_name = request.POST.get('name')
        car_brand = request.POST.get('brand')
        car_year = request.POST.get('year')
        if car_name and car_brand and car_year:
            SportsCar.objects.create(name=car_name, brand=car_brand, year=car_year)
            return redirect('index')  # Redirect to the same page
    return render(request, 'index.html', {'cars': cars})




@never_cache
@login_required(login_url='admin_login')
def product_variants_view(request, product_id):
    order_id = request.session.get('order_id', None)  # Default to None if not found

    product = get_object_or_404(Product, id=product_id)
    variants = product.variants.filter(id__isnull=False)  
    print('iiii',variants)
    for variant in variants:
        print('Variant ID:', variant.id)
    order_items = OrderItem.objects.prefetch_related(
        Prefetch('variants', queryset=Variants.objects.prefetch_related('images'))
    ).filter(order_id=order_id)
    # variants = product.variants.all()
    
    context = {
        'product': product,
        'variants': variants,
        'order_items': order_items,
    }
    
    return render(request, 'adminside/varients.html', context)
@never_cache
@login_required(login_url='admin_login')
def add_variant_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        # Capture the fields
        colour = request.POST.get('colour')
        size = request.POST.get('size')
        type1 = request.POST.get('type1')
        stock = int(request.POST.get('stock'))
        price = float(request.POST.get('price'))

        # Check if the variant already exists
        if Variants.objects.filter(product=product, colour=colour, size=size, type1=type1).exists():
            messages.error(request, 'This variant already exists for the product.')
            return render(request, 'adminside/varients.html', {'product': product})

        # Create the variant instance
        variant = Variants.objects.create(
            product=product,
            colour=colour,
            size=size,
            type1=type1,
            stock=stock,
            price=price,
 
        )

        # Handle the uploaded images
        for key in request.FILES:
            if key.startswith('additional_image_'):
                image = request.FILES[key]
                VariantImage.objects.create(variant=variant, image=image)

        messages.success(request, 'Variant added successfully.')
        return redirect('variants', product_id=product.id)  # Redirect to the variants page

    return render(request, 'adminside/varients.html', {'product': product})

@never_cache
@login_required(login_url='admin_login')
def edit_variant(request, product_id, variant_id):
    product = get_object_or_404(Product, id=product_id)
    variant = get_object_or_404(Variants, id=variant_id)

    if request.method == 'POST':
        # Update the variant with the new data
        variant.colour = request.POST.get('colour')
        variant.size = request.POST.get('size')
        variant.type1 = request.POST.get('type1')
        variant.stock = int(request.POST.get('stock'))
        variant.price = float(request.POST.get('price'))


    
        variant.save()  # Save the variant first

        # Handle image uploads if provided
        for i in range(1, 5):  # Assuming you want to support 4 images
            if f'image{i}' in request.FILES:
                image = request.FILES[f'image{i}']
                VariantImage.objects.create(variant=variant, image=image)

        return redirect('variants', product_id=variant.product.id)

    # For GET request, render the edit form with existing variant data
    context = {
         'product': product,
        'variant': variant,
    }
    return render(request, 'adminside/varients.html', context)
@never_cache
@login_required(login_url='admin_login')
def toggle_listing(request, variant_id):
    variant = get_object_or_404(Variants, id=variant_id)
    
    # Toggle the status
    if variant.status == 'listed':
        variant.status = 'unlisted'
    else:
        variant.status = 'listed'
    
    variant.save()
    product_id = variant.product.id 
    
    return redirect('variants',product_id=product_id) 


@never_cache
@login_required(login_url='admin_login')
def question(request):
    print('hi')
    questions = ProductQuestion.objects.all().order_by('-status')
    question_to_answer = None

    if request.method == 'POST':
        print('hloo')
        action = request.POST.get('action')
        question_id = request.POST.get('question_id')

        if action == 'answer' and question_id:
            question_to_answer = get_object_or_404(ProductQuestion, id=question_id)

        elif action == 'submit_answer':
            answer = request.POST.get('answer')
            question = get_object_or_404(ProductQuestion, id=question_id)
            question.answer = answer  # Store the answer in the database
            question.status = 'answered'
            question.save()
            question_text = question.question
            send_answer_email(question.email, answer,question_text)  # Send an email notification
            return redirect('question')

        elif action == 'send_privately':
            answer = request.POST.get('answer')
            question = get_object_or_404(ProductQuestion, id=question_id)
            question.status = 'answered'
            question.answered_privately = True
            question.save()
            question_text = question.question
            send_answer_email(question.email, answer,question_text)  # Send an email notification
            return redirect('question')

    return render(request, 'adminside/questions.html', {
        'questions': questions,
        'question_to_answer': question_to_answer
    })
    
def send_answer_email(to_email, answer,question_text):
    subject = 'Your Question Answered'
    # Render the email HTML template with the answer context
    context = {
        'answer': answer,
        'question': question_text
    }
    html_message = render_to_string('email_templates/answer_notification.html',context)
    plain_message = strip_tags(html_message)  # Fallback plain-text version
    from_email = settings.DEFAULT_FROM_EMAIL

    send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)
    
    
@never_cache
@login_required(login_url='admin_login')
@csrf_exempt
def submit_question(request):
    if request.method == 'POST':
        question_text = request.POST.get('question')
        email = request.POST.get('email')  # Retrieve email from request
        product_id = request.POST.get('product_id')  # Retrieve product_id from request

        if question_text and email and product_id:
            try:
                # Save the question to the ProductQuestion model
                new_question = ProductQuestion.objects.create(
                    question=question_text,
                    email=email,
                    product_id=product_id  # Set the product_id
                )
                return JsonResponse({'message': 'Question submitted successfully!'}, status=200)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        else:
            # Check for missing fields and provide a specific error message
            missing_fields = []
            if not question_text:
                missing_fields.append('question')
            if not email:
                missing_fields.append('email')
            if not product_id:
                missing_fields.append('product_id')
            error_message = f"{' and '.join(missing_fields).capitalize()} cannot be empty."
            return JsonResponse({'error': error_message}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)



   # Adjust import according to your structure
@never_cache
@login_required(login_url='admin_login')
@csrf_exempt
def update_order_item_status(request):
    order_items = OrderItem.objects.all()

    for item in order_items:
        current_status = item.status
        
        # Determine allowed statuses based on the current status
        if current_status == "Order Pending":
            item.allowed_statuses = ["Order Confirmed", "Cancelled"]
        elif current_status == "Order Confirmed":
            item.allowed_statuses = ["Shipped", "Cancelled"]
        elif current_status == "Shipped":
            item.allowed_statuses = ["Out For Delivery", "Cancelled"]
        elif current_status == "Out For Delivery":
            item.allowed_statuses = ["Delivered", "Cancelled"]
        elif current_status == "Delivered":
            item.allowed_statuses = ["Requested Return"]
        elif current_status == "Cancelled":
            item.allowed_statuses = []  # No further actions allowed
        elif current_status == "Requested Return":
            item.allowed_statuses = ["Approve Returned", "Reject Returned"]
        elif current_status == "Approve Returned":
            item.allowed_statuses = []  # No further actions allowed
        elif current_status == "Reject Returned":
            item.allowed_statuses = []  # No further actions allowed
        else:
            item.allowed_statuses = []  # Default case

    return render(request, 'adminside/order.html', {
        'order_items': order_items,
    })
@never_cache
@login_required(login_url='admin_login')
def update_status(request, orderitem_id):
    # Get the OrderItem object by its ID
    order_item = get_object_or_404(OrderItem, orderitem_id=orderitem_id)
    status = request.POST.get('status')  # Retrieve the status from the POST request

    # Update the status if it's a valid choice
    valid_statuses = [choice[0] for choice in OrderItem.STATUS_CHOICES]
    if status in valid_statuses:
        order_item.status = status
        order_item.save()
        messages.success(request, f"Order status updated to '{status}'.")
    else:
        messages.error(request, "Invalid status selected.")

    # Redirect back to the main order management page
    return redirect('update_order_item_status')
