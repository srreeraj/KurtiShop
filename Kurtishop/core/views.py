from django.shortcuts import render
from products.models import Product, ProductVariant
from categories.models import Category
from django.db.models import Count, Q

# Create your views here.

def home(request):

    categories = Category.objects.filter(
        is_active = True,
        is_deleted = False,
    ).annotate(
        product_count=Count('products', filter=Q(products__is_active=True, products__is_deleted=False))
    ).order_by('name')[:12]

    featured_products = Product.objects.filter(
        is_featured = True,
        is_active = True,
        is_deleted = False,
    ).select_related('category')[:8]

    new_arrivals = Product.objects.filter(
        is_new_arrival = True,
        is_active =True,
        is_deleted = False,
    ).select_related('category')[:8]

    context = {
        'categories' : categories,
        'featured_products' : featured_products,
        'new_arrivals' : new_arrivals
    }
    return render(request, 'core/home.html', context)

def search(request):
    query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category')

    variants = ProductVariant.objects.filter(
        product__is_active=True,
        product__is_deleted=False,
        is_active=True,
        is_deleted=False,
        stock__gt=0
    ).select_related('product', 'product__category', 'color')

    if query:
        variants = products.filter(
            Q(product__name__icontains=query) |
            Q(product__description__icontains=query) |
            Q(color__name__icontains=query)
        )

    if category_slug:
        variants = variants.filter(product__category__slug=category_slug)

    # Remove duplicate products (show one variant per product)
    seen = {}
    unique_products = []
    for v in variants:
        if v.product_id not in seen:
            seen.add(v.product_id)
            product = v.product
            product.primary_image = v.product.images.first()
            product.color = v.color                     # Attach color for card
            product.display_price = v.price             # Attach price
            product.discount_percentage = v.discount_percentage
            products.append(product)

    categories = Category.objects.filter(
        is_active=True,
        is_deleted=False
    ).annotate(
        product_count=Count('products', filter=Q(products__is_active=True))
    )

    context = {
        'query': query,
        'products': unique_products[:48],   # limit results
        'categories': categories,
        'selected_category': category_slug,
    }

    return render(request, 'core/search.html', context)