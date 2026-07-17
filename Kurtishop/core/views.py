from django.shortcuts import render
from products.models import Product
from categories.models import Category
from django.db.models import Count, Q
from .forms import ContactForm
from django.contrib import messages
from django.core.mail import send_mail

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
            except:
                messages.error(request, "Something went wrong. Please try again later.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ContactForm()

    context = {
        'form' = form,
        'title' = "Contact Us"
    }

    return render(request, 'core/contact.html', context)