from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from .models import Categories,Brand 



def users(request):
    all_users = User.objects.order_by('-is_active', 'last_login')
    return render(request, 'adminside/users.html', {'users': all_users})

def block_user(request, user_id):
    User = get_user_model()


    if request.method == 'POST':
        
        user = get_object_or_404(User, id=user_id)
        user.is_active = not user.is_active
        user.save()
        return JsonResponse({'is_active': user.is_active})
    return JsonResponse({'error': 'Invalid request'}, status=400)

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
    
def catogery(request):
    categories = Categories.objects.all().order_by('-status')

    return render(request,'adminside/catogery.html',{'categories': categories})
 
def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        brand = request.POST.get('brand')
        edition = request.POST.get('edition')
       
        print(f"Received: name={name}, brand={brand}, edition={edition} ")  # Debugging

        category = Categories(name=name, brand=brand, edition=edition,  )
        category.save()
        print('saved',category)
        
        return redirect('catogery')  # Redirect back to the category view after saving

    return redirect('catogery') 


def edit_category(request, pk):
    category = get_object_or_404(Categories, pk=pk)

    if request.method == 'POST':
        try:
            # Update the category with the new data from the request
            Categories.name = request.POST.get('name')
            Categories.brand = request.POST.get('brand')
            Categories.edition = request.POST.get('edition')
          
            category.save()

            # Return the updated data as a JSON response
            return JsonResponse({
                'status': 'success',
                'message': 'Category updated successfully!',
                'name': Categories.name,
                'brand': Categories.brand,
                'edition': Categories.edition,
               
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@csrf_exempt  # Use this if you're handling CSRF tokens manually
def delete_category(request, pk):
    if request.method == 'POST':
        category = get_object_or_404(Categories, pk=pk)
        category.delete()
        return JsonResponse({'status': 'deleted'})
    return JsonResponse({'error': 'Invalid request'}, status=400)

def list_category(request, pk):
    category = get_object_or_404(Categories, pk=pk)
    category.status = 'listed'  # Set to 'listed'
    category.save()
    return JsonResponse({'status': 'listed'})

def delist_category(request, pk):
    category = get_object_or_404(Categories, pk=pk)
    category.status = 'delisted'  # Set to 'delisted'
    category.save()
    return JsonResponse({'status': 'delisted'})

def toggle_category_status(request, pk):
    category = get_object_or_404(Categories, pk=pk)
    category.status = 'delisted' if Categories.status == 'listed' else 'listed'
    category.save()
    return JsonResponse({'status': Categories.status})

def get_suggestions(request):
    query = request.GET.get('query', '')
    field = request.GET.get('field', '')

    if field not in ['name', 'brand', 'edition' ]:
        return JsonResponse([], safe=False)

    suggestions = Categories.objects.filter(**{f"{field}__icontains": query}).values_list(field, flat=True).distinct()
    return JsonResponse(list(suggestions), safe=False)
 

def products(request):
    return render(request,'adminside/product.html')
def brand(request):
    brand=Brand.objects.all().order_by('status')
    return render(request,'adminside/brand.html',{'brand':brand})


@csrf_exempt
def add_Brand(request):
    print('hhhhh')
    if request.method == 'POST':
        name = request.POST.get('brand_name')
        country = request.POST.get('country')
        image = request.FILES.get('image') 
        status = 'listed '  # Default status
        print(name)
        print(country)
        brands = Brand(brand_name=name, status='listed'  , country=country, image=image, active=True)
        brands.save()
        print('reached',brands)
        return JsonResponse({'status': 'success'}, status=200)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)

def update_brand(request):
    if request.method == 'POST':
        brand_id = request.POST.get('id')
        brand_name = request.POST.get('brand_name')
        country = request.POST.get('country')
        print('hiiiii')

        try:
            brand = Brand.objects.get(id=brand_id)
            brand.brand_name = brand_name
            brand.country = country
            print('hlooooooo')
            
            # If an image is uploaded, update it
            if request.FILES.get('image'):
                brand.image = request.FILES.get('image')

            brand.save()
            return JsonResponse({'status': 'success'}, status=200)
        except Brand.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Brand not found.'}, status=404)
                 
                 #list and dislist

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
def edtion(request):
    return render(request,'adminside/edition.html')
def type1(request):
    return render(request,'adminside/type1.html')
def varients(request):
    return render(request,'adminside/varients.html')
