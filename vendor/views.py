from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import user_passes_test, login_required
from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from accounts.views import validate_vendor
from menu.models import Category, FoodItem
from .models import OpeningHours, Vendor
from .forms import VendorForm, OpeningHoursForm
from django.contrib import messages
from django.shortcuts import get_object_or_404
from menu.forms import CategoryForm, FoodItemForm
from .utils import get_vendor
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.template.defaultfilters import slugify
from django.middleware.csrf import get_token
# Create your views here.


@login_required(login_url='login')
@user_passes_test(validate_vendor)
def vendor_profile(request):
    vendor = get_object_or_404(Vendor, user=request.user)
    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)
        user_profile_form = UserProfileForm(
            request.POST, request.FILES, instance=profile)

        if vendor_form.is_valid() and user_profile_form.is_valid():
            vendor_form.save()
            user_profile_form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('vendor_profile')
        else:
            print(vendor_form.errors)
            print(user_profile_form.errors)

            context = {
                'vendor_form': vendor_form,
                'user_profile_form': user_profile_form,
                'profile': profile,
                'vendor': vendor,
            }

            return render(request, 'vendor/vendor_profile.html', context)
    else:
        vendor_form = VendorForm(instance=vendor)
        user_profile_form = UserProfileForm(instance=profile)
        context = {
            'vendor_form': vendor_form,
            'user_profile_form': user_profile_form,
            'profile': profile,
            'vendor': vendor,
        }
        return render(request, 'vendor/vendor_profile.html', context)

@login_required(login_url='login')
@user_passes_test(validate_vendor)
def menu_builder(request):
    vendor = get_vendor(request)
    categories = Category.objects.filter(vendor=vendor).order_by('created_at')
    context = {
        'categories': categories,
    }
    return render(request, 'vendor/menu_builder.html', context)


@login_required(login_url='login')
@user_passes_test(validate_vendor)
def fooditems_by_category(request, pk=None):
    vendor = get_vendor(request)
    category = get_object_or_404(Category, pk=pk)
    fooditems = FoodItem.objects.filter(vendor=vendor, category=category).order_by('created_at')
    context = {
        'fooditems': fooditems,
        'category': category,
    }
    return render(request, 'vendor/fooditems_by_category.html', context)


@login_required(login_url='login')
@user_passes_test(validate_vendor)
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            category.slug = slugify(category_name) + str(request.user.id)
            try:
                category.save()
            except IntegrityError:
                messages.info(request, 'A similar Category already exists')
            else:
                messages.success(request, f'Category - \"{category_name.upper()}\" added successfully')
            return redirect('menu_builder')
        else:
            for field in form:
                for error in field.errors:
                    print(error)
                    messages.error(request, error)
    else:
        form = CategoryForm()
    context = {
        'form': form,
    }
    return render(request, 'vendor/add_category.html', context)


@login_required(login_url='login')
@user_passes_test(validate_vendor)
def delete_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, 'Category deleted successfully')
    return redirect('menu_builder')


@login_required(login_url='login')
@user_passes_test(validate_vendor)
def edit_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    if category.vendor != get_vendor(request):
        messages.error(request, 'You are not allowed to edit this category')
        return redirect('menu_builder')
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.slug = slugify(category_name)
            try:
                category.save()
            except IntegrityError:
                messages.info(request, 'A Similar Category already exists')
                return redirect('edit_category', category.pk)
            else:
                messages.success(request, 'Category updated successfully')
            return redirect('menu_builder')
        else:
            for field in form:
                for error in field.errors:
                    print(error)
                    messages.error(request, error)
    else:
        form = CategoryForm(instance=category)
    context = {
        'form': form,
        'category': category,
    }
    return render(request, 'vendor/edit_category.html', context)


@login_required(login_url='login')
@user_passes_test(validate_vendor)
def add_food(request):
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            food_title = form.cleaned_data['food_title']
            food = form.save(commit=False)
            food.vendor = get_vendor(request)
            food.slug = slugify(food.food_title)
            try:
                food.save()
            except IntegrityError:
                messages.info(request, 'A similar food item already exists')
                food_category = form.cleaned_data['category']
                return redirect('fooditems_by_category', food_category.pk)
            else:
                messages.success(request, 'Food Item added successfully')
            return redirect('fooditems_by_category', food.category.pk)
 
    else:
        form = FoodItemForm()
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
    context = {
        'form': form,
    }
    return render(request, 'vendor/add_food.html', context)


