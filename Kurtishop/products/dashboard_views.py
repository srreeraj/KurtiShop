from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Min
from django.db import transaction

from .models import Product, ProductImage, Color
from .forms import ProductForm, ProductVariantFormSet

# Auto-assign order for multi-image upload per color
VIEW_ORDER = ["front", "back", "left", "right", "three-quarter", "closeup", "detail"]


def get_product_context(request, per_page=10):
    qs = Product.objects.filter(is_deleted=False).select_related("category") \
        .annotate(min_price=Min("variants__price")).order_by("-created_at")

    search = request.GET.get("search", "").strip()
    if search:
        qs = qs.filter(
            Q(name__icontains=search) | Q(sku__icontains=search) | Q(category__name__icontains=search)
        )

    category_id = request.GET.get("category")
    if category_id:
        qs = qs.filter(category_id=category_id)

    status = request.GET.get("status")
    if status == "active":
        qs = qs.filter(is_active=True)
    elif status == "inactive":
        qs = qs.filter(is_active=False)

    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(request.GET.get("page"))

    return {"products": page_obj, "page_obj": page_obj, "paginator": paginator, "search": search}


@login_required
@user_passes_test(lambda u: u.is_staff)
def product_list(request):
    context = get_product_context(request)
    context["page_title"] = "Products"
    return render(request, "dashboard/products/list.html", context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        variant_formset = ProductVariantFormSet(request.POST, prefix="variants")

        if form.is_valid() and variant_formset.is_valid():
            with transaction.atomic():
                product = form.save()
                variant_formset.instance = product
                variant_formset.save()
                _save_new_images(request, product)
            messages.success(request, "Product created successfully!")
            return redirect("products_dashboard:product_edit", pk=product.pk)
    else:
        form = ProductForm()
        variant_formset = ProductVariantFormSet(prefix="variants")

    return render(request, "dashboard/products/form.html", {
        "form": form,
        "variant_formset": variant_formset,
        "colors": Color.objects.all(),
        "view_choices": ProductImage.ImageView.choices,
        "images_by_color": {},
        "page_title": "Add Product",
    })


@login_required
@user_passes_test(lambda u: u.is_staff)
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk, is_deleted=False)

    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        variant_formset = ProductVariantFormSet(request.POST, instance=product, prefix="variants")

        if form.is_valid() and variant_formset.is_valid():
            with transaction.atomic():
                form.save()
                variant_formset.save()
                _save_new_images(request, product)
                _delete_images(request)
            messages.success(request, "Product updated successfully!")
            return redirect("products_dashboard:product_edit", pk=product.pk)
    else:
        form = ProductForm(instance=product)
        variant_formset = ProductVariantFormSet(instance=product, prefix="variants")

    images_by_color = {}
    for img in product.images.select_related("color").order_by("color__name", "display_order"):
        images_by_color.setdefault(img.color, []).append(img)

    return render(request, "dashboard/products/form.html", {
        "form": form,
        "product": product,
        "variant_formset": variant_formset,
        "colors": Color.objects.all(),
        "view_choices": ProductImage.ImageView.choices,
        "images_by_color": images_by_color,
        "page_title": f"Edit {product.name}",
    })


@login_required
@user_passes_test(lambda u: u.is_staff)
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk, is_deleted=False)
    product.is_deleted = True
    product.is_active = False
    product.save()
    messages.success(request, "Product deleted successfully!")
    return redirect("products_dashboard:product_list")


def _save_new_images(request, product):
    """
    Each 'color block' the staff adds in the form submits:
      image_block_color   (hidden input, repeated once per block) -> color id
      image_block_files_<index>  (multiple file input for that block)
    Views (front/back/left/...) are auto-assigned in upload order.
    """
    color_ids = request.POST.getlist("image_block_color")
    for idx, color_id in enumerate(color_ids):
        if not color_id:
            continue
        files = request.FILES.getlist(f"image_block_files_{idx}")
        if not files:
            continue

        existing_views = set(
            ProductImage.objects.filter(product=product, color_id=color_id).values_list("view", flat=True)
        )
        last_order = ProductImage.objects.filter(product=product, color_id=color_id) \
            .order_by("-display_order").values_list("display_order", flat=True).first() or 0

        available = [v for v in VIEW_ORDER if v not in existing_views]

        for i, f in enumerate(files):
            view = available[i] if i < len(available) else None
            if view is None:
                break  # all 7 view slots for this color are used; edit existing images instead
            last_order += 1
            ProductImage.objects.create(
                product=product, color_id=color_id, view=view, image=f, display_order=last_order,
            )
            existing_views.add(view)


def _delete_images(request):
    delete_ids = request.POST.getlist("delete_image")
    if delete_ids:
        ProductImage.objects.filter(id__in=delete_ids).delete()