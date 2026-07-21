from django import forms
from .models import Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'parent', 'image', 'description', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'rounded-2xl'}),
            'parent': forms.Select(attrs={'class': 'rounded-2xl'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Prevent selecting self as parent + show hierarchy
        if self.instance.pk:
            self.fields['parent'].queryset = Category.objects.filter(
                is_deleted=False
            ).exclude(pk=self.instance.pk)
        else:
            self.fields['parent'].queryset = Category.objects.filter(is_deleted=False)