@login_required(login_url='login')
@user_passes_test(validate_vendor)
def edit_food(request, pk=None):
    food = get_object_or_404(FoodItem, pk=pk)
    if food.vendor != get_vendor(request):
        messages.error(request, 'You are not allowed to edit this food item')
        return redirect('menu_builder')
    
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES, instance=food)
        if form.is_valid():
            food_title = form.cleaned_data['food_title']
            food = form.save(commit=False)
            food.slug = slugify(food_title)
            try:
                food.save()
            except IntegrityError:
                messages.info(request, 'A similar food item already exists')
                return redirect('edit_food', food.pk)
            else:
                messages.success(request, 'Food Item updated successfully')
            return redirect('fooditems_by_category', food.category.pk)
        else:
            for field in form:
                for error in field.errors:
                    print(error)
                    messages.error(request, error)
    else:
        form = FoodItemForm(instance=food)
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
    context = {
        'form': form,
        'food': food,
    }
    return render(request, 'vendor/edit_food.html', context)


@login_required(login_url='login')
@user_passes_test(validate_vendor)
def delete_food(request, pk=None):
    food = get_object_or_404(FoodItem, pk=pk)
    if food.vendor != get_vendor(request):
        messages.error(request, 'You are not allowed to delete this food item')
        return redirect('menu_builder')
    
    pk = food.category.pk
    food.delete()
    messages.success(request, 'Food Item deleted successfully')
    return redirect('fooditems_by_category', pk)

@login_required(login_url='login')
@user_passes_test(validate_vendor)
def opening_hours(request):
    vendor = get_vendor(request)
    form = OpeningHoursForm()
    opening_hours = OpeningHours.objects.filter(vendor=vendor).order_by('day', 'open')
    context = {
        'opening_hours': opening_hours,
        'form': form,
    }
    return render(request, 'vendor/opening_hours.html', context)


def add_opening_hours(request):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
            day = request.POST['day']
            open = request.POST['open']
            close = request.POST['close']
            is_closed = request.POST['is_closed']

            if is_closed == 'true':
                is_closed = True
            else:
                is_closed = False
            try:
                obj = OpeningHours.objects.create(vendor=get_vendor(request), day=day, open=open, close=close, is_closed=is_closed)
            except ValidationError as e:
                for error in e:
                    if '500' in error[1]:
                        return JsonResponse({'status': 'Failed', 'message': 'Restaurant must Open before Closing', 'code': 500})
                    elif '501' in error[1]:
                        return JsonResponse({'status': 'Failed', 'message': 'There is an overlap in the Opening Time for this day', 'code': 501})
                    elif '502' in error[1]:
                        return JsonResponse({'status': 'Failed', 'message': 'There is an overlap in the Closing Time for this day', 'code': 502})
                    elif '503' in error[1]:
                        return JsonResponse({'status': 'Failed', 'message': 'There is a subset of the Open Period for this day', 'code': 503})
                    elif '504' in error[1]:
                        return JsonResponse({'status': 'Failed', 'message': 'The Restaurant is closed on this day', 'code': 504})
                    elif '499' in error[1]:
                        return JsonResponse({'status': 'Failed', 'message': 'There exist Open Slab(s) for the day', 'code': 499})
                    elif '498' in error[1]:
                        return JsonResponse({'status': 'Failed', 'message': 'The Restaurant is already closed on this day', 'code': 498})
                    else:
                        print(error)
                        return JsonResponse({'status': 'Failed', 'message': 'Unknown Error', 'code': 410})

            except IntegrityError as i:
                return JsonResponse({'status': 'Failed', 'message': 'Similar entry exists', 'code': 402})
            else:
                # Only Success
                return JsonResponse({'status': 'Success', 'message': 'New opening hours added', 'code': 200, 'new_id': obj.id, 'csrf': get_token(request)})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid Request', 'code': 408})
    else:
        return JsonResponse({'status': 'Failed', 'message': 'Please Login to Your Account', 'code': 400})


def remove_opening_hours(request, pk):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'DELETE':
            try:
                OpeningHours.objects.get(pk=pk).delete()
            except ObjectDoesNotExist:
                return JsonResponse({'status': 'Failed', 'message': 'Opening Hours does not exist', 'code': 404})
            else:
                # Only Success
                return JsonResponse({'status': 'Success', 'message': 'Opening Hours removed', 'code': 200, 'new_id': pk})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid Request', 'code': 408})
    else:
        return JsonResponse({'status': 'Failed', 'message': 'Please Login to Your Account', 'code': 400})