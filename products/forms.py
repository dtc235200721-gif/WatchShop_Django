from django import forms
from django.contrib.auth.models import User

class UserUpdateForm(forms.ModelForm):
    # Thêm class CSS của Bootstrap cho đẹp giống các form khác của bạn
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']