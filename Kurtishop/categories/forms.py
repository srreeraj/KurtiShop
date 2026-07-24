from django import forms
from .models import Category


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "parent", "image", "description", "is_active"]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "block w-full rounded-2xl border-gray-200 focus:border-red-500 focus:ring-red-500 py-3 px-4"
                }
            ),

            "parent": forms.Select(
                attrs={
                    "class": "block w-full rounded-2xl border-gray-200 focus:border-red-500 focus:ring-red-500 py-3 px-4"
                }
            ),

            "image": forms.ClearableFileInput(
                attrs={
                    "class": "block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-2xl file:border-0 file:text-sm file:font-medium file:bg-red-50 file:text-red-700 hover:file:bg-red-100"
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "block w-full rounded-2xl border-gray-200 focus:border-red-500 focus:ring-red-500 py-3 px-4"
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields["parent"].queryset = Category.objects.filter(
                is_deleted=False
            ).exclude(pk=self.instance.pk)
        else:
            self.fields["parent"].queryset = Category.objects.filter(
                is_deleted=False
            )

        self.fields["parent"].empty_label = "— Root Category —"

    def clean_name(self):
        """Prevent duplicate names among active (non-deleted) categories"""
        name = self.cleaned_data.get('name')
        if not name:
            return name

        qs = Category.objects.filter(name=name, is_deleted=False)

        # Allow updating the same category
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError("A category with this name already exists.")

        return name