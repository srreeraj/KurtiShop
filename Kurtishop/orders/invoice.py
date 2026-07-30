# orders/invoice.py
from io import BytesIO
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from django.conf import settings
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

def generate_invoice_pdf(order):
    """
    Generates a professional PDF invoice and returns a ContentFile
    ready to be saved on order.invoice
    """
    context = {
        "order": order,
        "items": order.items.select_related("variant__product", "variant__color", "variant__size").all(),
        "company": {
            "name": getattr(settings, "COMPANY_NAME", "Your Store Name"),
            "address": getattr(settings, "COMPANY_ADDRESS", "123 Business Street, City, State - 000000"),
            "phone": getattr(settings, "COMPANY_PHONE", "+91 98765 43210"),
            "email": getattr(settings, "COMPANY_EMAIL", "support@yourdomain.com"),
            "gstin": getattr(settings, "COMPANY_GSTIN", ""),          # optional
            "logo_url": getattr(settings, "COMPANY_LOGO_URL", None),  # absolute URL or static path
        },
        "site_url": getattr(settings, "SITE_URL", "https://yourdomain.com"),
    }

    html_string = render_to_string("orders/invoice/invoice.html", context)

    font_config = FontConfiguration()
    html = HTML(string=html_string, base_url=settings.BASE_DIR)

    # Optional custom CSS
    css = CSS(string="""
        @page { size: A4; margin: 1.4cm 1.6cm; }
    """, font_config=font_config)

    pdf_bytes = html.write_pdf(stylesheets=[css], font_config=font_config)

    filename = f"Invoice_{order.order_number}.pdf"
    return ContentFile(pdf_bytes, name=filename)