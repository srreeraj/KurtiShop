# orders/invoice.py
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER


def generate_invoice_pdf(order):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18*mm,
        leftMargin=18*mm,
        topMargin=15*mm,
        bottomMargin=15*mm,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    styles.add(ParagraphStyle(
        name='Brand',
        fontName='Helvetica-Bold',
        fontSize=22,
        textColor=colors.HexColor('#111827'),
        spaceAfter=2,
    ))
    styles.add(ParagraphStyle(
        name='BrandSub',
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.HexColor('#6b7280'),
        spaceAfter=12,
    ))
    styles.add(ParagraphStyle(
        name='InvoiceTitle',
        fontName='Helvetica-Bold',
        fontSize=16,
        textColor=colors.HexColor('#C1121F'),
        alignment=TA_RIGHT,
    ))
    styles.add(ParagraphStyle(
        name='SectionHeader',
        fontName='Helvetica-Bold',
        fontSize=9,
        textColor=colors.HexColor('#9ca3af'),
        spaceBefore=8,
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name='NormalText',
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#374151'),
        leading=14,
    ))
    styles.add(ParagraphStyle(
        name='BoldText',
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=colors.HexColor('#111827'),
    ))
    styles.add(ParagraphStyle(
        name='Footer',
        fontName='Helvetica',
        fontSize=8,
        textColor=colors.HexColor('#6b7280'),
        alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name='ThankYou',
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=colors.HexColor('#C1121F'),
        alignment=TA_CENTER,
        spaceBefore=6,
    ))

    story = []

    # ========== HEADER ==========
    header_data = [
        [
            Paragraph("Liara", styles['Brand']),
            Paragraph("INVOICE", styles['InvoiceTitle']),
        ],
        [
            Paragraph("Fashion & Lifestyle", styles['BrandSub']),
            Paragraph(
                f"<b>Invoice No:</b> #{order.order_number}<br/>"
                f"<b>Date:</b> {order.created_at.strftime('%d %b %Y')}<br/>"
                f"<b>Status:</b> {order.get_order_status_display()}",
                styles['NormalText']
            ),
        ],
    ]

    header_table = Table(header_data, colWidths=[100*mm, 70*mm])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ]))
    story.append(header_table)

    # Red line
    story.append(HRFlowable(
        width="100%", thickness=2,
        color=colors.HexColor('#C1121F'),
        spaceBefore=4, spaceAfter=12
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
            Paragraph("BILL TO", styles['SectionHeader']),
            Paragraph("SHIP TO", styles['SectionHeader']),
        ],
        [
            Paragraph(bill_to, styles['NormalText']),
            Paragraph(ship_to, styles['NormalText']),
        ],
    ]

    address_table = Table(address_data, colWidths=[85*mm, 85*mm])
    address_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f9fafb')),
        ('BOX', (0, 0), (-1, -1), 0, colors.white),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(address_table)
    story.append(Spacer(1, 14))

    # ========== ITEMS TABLE ==========
    items = order.items.select_related(
        "variant__product", "variant__color", "variant__size"
    ).all()

    table_data = [
        ["Item", "Color / Size", "Qty", "Unit Price", "Total"]
    ]

    for item in items:
        # Safe unit price
        unit_price = getattr(item, "unit_price", None)
        if unit_price is None:
            unit_price = item.total_price / item.quantity if item.quantity else 0

        color = getattr(item, "color", "") or ""
        size = getattr(item, "size", "") or ""

        table_data.append([
            Paragraph(str(item.product_name), styles['BoldText']),
            f"{color} / {size}",
            str(item.quantity),
            f"₹{unit_price:.2f}",
            f"₹{item.total_price:.2f}",
        ])

    items_table = Table(table_data, colWidths=[70*mm, 35*mm, 18*mm, 25*mm, 25*mm])
    items_table.setStyle(TableStyle([
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#111827')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('ALIGN', (2, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (3, 0), (-1, 0), 'RIGHT'),
        ('ALIGN', (4, 0), (-1, 0), 'RIGHT'),

        # Body
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (2, 1), (2, -1), 'CENTER'),
        ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),
        ('ALIGN', (4, 1), (-1, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),

        # Lines
        ('LINEBELOW', (0, 0), (-1, 0), 0, colors.HexColor('#111827')),
        ('LINEBELOW', (0, 1), (-1, -2), 0.5, colors.HexColor('#e5e7eb')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 12))

    # ========== TOTALS ==========
    totals_data = []

    totals_data.append(["Subtotal", f"₹{order.subtotal:.2f}"])

    if getattr(order, "total_discount", 0) and order.total_discount > 0:
        totals_data.append(["Discount", f"– ₹{order.total_discount:.2f}"])

    if getattr(order, "shipping_charge", 0) and order.shipping_charge > 0:
        totals_data.append(["Shipping", f"₹{order.shipping_charge:.2f}"])

    if getattr(order, "tax", 0) and order.tax > 0:
        totals_data.append(["Tax", f"₹{order.tax:.2f}"])

    totals_data.append(["Grand Total", f"₹{order.grand_total:.2f}"])

    totals_table = Table(totals_data, colWidths=[40*mm, 30*mm])
    totals_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -2), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -2), 10),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#C1121F')),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LINEABOVE', (0, -1), (-1, -1), 1.5, colors.HexColor('#111827')),
        ('TOPPADDING', (0, -1), (-1, -1), 8),
    ]))

    # Right-align the totals table
    outer = Table([[totals_table]], colWidths=[170*mm])
    outer.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
    ]))
    story.append(outer)
    story.append(Spacer(1, 16))

    # ========== PAYMENT INFO ==========
    payment_method = order.get_payment_method_display() if hasattr(order, "get_payment_method_display") else "Online"
    payment_status = order.get_payment_status_display() if hasattr(order, "get_payment_status_display") else str(order.payment_status)

    payment_text = (
        f"<b>Payment Method:</b> {payment_method}<br/>"
        f"<b>Payment Status:</b> {payment_status}"
    )
    if order.razorpay_payment_id:
        payment_text += f"<br/><b>Payment ID:</b> {order.razorpay_payment_id}"

    story.append(Paragraph("PAYMENT DETAILS", styles['SectionHeader']))
    story.append(Paragraph(payment_text, styles['NormalText']))
    story.append(Spacer(1, 10))

    # ========== FOOTER ==========
    story.append(HRFlowable(
        width="100%", thickness=0.5,
        color=colors.HexColor('#e5e7eb'),
        spaceBefore=8, spaceAfter=8
    ))
    story.append(Paragraph("Thank you for choosing Liara", styles['ThankYou']))
    story.append(Paragraph(
        "Liara · Fashion & Lifestyle<br/>"
        "support@liara.store · +91 98765 43210",
        styles['Footer']
    ))

    # Build PDF
    doc.build(story)
    buffer.seek(0)

    filename = f"Invoice_{order.order_number}.pdf"
    return ContentFile(buffer.read(), name=filename)