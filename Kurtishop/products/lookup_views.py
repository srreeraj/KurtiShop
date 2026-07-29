from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Occasion, Color, Size
from .lookup_forms import OccasionForm, ColorForm, SizeForm


staff_required = user_passes_test(lambda u: u.is_staff)


# ==================== OCCASION ====================

@login_required
@staff_required
def occasion_list(request):
    qs = Occasion.objects.all().order_by("name")
    search = request.GET.get("search", "").strip()
    if search:
        qs = qs.filter(name__icontains=search)

    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "dashboard/lookups/occasion_list.html", {
        "page_title": "Occasions",
        "occasions": page_obj,
        "page_obj": page_obj,
        "search": search,
    })


@login_required
@staff_required
def occasion_create(request):
    if request.method == "POST":
        form = OccasionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Occasion created successfully!")
            return redirect("lookups:occasion_list")
    else:
        form = OccasionForm()

    return render(request, "dashboard/lookups/occasion_form.html", {
        "form": form,
        "page_title": "Add Occasion",
    })


@login_required
@staff_required
def occasion_edit(request, pk):
    occasion = get_object_or_404(Occasion, pk=pk)
    if request.method == "POST":
        form = OccasionForm(request.POST, request.FILES, instance=occasion)
        if form.is_valid():
            form.save()
            messages.success(request, "Occasion updated successfully!")
            return redirect("lookups:occasion_list")
    else:
        form = OccasionForm(instance=occasion)

    return render(request, "dashboard/lookups/occasion_form.html", {
        "form": form,
        "occasion": occasion,
        "page_title": f"Edit {occasion.name}",
    })


@login_required
@staff_required
def occasion_delete(request, pk):
    occasion = get_object_or_404(Occasion, pk=pk)
    occasion.delete()
    messages.success(request, "Occasion deleted successfully!")
    return redirect("lookups:occasion_list")


# ==================== COLOR ====================

@login_required
@staff_required
def color_list(request):
    qs = Color.objects.all().order_by("name")
    search = request.GET.get("search", "").strip()
    if search:
        qs = qs.filter(name__icontains=search)

    paginator = Paginator(qs, 30)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "dashboard/lookups/color_list.html", {
        "page_title": "Colors",
        "colors": page_obj,
        "page_obj": page_obj,
        "search": search,
    })


@login_required
@staff_required
def color_create(request):
    if request.method == "POST":
        form = ColorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Color created successfully!")
            return redirect("lookups:color_list")
    else:
        form = ColorForm()

    return render(request, "dashboard/lookups/color_form.html", {
        "form": form,
        "page_title": "Add Color",
    })


@login_required
@staff_required
def color_edit(request, pk):
    color = get_object_or_404(Color, pk=pk)
    if request.method == "POST":
        form = ColorForm(request.POST, instance=color)
        if form.is_valid():
            form.save()
            messages.success(request, "Color updated successfully!")
            return redirect("lookups:color_list")
    else:
        form = ColorForm(instance=color)

    return render(request, "dashboard/lookups/color_form.html", {
        "form": form,
        "color": color,
        "page_title": f"Edit {color.name}",
    })


@login_required
@staff_required
def color_delete(request, pk):
    color = get_object_or_404(Color, pk=pk)
    color.delete()
    messages.success(request, "Color deleted successfully!")
    return redirect("lookups:color_list")


# ==================== SIZE ====================

@login_required
@staff_required
def size_list(request):
    qs = Size.objects.all().order_by("name")
    search = request.GET.get("search", "").strip()
    if search:
        qs = qs.filter(name__icontains=search)

    paginator = Paginator(qs, 30)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "dashboard/lookups/size_list.html", {
        "page_title": "Sizes",
        "sizes": page_obj,
        "page_obj": page_obj,
        "search": search,
    })


@login_required
@staff_required
def size_create(request):
    if request.method == "POST":
        form = SizeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Size created successfully!")
            return redirect("lookups:size_list")
    else:
        form = SizeForm()

    return render(request, "dashboard/lookups/size_form.html", {
        "form": form,
        "page_title": "Add Size",
    })


@login_required
@staff_required
def size_edit(request, pk):
    size = get_object_or_404(Size, pk=pk)
    if request.method == "POST":
        form = SizeForm(request.POST, instance=size)
        if form.is_valid():
            form.save()
            messages.success(request, "Size updated successfully!")
            return redirect("lookups:size_list")
    else:
        form = SizeForm(instance=size)

    return render(request, "dashboard/lookups/size_form.html", {
        "form": form,
        "size": size,
        "page_title": f"Edit {size.name}",
    })


@login_required
@staff_required
def size_delete(request, pk):
    size = get_object_or_404(Size, pk=pk)
    size.delete()
    messages.success(request, "Size deleted successfully!")
    return redirect("lookups:size_list")