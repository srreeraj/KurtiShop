# orders/invoice.py
from io import BytesIO
from pathlib import Path

from django.core.files.base import ContentFile
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Image
)
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER


# -------------------------------------------------
# Register Noto Sans (supports ₹ perfectly)
# -------------------------------------------------
FONT_DIR = Path(settings.BASE_DIR) / "static" / "fonts"

pdfmetrics.registerFont(TTFont("NotoSans", str(FONT_DIR / "NotoSans-Regular.ttf")))
pdfmetrics.registerFont(TTFont("NotoSans-Bold", str(FONT_DIR / "NotoSans-Bold.ttf")))


def generate_invoice_pdf(order):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=16*mm,
        leftMargin=16*mm,
        topMargin=12*mm,
        bottomMargin=12*mm,
    )

    styles = getSampleStyleSheet()

    # ---------- Custom styles (using Noto Sans) ----------
    styles.add(ParagraphStyle(
        name="Brand",
        fontName="NotoSans-Bold",
        fontSize=16,
        textColor=colors.HexColor("#111827"),
        spaceAfter=1,
        leading=18,
    ))
    styles.add(ParagraphStyle(
        name="BrandSub",
        fontName="NotoSans",
        fontSize=8,
        textColor=colors.HexColor("#6b7280"),
        leading=11,
        spaceAfter=1,
    ))
    styles.add(ParagraphStyle(
        name="InvoiceTitle",
        fontName="NotoSans-Bold",
        fontSize=18,
        textColor=colors.HexColor("#C1121F"),
        alignment=TA_RIGHT,
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="SectionHeader",
        fontName="NotoSans-Bold",
        fontSize=8,
        textColor=colors.HexColor("#9ca3af"),
        spaceBefore=4,
        spaceAfter=3,
    ))
    styles.add(ParagraphStyle(
        name="NormalText",
        fontName="NotoSans",
        fontSize=9.5,
        textColor=colors.HexColor("#374151"),
        leading=13,
    ))
    styles.add(ParagraphStyle(
        name="BoldText",
        fontName="NotoSans-Bold",
        fontSize=9.5,
        textColor=colors.HexColor("#111827"),
        leading=12,
    ))
    styles.add(ParagraphStyle(
        name="Footer",
        fontName="NotoSans",
        fontSize=8,
        textColor=colors.HexColor("#6b7280"),
        alignment=TA_CENTER,
        leading=11,
    ))
    styles.add(ParagraphStyle(
        name="ThankYou",
        fontName="NotoSans-Bold",
        fontSize=10,
        textColor=colors.HexColor("#C1121F"),
        alignment=TA_CENTER,
        spaceBefore=4,
        spaceAfter=2,
    ))
    styles.add(ParagraphStyle(
        name="MetaRight",
        fontName="NotoSans",
        fontSize=9,
        textColor=colors.HexColor("#374151"),
        alignment=TA_RIGHT,
        leading=13,
    ))

    story = []

    # ========== COMPANY DATA ==========
    company_name = getattr(settings, "COMPANY_NAME", "Kyla Fashions")
    company_address = getattr(settings, "COMPANY_ADDRESS", "").replace("\n", "<br/>")
    company_phone = getattr(settings, "COMPANY_PHONE", "")
    company_email = getattr(settings, "COMPANY_EMAIL", "")
    company_gstin = getattr(settings, "COMPANY_GSTIN", "")

    # ========== HEADER ==========
    left_content = []

    # Logo
    logo_path = getattr(settings, "COMPANY_LOGO_PATH", None)
    if logo_path:
        logo_path = Path(logo_path)
        if logo_path.exists():
            try:
                logo = Image(str(logo_path), width=48*mm, height=19*mm)
                logo.hAlign = "LEFT"
                left_content.append(logo)
                left_content.append(Spacer(1, 2*mm))
            except Exception as e:
                print(f"Logo load failed: {e}")

    left_content.append(Paragraph(company_name, styles["Brand"]))

    address_parts = []
    if company_address:
        address_parts.append(company_address)
    if company_phone:
        address_parts.append(company_phone)
    if company_email:
        address_parts.append(company_email)
    if company_gstin:
        address_parts.append(f"GSTIN: {company_gstin}")

    if address_parts:
        left_content.append(Paragraph("<br/>".join(address_parts), styles["BrandSub"]))

    right_content = [
        Paragraph("INVOICE", styles["InvoiceTitle"]),
        Paragraph(
            f"<b>Invoice No:</b>  #{order.order_number}<br/>"
            f"<b>Date:</b>  {order.created_at.strftime('%d %b %Y')}<br/>"
            f"<b>Status:</b>  {order.get_order_status_display()}",
            styles["MetaRight"]
        ),
    ]

    header_table = Table(
        [[left_content, right_content]],
        colWidths=[110*mm, 64*mm]
    )
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(header_table)

    # Brand red line
    story.append(HRFlowable(
        width="100%",
        thickness=2.2,
        color=colors.HexColor("#C1121F"),
        spaceBefore=7,
        spaceAfter=11
    ))

    # ========== BILL TO / SHIP TO ==========
    bill_to = (
        f"<b>{order.full_name}</b><br/>"
        f"{order.email}<br/>"
        f"{order.phone}"
    )
    ship_to = (
        f"<b>{order.full_name}</b><br/>"
        f"{order.address_line_1}"
        f"{', ' + order.address_line_2 if order.address_line_2 else ''}<br/>"
        f"{order.city}, {order.state} – {order.postal_code}"
    )

    address_data = [
        [
            Paragraph("BILL TO", styles["SectionHeader"]),
            Paragraph("SHIP TO", styles["SectionHeader"]),
        ],
        [
            Paragraph(bill_to, styles["NormalText"]),
            Paragraph(ship_to, styles["NormalText"]),
        ],
    ]

    address_table = Table(address_data, colWidths=[87*mm, 87*mm])
    address_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#e5e7eb")),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(address_table)
    story.append(Spacer(1, 12))

    # ========== ITEMS TABLE ==========
    items = order.items.select_related(
        "variant__product", "variant__color", "variant__size"
    ).all()

    table_data = [["Item", "Color / Size", "Qty", "Unit Price", "Total"]]

    for item in items:
        unit_price = getattr(item, "unit_price", None)
        if unit_price is None:
            unit_price = item.total_price / item.quantity if item.quantity else 0

        color = getattr(item, "color", "") or ""
        size = getattr(item, "size", "") or ""

        table_data.append([
            Paragraph(str(item.product_name), styles["BoldText"]),
            f"{color} / {size}" if color or size else "—",
            str(item.quantity),
            f"₹{unit_price:,.2f}",
            f"₹{item.total_price:,.2f}",
        ])

    items_table = Table(
        table_data,
        colWidths=[72*mm, 38*mm, 16*mm, 28*mm, 28*mm]
    )
    items_table.setStyle(TableStyle([
        # Header
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "NotoSans-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("ALIGN", (2, 0), (-1, 0), "CENTER"),
        ("ALIGN", (3, 0), (-1, 0), "RIGHT"),
        ("ALIGN", (4, 0), (-1, 0), "RIGHT"),

        # Body
        ("FONTNAME", (0, 1), (-1, -1), "NotoSans"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("ALIGN", (2, 1), (2, -1), "CENTER"),
        ("ALIGN", (3, 1), (-1, -1), "RIGHT"),
        ("ALIGN", (4, 1), (-1, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 6.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),

        ("LINEBELOW", (0, 0), (-1, 0), 0, colors.HexColor("#111827")),
        ("LINEBELOW", (0, 1), (-1, -2), 0.4, colors.HexColor("#e5e7eb")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#f9fafb")),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 10))

    # ========== TOTALS ==========
    totals_data = []
    totals_data.append(["Subtotal", f"₹{order.subtotal:,.2f}"])

    if getattr(order, "total_discount", 0) and order.total_discount > 0:
        totals_data.append(["Discount", f"– ₹{order.total_discount:,.2f}"])

    if getattr(order, "shipping_charge", 0) and order.shipping_charge > 0:
        totals_data.append(["Shipping", f"₹{order.shipping_charge:,.2f}"])

    if getattr(order, "tax", 0) and order.tax > 0:
        totals_data.append(["Tax", f"₹{order.tax:,.2f}"])

    totals_data.append(["Grand Total", f"₹{order.grand_total:,.2f}"])

    totals_table = Table(totals_data, colWidths=[38*mm, 32*mm])
    totals_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -2), "NotoSans"),
        ("FONTSIZE", (0, 0), (-1, -2), 9.5),
        ("FONTNAME", (0, -1), (-1, -1), "NotoSans-Bold"),
        ("FONTSIZE", (0, -1), (-1, -1), 11),
        ("TEXTCOLOR", (0, -1), (-1, -1), colors.HexColor("#C1121F")),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("LINEABOVE", (0, -1), (-1, -1), 1.4, colors.HexColor("#111827")),
        ("TOPPADDING", (0, -1), (-1, -1), 7),
    ]))

    outer = Table([[totals_table]], colWidths=[174*mm])
    outer.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
    ]))
    story.append(outer)
    story.append(Spacer(1, 12))

    # ========== PAYMENT INFO ==========
    payment_method = (
        order.get_payment_method_display()
        if hasattr(order, "get_payment_method_display")
        else "Online"
    )
    payment_status = (
        order.get_payment_status_display()
        if hasattr(order, "get_payment_status_display")
        else str(order.payment_status)
    )

    payment_text = (
        f"<b>Payment Method:</b>  {payment_method}<br/>"
        f"<b>Payment Status:</b>  {payment_status}"
    )
    if getattr(order, "razorpay_payment_id", None):
        payment_text += f"<br/><b>Payment ID:</b>  {order.razorpay_payment_id}"

    story.append(Paragraph("PAYMENT DETAILS", styles["SectionHeader"]))
    story.append(Paragraph(payment_text, styles["NormalText"]))
    story.append(Spacer(1, 8))

    # ========== FOOTER ==========
    story.append(HRFlowable(
        width="100%",
        thickness=0.6,
        color=colors.HexColor("#e5e7eb"),
        spaceBefore=6,
        spaceAfter=7
    ))
    story.append(Paragraph(f"Thank you for choosing {company_name}", styles["ThankYou"]))
    story.append(Paragraph(
        f"{company_name}  ·  {company_email}  ·  {company_phone}",
        styles["Footer"]
    ))

    doc.build(story)
    buffer.seek(0)

    filename = f"Invoice_{order.order_number}.pdf"
    return ContentFile(buffer.read(), name=filename)