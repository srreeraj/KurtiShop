from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class' : 'w-full px-6 py-4 rounded-2xl border border-gray-200 focus:border-red-600 focus:ring-0 transition-all',
            'placeholder' : 'Full Name...'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-6 py-4 rounded-2xl border border-gray-200 focus:border-red-600 focus:ring-0 transition-all',
            'placeholder': 'your@email.com'
        })
    )
    phone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-6 py-4 rounded-2xl border border-gray-200 focus:border-red-600 focus:ring-0 transition-all',
            'placeholder': '+91 98765 43210'
        })
    )
    subject = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-6 py-4 rounded-2xl border border-gray-200 focus:border-red-600 focus:ring-0 transition-all',
            'placeholder': 'Subject'
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-6 py-4 rounded-3xl border border-gray-200 focus:border-red-600 focus:ring-0 transition-all h-40 resize-y',
            'placeholder': 'How can we help you today?'
        })
    )