from django import forms
from .models import Occasion, Color, Size

INPUT = "block w-full rounded-2xl border-gray-200 focus:border-red-500 focus:ring-red-500 py-3 px-4"
FILE = "block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-2xl file:border-0 file:text-sm file:font-medium file:bg-red-50 file:text-red-700 hover:file:bg-red-100"
CHECKBOX = "w-5 h-5 rounded border-gray-300 text-red-600 focus:ring-red-500"


class OccasionForm(forms.ModelForm):
    class Meta:
        model = Occasion
        fields = ["name", "image", "is_featured"]
        widgets = {
            "name": forms.TextInput(attrs={"class": INPUT, "placeholder": "e.g. Wedding, Party, Casual"}),
            "image": forms.ClearableFileInput(attrs={"class": FILE}),
            "is_featured": forms.CheckboxInput(attrs={"class": CHECKBOX}),
        }


class ColorForm(forms.ModelForm):
    class Meta:
        model = Color
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={"class": INPUT, "placeholder": "e.g. Teal, Maroon, Mustard"}),
        }


class SizeForm(forms.ModelForm):
    class Meta:
        model = Size
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={"class": INPUT, "placeholder": "e.g. S, M, L, XL, Free Size"}),
        }