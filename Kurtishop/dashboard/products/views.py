from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q

from products.models import Product, ProductVariant, ProductImage
from .forms import ProductForm, ProductVariantForm, ProductImageForm


@login_required
@user_passes_test(lambda u: u.is_staff)
def product_list(request):
    search = request.GET.get('search', '')
    category_slug = request.GET.get('category')
    
    qs = Product.objects.filter(is_deleted=False).select_related('category')
    
    if search:
        qs = qs.filter(
            Q(name__icontains=search) | 
            Q(sku__icontains=search) |
            Q(category__name__icontains=search)
        )
    if category_slug:
        qs = qs.filter(category__slug=category_slug)

    paginator = Paginator(qs.order_by('-created_at'), 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'products': page_obj,
        'page_obj': page_obj,
        'page_title': 'Products',
        'categories': Category.objects.filter(is_deleted=False),
    }
    return render(request, 'dashboard/products/list.html', context)