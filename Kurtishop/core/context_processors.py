# core/context_processors.py

def breadcrumbs(request):
    """Automatically generates breadcrumbs for all pages"""
    breadcrumbs_list = [{'name': 'Home', 'url': '/'}]
    
    path = request.path.strip('/').split('/')
    
    # Shop / Product Listing
    if any(x in request.path for x in ['shop', 'products', 'product_list']):
        breadcrumbs_list.append({'name': 'Shop', 'url': '/shop/'})
        
        # If category filter is active
        category_slug = request.GET.get('category')
        if category_slug:
            from products.models import Category
            category = Category.objects.filter(slug=category_slug).first()
            if category:
                breadcrumbs_list.append({
                    'name': category.name, 
                    'url': f'/shop/?category={category_slug}'
                })

    # Product Detail Page
    elif 'product' in request.path and len(path) > 1:
        breadcrumbs_list.append({'name': 'Shop', 'url': '/shop/'})
        
        # We'll set the product name in the view itself (better UX)
        product = getattr(request, 'current_product', None)
        if product:
            breadcrumbs_list.append({
                'name': product.name,
                'url': request.path
            })
        else:
            breadcrumbs_list.append({'name': 'Product', 'url': request.path})

    # Checkout
    elif 'checkout' in request.path:
        breadcrumbs_list.append({'name': 'Cart', 'url': '/cart/'})
        breadcrumbs_list.append({'name': 'Checkout', 'url': request.path})

    # Fallback for other pages
    else:
        for segment in path:
            if segment and segment not in ['products', 'orders']:
                name = segment.replace('-', ' ').replace('_', ' ').title()
                breadcrumbs_list.append({'name': name, 'url': f'/{segment}/'})

    return {
        'breadcrumbs': breadcrumbs_list,
    }