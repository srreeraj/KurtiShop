from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Category
from .forms import CategoryForm
# Create your views here.

def get_category_context():
    return {
        'categories': Category.objects.filter(is_deleted=False).select_related('parent').order_by('name')
    }

@login_required
@user_passes_test(lambda u : u.is_staff)
def category_list(request):
    categories = get_category_context()
    context = {
        'categories' : categories,
        'page_title' : 'Categories'
    }
    return render(request, 'dashboard/categories/list.html', context)


@login_required
@user_passes_test(lambda u : u.is_staff)
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully')
            return redirect('categories:category_list')
    else:
        form = CategoryForm()
    context = get_category_context()
    context.update({
        'form' : form,
        'page_title' : 'Create Category'
    })
    return render(request, 'dashboard/categories/list.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk, is_deleted=False)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('categories:category_list')
    else:
        form = CategoryForm(instance=category)

    context.update({
        'form': form,
        'category': category,
        'page_title': 'Edit Category'
    })
    return render(request, 'dashboard/categories/list.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk, is_deleted=False)
    category.is_deleted = True
    category.save()
    messages.success(request, 'Category deleted successfully!')
    return redirect('categories:category_list')

