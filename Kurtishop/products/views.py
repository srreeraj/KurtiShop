from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q, Min
from .models import Product, ProductVariant,Category, Color, Size, Sleeve, Neck, Occasion, Pattern

# Create your views here.

def product_list(request):
    # Based on queryset - Get variants instead of products
    variants = ProductVariant.objects.filter(
        product__is_active = True,
        product__is_deleted = False,
        is_active = True,
        is_deleted = False,
        stock__gt = 0, # only show variants that are in stock
    ).select_related(
        'product', 'product__category','color','size'
    ).prefetch_related(
        'product__images'
    ).order_by('product__name', 'color__name')

    # Category filter
    category_slug = request.GET.get('category')
    if category_slug:
        variants = variants.filter(product__category__slug=category_slug)

    # Price filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        variants = variants.filter(price__gte=min_price)
    if max_price:
        variants = variants.filter(price__lte=max_price)

    # Color filter
    color_id = request.GET.get('color')
    if color_id:
        variants = variants.filter(color_id=color_id)
    
    # Size filter
    size_id = request.GET.get('size')
    if size_id:
        variants = variants.filter(size_id=size_id)

    # Sleeve filter
    sleeve_id = request.GET.get('sleeve')
    if sleeve_id:
        variants = variants.filter(sleeve_id=sleeve_id)

    # Neck filter
    neck_id = request.GET.get('neck')
    if neck_id:
        variants = variants.filter(neck_id=neck_id)

    # Occasion filter
    occasion_slug = request.GET.get('occasion')
    if occasion_id:
        variants = variants.filter(product__occasion__name__iexact=occasion_slug)

    # Pattern filter
    pattern_id = request.GET.get('pattern')
    if pattern_id:
        variants = variants.filter(pattern_id=pattern_id)

    # New Arrivals
    if request.GET.get('new_arrivals') == 'true':
        variants = variants.filter(product__is_new_arrival=True)

    # Sale / Discounted products
    if request.GET.get('sale') == 'true':
        variants = variants.filter(discount_percentage__gt=0)
    
    # Remove duplicate color variants per product (keep only one per color)
    seen = {}
    unique_variants = []
    for v in variants:
        key = (v.product_id, v.color_id)
        if key not in seen:
            seen[key] = True
            unique_variants.append(v)
    
    # For each variant, get the best price and primary image
    for variant in unique_variants:
        # Get all images for this color
        color_images = variant.product.images.filter(color=variant.color).order_by('display_order')
        variant.color_images = color_images[:4]
        variant.primary_image = color_images.first() if color_images.exists() else None

        # Get all in-stock variant for the product + color
        color_variants = list(ProductVariant.objects.filter(
            product=variant.product,
            color=variant.color,
            stock__gt=0
        ))

        # Pick the variant with the lowest DISCOUNTED price
        # (not just lowest raw price) so original + discounted stay in sync
        best_variant = min(color_variants, key=lambda v: v.discounted_price) if color_variants else variant

        variant.display_price = best_variant.discounted_price
        variant.display_original_price = best_variant.price
        variant.display_discount_percentage = best_variant.discount_percentage

    # Pagination

    # from django.core.paginator import Paginator
    # paginator = Paginator(products, 12) #12 products per page
    # page_number = request.GET.get('page')
    # products_page = paginator.get_page(page_number)

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
        'products': unique_variants,
        'categories' : categories,
        'colors' : colors,
        'sizes' : sizes,
        'sleeves' : sleeves,
        'necks' : necks,
        'occasions' : occasions,
        'patterns' : patterns,

        # For active filter highlighting
        'active_category' : Category.objects.filter(slug=category_slug).first() if category_slug else None,
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

    preselected_color_id = request.GET.get('color')
    # Get all variants by colors - Convert to JSON serializable format

    variants_by_color = []
    for variant in product.variants.all().select_related('color', 'size'):
        color = variant.color

        # Check if color next already exists in list
        color_entry = next((item for item in variants_by_color if item['color']['id'] == color.id), None)

        if not color_entry:
            color_entry = {
                'color' : {
                    'id' : color.id,
                    'name' : color.name,
                },
                'variants' : [],
                'images' : [],
            }
            variants_by_color.append(color_entry)

        # Add variant
        color_entry['variants'].append({
            'id' : variant.id,
            'size' : {
                'id' : variant.size.id,
                'name' : variant.size.name,
            },
            'stock' : variant.stock,
            'price' : float(variant.price),
            'discounted_price' : float(variant.discounted_price),
        })

    # Add images for each color
    for color_entry in variants_by_color:
        color_id = color_entry['color']['id']
        images = product.images.filter(color_id=color_id).order_by('display_order')
        color_entry['images'] = []
        
        color_entry['images'] = [
            {
                'image': {'url': img.image.url},
                'alt_text': img.alt_text or f"{product.name} - {color_entry['color']['name']}"
            }
            for img in images
        ]
        
    print("Preselected color from URL:", preselected_color_id)  # in console

    context = {
        'product' : product,
        'variants_by_color' : variants_by_color,
        'default_images' : product.images.all().order_by('display_order'),
        'preselected_color_id' : preselected_color_id,
    }

    return render(
        request,
        'products/product_detail.html',
        context
    )
