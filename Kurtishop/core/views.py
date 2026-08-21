from django.shortcuts import render, redirect
from products.models import Product, Occasion, ProductVariant
from categories.models import Category
from django.db.models import Count, Q
from .forms import ContactForm
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

# Create your views here.

def home(request):

    categories = Category.objects.filter(
        is_active = True,
        is_featured = True,
        is_deleted = False,
    ).annotate(
        product_count=Count('products', filter=Q(products__is_active=True, products__is_deleted=False))
    ).order_by('name')[:6]

    occasions = Occasion.objects.filter(
        is_featured = True,
    ).order_by('name')[:6]

    def get_unique_color_variants(base_qs, limit=8):
        variants = ProductVariant.objects.filter(
            product__in=base_qs,
            product__is_active=True,
            product__is_deleted=False,
            is_active=True,
            is_deleted=False,
            stock__gt=0,
        ).select_related(
            'product', 'product__category', 'product__material', 'color', 'size'
        ).prefetch_related(
            'product__images'
        ).order_by('product__name', 'color__name')

        # Keep only one variant per product + color
        seen = {}
        unique_variants = []
        for v in variants:
            key = (v.product_id, v.color_id)
            if key not in seen:
                seen[key] = True
                unique_variants.append(v)

        # Attach display prices + primary image (exact same logic as product_list)
        for variant in unique_variants:
            color_images = variant.product.images.filter(color=variant.color).order_by('display_order')
            variant.color_images = color_images[:4]
            variant.primary_image = color_images.first() if color_images.exists() else None

            color_variants = list(ProductVariant.objects.filter(
                product=variant.product,
                color=variant.color,
                stock__gt=0,
                is_active=True,
                is_deleted=False,
            ))

            best_variant = min(color_variants, key=lambda v: v.discounted_price) if color_variants else variant

            variant.display_price = best_variant.discounted_price
            variant.display_original_price = best_variant.price
            variant.display_discount_percentage = best_variant.discount_percentage

        return unique_variants[:limit]

    # ---------- New Arrivals ----------
    new_arrival_products = Product.objects.filter(
        is_new_arrival=True,
        is_active=True,
        is_deleted=False,
    )
    new_arrivals = get_unique_color_variants(new_arrival_products, limit=4)

    # ---------- Featured / Best Sellers ----------
    featured_products_qs = Product.objects.filter(
        is_featured=True,
        is_active=True,
        is_deleted=False,
    )
    featured_products = get_unique_color_variants(featured_products_qs, limit=4)

    context = {
        'categories' : categories,
        'occasions': occasions,
        'featured_products' : featured_products,
        'new_arrivals' : new_arrivals
    }
    return render(request, 'core/home.html', context)


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            # Email content
            email_subject = f"New Contact Form : {subject}"
            email_message = f"""
                                New Inquiry from {name}
                                Name : {name}
                                Email : {email}
                                Phone : {phone if phone else "Not provided"}
                                Subject : {subject}
                                Message:
                                {message}
                            """
            try:
                send_mail(
                    email_subject,
                    email_message,
                    email,
                    [settings.ADMIN_EMAIL],
                    fail_silently=False,
                )
                messages.success(request, "Thank you! Your message has been sent successfully.")
                return redirect('contact')
            except Exception as e:
                messages.error(request, "Something went wrong. Please try again later.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ContactForm()

    context = {
        'form' : form,
        'title' : "Contact Us"
    }

    return render(request, 'core/contact.html', context)

def privacy_policy(request):
    context = {
        'title' : "Privacy Policy"
    }
    return render(request, 'pages/privacy_policy.html', context)

def terms_of_service(request):
    context = {
        'title' : 'Terms of Service'
    }
    return render(request, 'pages/terms_of_service.html', context)

def sitemap(request):
    context = {
        'title' : 'Sitemap'
    }
    return render(request, 'pages/sitemap.html', context)