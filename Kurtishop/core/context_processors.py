
def breadcrumbs(request):
    path = request.path.strip('/').split('/')
    breadcrumbs = [{'name': 'Home', 'url': '/'}]
    
    current_path = ''
    title = "Kurti Shop"  # Default fallback

    for segment in path:
        if not segment:
            continue
            
        current_path += f'/{segment}'
        
        # ============== CUSTOM LOGIC FOR YOUR PAGES ==============
        if segment == 'shop' or segment.startswith('products'):
            name = 'Shop'
            url = '/shop/' if segment == 'shop' else current_path
            title = 'Our Collection'
            
        elif 'product' in request.path and len(path) > 1:
            # For product detail pages
            name = "Product"  # Will be overridden by view if needed
            url = current_path
            title = "Product Detail"
            
        elif segment == 'checkout':
            name = 'Checkout'
            url = current_path
            title = 'Secure Checkout'
            
        elif segment == 'cart':
            name = 'Cart'
            url = current_path
            title = 'Your Cart'
            
        elif segment == 'orders' or 'order' in request.path:
            name = 'Orders'
            url = current_path
            title = 'Order'
            
        else:
            # Generic fallback (capitalize)
            name = segment.replace('-', ' ').replace('_', ' ').title()
            url = current_path

        breadcrumbs.append({'name': name, 'url': url})

    # Override last item with better name from context if available
    if hasattr(request, 'resolver_match') and request.resolver_match:
        view_name = request.resolver_match.view_name
        if view_name == 'product_detail':
            # We'll improve this in views
            pass

    return {
        'breadcrumbs': breadcrumbs[:-1] if len(breadcrumbs) > 1 else breadcrumbs,  # Remove duplicate last if needed
        'current_page_title': title
    }