from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import transaction
from django.http import FileResponse, Http404
from .invoice import generate_invoice_pdf
from .models import Order, OrderStatusHistory, ReturnRequest, ReturnRequestItem
from .dashboard_forms import OrderStatusUpdateForm
from django.utils import timezone
from .utils import send_cancellation_decision_email,send_order_confirmation_email, send_return_decision_email
from .services import fulfill_exchange_request
from products.models import ProductVariant



def get_order_context(request, per_page=15):
    qs = Order.objects.all().order_by("-created_at")

    search = request.GET.get("search", "").strip()
    if search:
        qs = qs.filter(
            Q(order_number__icontains=search) |
            Q(full_name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )

    order_status = request.GET.get("order_status")
    if order_status:
        qs = qs.filter(order_status=order_status)

    payment_status = request.GET.get("payment_status")
    if payment_status:
        qs = qs.filter(payment_status=payment_status)

    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")
    if date_from:
        qs = qs.filter(created_at__date__gte=date_from)
    if date_to:
        qs = qs.filter(created_at__date__lte=date_to)

    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(request.GET.get("page"))

    return {
        "orders": page_obj,
        "page_obj": page_obj,
        "paginator": paginator,
        "search": search,
        "order_status": order_status,
        "payment_status": payment_status,
        "date_from": date_from or "",
        "date_to": date_to or "",
        "order_status_choices": Order.OrderStatus.choices,
        "payment_status_choices": Order.PaymentStatus.choices,
    }


@login_required
@user_passes_test(lambda u: u.is_staff)
def order_list(request):
    context = get_order_context(request)
    context["page_title"] = "Orders"
    return render(request, "dashboard/orders/list.html", context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def order_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)

    if request.method == "POST":
        action = request.POST.get("action")
        # ---------- Cancellation approve / reject ----------
        if action in ("approve_cancellation", "reject_cancellation"):
            with transaction.atomic():
                if action == "approve_cancellation":
                    order.order_status = Order.OrderStatus.CANCELLED
                    note = "Cancellation approved by admin"
                    approved = True
                else:
                    order.order_status = order.get_pre_cancellation_status()
                    note = "Cancellation request rejected by admin."
                    approved = False

                order.save(update_fields=["order_status", "updated_at"])
                OrderStatusHistory.objects.create(
                    order=order, status=order.order_status, note=note,
                )

            send_cancellation_decision_email(order, approved=approved)
            messages.success(request, note)
            return redirect("orders_dashboard:order_detail", order_number=order.order_number)
        
        # ---------- Return / Exchange approve / reject ----------
        if action in ("approve_return", "reject_return"):
            return_id = request.POST.get("return_id")
            return_req = get_object_or_404(
                ReturnRequest,
                id=return_id,
                order=order,
                status=ReturnRequest.Status.PENDING,
            )

            admin_note = request.POST.get("admin_note", "").strip()

            with transaction.atomic():
                if action == "approve_return":
                    return_req.status = ReturnRequest.Status.APPROVED
                    note = "Return/Exchange approved by admin"
                    approved = True
                else:
                    return_req.status = ReturnRequest.Status.REJECTED
                    note = "Return/Exchange rejected by admin"
                    approved = False

                return_req.admin_note = admin_note
                return_req.save(update_fields=["status", "admin_note", "updated_at"])

            send_return_decision_email(return_req, approved=approved)
            messages.success(request, note)
            return redirect("orders_dashboard:order_detail", order_number=order.order_number)
            
        form = OrderStatusUpdateForm(request.POST)
        if form.is_valid():
            new_status = form.cleaned_data["order_status"]
            note = form.cleaned_data["note"]

            if new_status != order.order_status:
                with transaction.atomic():
                    old_status = order.order_status
                    order.order_status = new_status

                    # CRITICAL: set delivered_at when moving to Delivered
                    update_fields = ["order_status", "updated_at"]
                    if new_status == Order.OrderStatus.DELIVERED and not order.delivered_at:
                        order.delivered_at = timezone.now()
                        update_fields.append("delivered_at")

                    order.save(update_fields=update_fields)

                    OrderStatusHistory.objects.create(
                        order=order,
                        status=new_status,
                        note= note or f"Status changed from {old_status} to {new_status} by admin."
                    )

                try:
                    from .utils import send_order_status_update_email
                    send_order_status_update_email(order, old_status=old_status)
                except Exception as e:
                    print(f"Status update email failed: {e}")
                
                messages.success(
                    request,
                    f"Order status updated to {order.get_order_status_display()}."
                )
            else:
                messages.info(request, "Status unchanged — no update made.")
            return redirect("orders_dashboard:order_detail", order_number=order.order_number)
    else:
        form = OrderStatusUpdateForm(initial={"order_status": order.order_status})

    items = order.items.select_related("variant__product", "variant__color", "variant__size")
    history = order.status_history.all()
    return_requests = order.return_requests.prefetch_related("items__order_item").all()

    return render(request, "dashboard/orders/detail.html", {
        "order": order,
        "items": items,
        "history": history,
        "form": form,
        "return_requests": return_requests,
        "page_title": f"Order {order.order_number}",
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def download_invoice(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)

    # Always regenerate if missing or if the stored file is broken
    try:
        if not order.invoice or not order.invoice.storage.exists(order.invoice.name):
            pdf_file = generate_invoice_pdf(order)
            order.invoice.save(pdf_file.name, pdf_file, save=True)
    except Exception as e:
        print(f"Invoice generation failed: {e}")
        # Fallback: generate in memory and serve directly
        pdf_file = generate_invoice_pdf(order)
        return FileResponse(
            pdf_file,
            as_attachment=True,
            filename=f"Invoice_{order.order_number}.pdf",
            content_type="application/pdf",
        )

    return FileResponse(
        order.invoice.open("rb"),
        as_attachment=True,
        filename=f"Invoice_{order.order_number}.pdf",
        content_type="application/pdf",
    )

@login_required
@user_passes_test(lambda u: u.is_staff)
def fulfill_exchange(request, order_number, return_id):
    order = get_object_or_404(Order, order_number=order_number)
    return_req = get_object_or_404(
        ReturnRequest,
        id=return_id,
        order=order,
    )

    # Only allow if already approved (or still pending – your choice)
    if return_req.status not in (
        ReturnRequest.Status.APPROVED,
        ReturnRequest.Status.PENDING,   # remove if you want strict approve-first
    ):
        messages.error(request, "This return request cannot be fulfilled.")
        return redirect("orders_dashboard:order_detail", order_number=order.order_number)

    exchange_items = return_req.items.filter(
        request_type=ReturnRequest.RequestType.EXCHANGE
    ).select_related("order_item__variant__product")

    if not exchange_items.exists():
        messages.error(request, "No exchange items found in this request.")
        return redirect("orders_dashboard:order_detail", order_number=order.order_number)

    if request.method == "POST":
        items_data = []
        errors = []

        for ritem in exchange_items:
            variant_id = request.POST.get(f"variant_{ritem.id}")
            qty_str = request.POST.get(f"qty_{ritem.id}", "1")

            if not variant_id:
                errors.append(f"Please select a new variant for {ritem.order_item.product_name}")
                continue

            try:
                new_variant = ProductVariant.objects.get(id=variant_id)
                new_qty = int(qty_str)
                if new_qty < 1:
                    raise ValueError("Quantity must be ≥ 1")
            except (ProductVariant.DoesNotExist, ValueError) as e:
                errors.append(str(e))
                continue

            items_data.append({
                "return_item_id": ritem.id,
                "new_variant": new_variant,
                "new_quantity": new_qty,
            })

        if errors:
            for e in errors:
                messages.error(request, e)
            return redirect("orders_dashboard:order_detail", order_number=order.order_number)

        try:
            price_diff = fulfill_exchange_request(return_req, items_data)
            msg = "Exchange fulfilled successfully."
            if price_diff > 0:
                msg += f" Customer owes ₹{price_diff} extra."
            elif price_diff < 0:
                msg += f" Refund due to customer: ₹{abs(price_diff)}."
            messages.success(request, msg)
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f"Failed to fulfill exchange: {e}")

        return redirect("orders_dashboard:order_detail", order_number=order.order_number)

    # GET → just redirect back (modal is on the detail page)
    return redirect("orders_dashboard:order_detail", order_number=order.order_number)