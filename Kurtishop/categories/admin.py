from django.contrib import admin
from .models import Category

# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'parent',
        'is_active',
        'is_featured',
        'created_at',
    )

    list_filter = (
        'parent',
        'is_active',
        'is_featured',
    )
    list_editable = ('is_featured',)
    search_fields = (
        'name',
        'description',
    )

    prepopulated_fields = {
        'slug' : ('name',)
    }

    ordering = ("name",)