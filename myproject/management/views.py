from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from .models import Categories,Brand,Type1,Edition,Product,Variants
from django.shortcuts import render, redirect, get_object_or_404
import logging
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import SportsCar
from django.views.decorators.cache import never_cache
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
    products = Product.objects.all()
    categories = Categories.objects.all() # Fetch all products
    brands = Brand.objects.all()  # Fetch all brands
    return render(request, 'adminside/product.html', {'products': products, 'brands': brands,'categories': categories})
@never_cache
@login_required(login_url='admin_login')
def add_products(request):
    categories = Categories.objects.filter(status='listed')
    brands = Brand.objects.filter(status='listed')
    variants = Variants.objects.all()  # Fetch variants if needed

    if request.method == 'POST':
        print('hii')
        name = request.POST.get('name')
        description = request.POST.get('description')
        category_id = request.POST.get('category')
        brand_id = request.POST.get('brand')
        price = request.POST.get('price')  # Get price from the form
        stock = request.POST.get('stock')  # Get stock from the form
        image = request.FILES.get('main_image')  # Get image from the form

        
        category = get_object_or_404(Categories, id=category_id)
        brand = get_object_or_404(Brand, id=brand_id)

            # Create a new product instance
        new_item = Product(
                name=name,
                description=description,
                category=category,
                brand=brand,
                price=price,
                stock=stock,
                image=image  # Save the image
            )
        new_item.save()
        return redirect('products')

    return render(request, 'adminside/product.html', {
        'categories': categories,
        'brands': brands,
        'variants': variants  # Pass variants to the template if needed
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
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        
        if request.FILES.get('main_image'):
            product.image = request.FILES.get('main_image')  # Update the image if provided
        
        if category_id and brand_id:
            category = get_object_or_404(Categories, id=category_id)
            brand = get_object_or_404(Brand, id=brand_id)

            product.category = category
            product.brand = brand
            product.price = price  # Update the price
            product.stock = stock  # Update the stock
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
    if request.user.is_authenticated:
      return redirect('users')
    brand=Brand.objects.all().order_by('status')
    return render(request,'adminside/brand.html',{'brand':brand})
@never_cache
@login_required(login_url='admin_login')
@csrf_exempt
def add_brand(request):
    if request.method == 'POST':
        brand_name = request.POST['brand_name']
        country = request.POST['country']
        image = request.FILES['image']
         
        
        # Save the new brand
        brand = Brand(brand_name=brand_name, country=country, image=image)
        brand.save()
        
        return redirect('brand')

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

    if request.method == 'POST':
        try:
            # Prepare to collect variant data
            variant_data = []
            for i in range(len(request.POST.getlist('colour'))):  # Iterate over the number of variants submitted
                colour = request.POST.getlist('colour')[i]
                size = request.POST.getlist('size')[i]
                type1 = request.POST.getlist('type1')[i]
                stock = int(request.POST.getlist('stock')[i])
                price = float(request.POST.getlist('price')[i])

                # Handle the images (if required, can use a list for multiple images)
                image1 = request.FILES.getlist('image1')[i] if request.FILES.getlist('image1') else None
                image2 = request.FILES.getlist('image2')[i] if request.FILES.getlist('image2') else None

                # Check for duplicates
                if Variants.objects.filter(
                    colour=colour,
                    size=size,
                    type1=type1,
                    products=product
                ).exists():
                    return HttpResponseBadRequest(f"Variant with Colour: {colour}, Size: {size}, Type: {type1} already exists.")

                # Save variant data for this entry
                variant_data.append({
                    'colour': colour,
                    'size': size,
                    'type1': type1,
                    'stock': stock,
                    'price': price,
                    'image1': image1,
                    'image2': image2,
                })

            # Now save all variants
            for data in variant_data:
                variant = Variants(
                    colour=data['colour'],
                    size=data['size'],
                    type1=data['type1'],
                    stock=data['stock'],
                    price=data['price'],
                    image1=data['image1'],
                    image2=data['image2'],
                )
                variant.save()
                variant.products.add(product)  # Associate the variant with the product

            return redirect('varients', product_id=product_id)  # Redirect after saving

        except Exception as e:
            return HttpResponseBadRequest(f"An error occurred: {str(e)}")

    # Load existing variants for the specific product
    variants = Variants.objects.filter(products__id=product_id)

    return render(request, 'adminside/varients.html', {'product': product, 'variants': variants})



# def viewvarients(request,id):
#    print('hii')
#    product = get_object_or_404(Product, id=id)
#    variants = Variants.objects.filter(products=product)
#    print('varient ind  too  :',variants)
#    context = {
#         'product': product, 
#         'variants': variants}
#    return render(request,'adminside/view varient.html',context)




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
    product = get_object_or_404(Product, id=product_id)
    variants = product.variants.all()
    
    context = {
        'product': product,
        'variants': variants,
    }
    
    return render(request, 'adminside/varients.html', context)
@never_cache
@login_required(login_url='admin_login')
def add_variant_view(request, product_id):
    if request.method == 'POST':
        # Capture the fields
        colour = request.POST.getlist('colour')  # Assuming this is a list of colors
        size = request.POST.getlist('size')      # Assuming this is a list of sizes
        type1 = request.POST.getlist('type1')    # Assuming this is a list of types
        stock = request.POST.getlist('stock')     # Assuming this is a list of stock quantities
        price = request.POST.getlist('price')     # Assuming this is a list of prices
        # Capture image fields
        image1 = request.FILES.get('image1')
        image2 = request.FILES.get('image2')
        image3 = request.FILES.get('image3')
        image4 = request.FILES.get('image4')

        # Create the variant instance
        variant = Variants.objects.create(
            colour=colour,  # This will be a JSON array
            size=size,      # This will be a JSON array
            type1=type1,    # This will be a JSON array
            stock=stock,    # This will be a JSON array
            price=price,    # This will be a JSON array
            image1=image1,
            image2=image2,
            image3=image3,
            image4=image4,
        )

        # Associate the variant with the product
        product = get_object_or_404(Product, id=product_id)
        variant.products.add(product)

        return redirect('variants', product_id=product.id)

    # Handle GET request
    return render(request, 'adminside/varients.html')
@never_cache
@login_required(login_url='admin_login')
def edit_variant(request, id):
    print('hiii',id)
    variant = get_object_or_404(Variants, id=id)

    if request.method == 'POST':
        # Update the variant with the new data
        variant.colour = request.POST.get('colour')
        variant.size = request.POST.get('size')
        variant.type1 = request.POST.get('type1')
        variant.stock = request.POST.get('stock')
        variant.price = request.POST.get('price')

        # Handle image uploads if provided
        if 'image1' in request.FILES:
            variant.image1 = request.FILES['image1']
        if 'image2' in request.FILES:
            variant.image2 = request.FILES['image2']
        if 'image3' in request.FILES:
            variant.image3 = request.FILES['image3']
        if 'image4' in request.FILES:
            variant.image4 = request.FILES['image4']

        variant.save()
        return redirect('variants')  # Redirect to the variant list or another page

    # For GET request, render the edit form with existing variant data
    context = {
        'variant': variant
    }
    return render(request, 'adminside/varients.html', context)