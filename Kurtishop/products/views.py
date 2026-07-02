from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q
from .models import Product,Category, Color, Size, Sleeve, Neck, Occasion, Pattern

# Create your views here.

def product_list(request):
    products = Product.objects.filter(
        is_active=True,
        is_deleted=False
    ).select_related('category','sleeve','neck','occasion','pattern').prefetch_related('images','variants')

    # Category filter
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)

    # Price filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(variants__price__gte=min_price)
    if max_price:
        products = products.filter(variants__price__lte=max_price)

    # Color filter
    color_id = request.GET.get('color')
    if color_id:
        products = products.filter(variants__color_id=color_id)
    
    # Size filter
    size_id = request.GET.get('size')
    if size_id:
        products = products.filter(variants__size_id=size_id)

    # Sleeve filter
    sleeve_id = request.GET.get('sleeve')
    if sleeve_id:
        products = products.filter(variants__sleeve_id=sleeve_id)

    # Neck filter
    neck_id = request.GET.get('neck')
    if neck_id:
        products = products.filter(variants__neck_id=neck_id)

    # Occasion filter
    occasion_id = request.GET.get('occasion')
    if occasion_id:
        products = products.filter(variants__occasion_id=occasion_id)

    # Pattern filter
    pattern_id = request.GET.get('pattern')
    if pattern_id:
        products = products.filter(variants__pattern_id=pattern_id)
    
    # Remove duplicate products
    products = products.distinct()


    # Pagination

    from django.core.paginator import Paginator
    paginator = Paginator(products, 12) #12 products per page
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)

    # ====================SIDEBAR DATA===========================================

    # Categories with count
    categories = Category.objects.filter(
        is_active=True,
        is_deleted=False,
    ).annotate(
        product_count=Count('products',filter=Q(products__is_active=True))
    )

    # Colors with count
    colors = Color.objects.annotate(
        product_count=Count('productvariant', filter=Q(productvariant__product__is_active=True))
    )

    # Size with count
    sizes = Size.objects.annotate(
        product_count=Count('productvariant',filter=Q(productvariant__product__is_active=True))
    )

    # Other lookup fields
    sleeves = Sleeve.objects.all()
    necks = Neck.objects.all()
    occasions = Occasion.objects.all()
    patterns = Pattern.objects.all()


    context = {
        'products': products_page,
        'categories' : categories,
        'colors' : colors,
        'sizes' : sizes,
        'sleeves' : sleeves,
        'necks' : necks,
        'occasions' : occasions,
        'patterns' : patterns,

        # For active filter highlighting
        'acitve_category' : Category.objects.filter(slug=category_slug).first() if category_slug else None,
    }

    return render(
        request,
        'products/product_list.html',
        context
    )

def product_detail(request,slug):
    product = get_object_or_404(
        Product,
        slug=slug,
        is_active=True,
        is_deleted=False,
    )

    # Get all variants grouped by colors
    variants_by_color = {}
    for variant in product.variants.all():
        color = variant.color
        if color not in variants_by_color:
            variants_by_color[color] = {
                'color' : color,
                'variants' : [],
                'images' : product.images.filter(color=color).order_by('display_order'),
            }
        variants_by_color[color]['variants'].append(variant)


    context = {
        'product' : product,
        'variants_by_color' : list(variants_by_color.values()),
        'defualt_images' : product.images.all().order_by('display_order')
    }

    return render(
        request,
        'products/product_detail.html',
        context
    )
